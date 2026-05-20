"""Validator Agent — Adversarial-CoT pre-solver gate.

Two operating modes:
  - **L2 mode (no `csp_spec` in state)**: validates the Java code directly against
    the natural-language problem description using `VALIDATOR_NL_*` prompts.
  - **L3+ mode (`csp_spec` present)**: validates against the formal Pydantic spec
    using `VALIDATOR_SYSTEM` / `VALIDATOR_HUMAN`.

When validation fails it also writes a synthetic `solver_result` so the
downstream refiner has an `error_message` to react to without depending on a
real solver run.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from src.config import get_llm, invoke_structured_with_retry
from src.state import PipelineState, CSPSpecification, ChocoModel, ValidationResult
from src.prompts.validator import (
    VALIDATOR_SYSTEM,
    VALIDATOR_HUMAN,
    VALIDATOR_NL_SYSTEM,
    VALIDATOR_NL_HUMAN,
)


def _format_variables_short(spec: CSPSpecification) -> str:
    return ", ".join(f"{v.name}[{v.domain_low}..{v.domain_high}]" for v in spec.variables)


def _format_constraints_short(spec: CSPSpecification) -> str:
    return "\n".join(f"  - {c.formal_expression} ({c.description})" for c in spec.constraints)


def _validation_to_solver_result(result: ValidationResult) -> dict:
    """Synthesize a SolverResult-shaped dict so the refiner has an error to react to."""
    msg_lines = []
    if result.issues:
        msg_lines.append("Validator issues:")
        msg_lines.extend(f"  - {i}" for i in result.issues)
    if result.suggestions:
        msg_lines.append("Suggestions:")
        msg_lines.extend(f"  - {s}" for s in result.suggestions)
    return {
        "status": "validation_error",
        "solution": {},
        "solution_text": "",
        "statistics": {},
        "monitor_traces": [],
        "error_message": "\n".join(msg_lines) or "Validator marked the model invalid.",
        "stdout": "",
        "stderr": "",
    }


def validator_node(state: PipelineState) -> dict:
    """LangGraph node: pre-solver semantic gate (Adversarial CoT)."""
    if "choco_model" not in state:
        return {
            "validation": {"is_valid": False, "issues": ["Model was skipped; nothing to validate."], "suggestions": []},
            "current_step": "validated",
            "status": "validation_skipped_no_model",
        }

    model = ChocoModel(**state["choco_model"])
    # Bigger budget — Adversarial-CoT validators emit reasoning preamble before
    # the JSON; without enough room the structured-output parser raises
    # "length limit reached". 8 k is still not always enough on stubborn
    # models, so we also catch the exception below and fail OPEN.
    llm = get_llm(max_tokens=8192)
    structured_llm = llm.with_structured_output(ValidationResult)

    if "csp_spec" in state and state["csp_spec"]:
        # L3+ path: structured CSP spec
        spec = CSPSpecification(**state["csp_spec"])
        messages = [
            SystemMessage(content=VALIDATOR_SYSTEM),
            HumanMessage(content=VALIDATOR_HUMAN.format(
                problem_name=spec.problem_name,
                variables=_format_variables_short(spec),
                constraints=_format_constraints_short(spec),
                objective=spec.objective or "None",
                java_code=model.java_code,
            )),
        ]
    else:
        # L2 path: NL problem description, Adversarial CoT
        problem = state.get("problem_description", "") or ""
        messages = [
            SystemMessage(content=VALIDATOR_NL_SYSTEM),
            HumanMessage(content=VALIDATOR_NL_HUMAN.format(
                problem_description=problem,
                java_code=model.java_code,
            )),
        ]

    # Fail-open on structured-output failure: if the LLM blows past the token
    # budget or emits unparseable text, treat the model as VALID and let the
    # solver be the next gate. Crashing here would otherwise bring down the
    # whole experiment (we saw this on qwen3-coder for 8queens / sudoku_9x9).
    try:
        result: ValidationResult = invoke_structured_with_retry(structured_llm, messages)
    except Exception as e:
        msg = str(e)[:200]
        result = ValidationResult(
            is_valid=True,
            issues=[],
            suggestions=[f"[validator-skipped] structured output failed: {msg}"],
        )

    update = {
        "validation": result.model_dump(),
        "current_step": "validated",
        "status": "valid" if result.is_valid else "validation_failed",
    }
    if not result.is_valid:
        update["solver_result"] = _validation_to_solver_result(result)
    return update

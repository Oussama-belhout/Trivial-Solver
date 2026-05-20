"""Formalizer Agent — converts natural language problems into structured CSP specifications.

Uses `method="function_calling"` for `with_structured_output` because the default
`json_schema` method is rejected by some OpenRouter upstream providers
(e.g. DeepInfra returns 405 for DeepSeek R1 Distill Llama 70B).

Falls open with a stub spec on schema-validation or upstream errors so a single
formalization failure doesn't crash the whole pipeline; the modeler then sees a
minimal spec containing the NL problem and produces best-effort Java.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from src.config import get_llm, invoke_structured_with_retry
from src.state import PipelineState, CSPSpecification
from src.prompts.formalizer import FORMALIZER_SYSTEM, FORMALIZER_HUMAN


def _stub_spec(problem_description: str) -> CSPSpecification:
    """Minimal spec used when the formalizer call fails — keeps the pipeline
    alive so the modeler still gets a chance and L3 numbers reflect end-to-end
    behavior rather than provider-side failures."""
    return CSPSpecification(
        problem_name="UnknownProblem",
        problem_description=problem_description,
        parameters={},
        variables=[],
        constraints=[],
        objective=None,
        is_optimization=False,
    )


def formalizer_node(state: PipelineState) -> dict:
    llm = get_llm(max_tokens=4096)
    structured_llm = llm.with_structured_output(CSPSpecification, method="function_calling")

    messages = [
        SystemMessage(content=FORMALIZER_SYSTEM),
        HumanMessage(content=FORMALIZER_HUMAN.format(
            problem_description=state["problem_description"]
        )),
    ]

    try:
        result: CSPSpecification = invoke_structured_with_retry(structured_llm, messages)
        status = "CSP specification created"
    except Exception as e:
        result = _stub_spec(state["problem_description"])
        status = f"formalizer_failed_open: {str(e)[:200]}"

    return {
        "csp_spec": result.model_dump(),
        "current_step": "formalized",
        "status": status,
    }

"""Refiner Agent — analyzes failures and generates fixed Choco models.

L1+ specialist. Uses Reflexion-style prompting (verbalize self-critique before
emitting the fix). Increments `iteration` so the workflow can bound the loop
with MAX_REFINEMENT_ITERATIONS.

Designed to work both standalone (L1, no formalizer in the pipeline — `csp_spec`
absent from state) and downstream (L3+ where a Formalizer agent populates
`csp_spec`). The agent never depends on `csp_spec`; if present, it is ignored
in favour of the natural-language problem description.
"""

from __future__ import annotations

import re

from langchain_core.messages import HumanMessage, SystemMessage

from src.config import get_llm, invoke_with_retry, MAX_REFINEMENT_ITERATIONS
from src.state import PipelineState, ChocoModel, SolverResult
from src.prompts.refiner import REFINER_SYSTEM, REFINER_HUMAN


# Reuse the robust extractors from the monolith — single source of truth.
from src.agents.monolith import (
    _extract_java_code,
    _ensure_package,
    _force_class_name,
    _truncate,
    _strip_think_block,
    _JAVA_ANCHOR_RE,
)


# Strip both closed and truncated/unclosed <reflection>...</reflection> blocks.
# Critical: when the LLM response gets cut off mid-reflection (token limit /
# OpenRouter clip), the unclosed `<reflection>` tag would otherwise leak into
# the .java file and break compilation on every subsequent refinement attempt.
_REFLECT_CLOSED_RE = re.compile(r"<reflection>.*?</reflection>", re.DOTALL | re.IGNORECASE)
_REFLECT_OPEN_RE = re.compile(r"<reflection>.*", re.DOTALL | re.IGNORECASE)


def _strip_reflection(text: str) -> str:
    text = _REFLECT_CLOSED_RE.sub("", text)
    text = _REFLECT_OPEN_RE.sub("", text)
    return text


def refiner_node(state: PipelineState) -> dict:
    """LangGraph node: Reflexion-style fix of a failed Choco model.

    Reads `problem_description` (NL), `choco_model` (last attempt), and
    `solver_result` (the failure that triggered this call). Does NOT require
    `csp_spec` — at L1 there is no Formalizer agent yet.
    """
    if "choco_model" not in state:
        return {
            "current_step": "refined",
            "status": "Skipped refinement (no choco_model in state)",
            "iteration": state.get("iteration", 0),
        }

    prev_model = ChocoModel(**state["choco_model"])
    class_name = prev_model.class_name
    iteration = state.get("iteration", 0) + 1
    problem_description = state.get("problem_description", "") or ""

    solver_dict = state.get("solver_result") or {}
    raw_status = solver_dict.get("status", "unknown")
    error_status = raw_status.value if hasattr(raw_status, "value") else str(raw_status)
    error_message = solver_dict.get("error_message", "") or ""

    error_history_lines = state.get("error_history", []) or []
    error_history_text = "\n".join(error_history_lines) if error_history_lines else "(none)"

    human_content = (
        REFINER_HUMAN
        .replace("{problem_description}", problem_description)
        .replace("{class_name}", class_name)
        .replace("{iteration}", str(iteration))
        .replace("{max_iterations}", str(MAX_REFINEMENT_ITERATIONS))
        .replace("{previous_java_code}", _truncate(prev_model.java_code, 4000))
        .replace("{error_status}", error_status)
        .replace("{error_message}", _truncate(error_message, 1500))
        .replace("{error_history}", _truncate(error_history_text, 1500))
    )

    messages = [
        SystemMessage(content=REFINER_SYSTEM),
        HumanMessage(content=human_content),
    ]

    response = invoke_with_retry(get_llm(temperature=0.2), messages)

    # Step 1: strip both <think> and <reflection> blocks (closed AND unclosed).
    raw = _strip_think_block(_strip_reflection(response.content))

    # Step 2: try to extract Java code. The robust extractor handles fenced
    # blocks, partial fences, and the `package`/`import`/`public class` anchor.
    candidate = _extract_java_code(raw)

    # Step 3: VALIDATE the candidate has real Java content. If the response was
    # truncated mid-reflection (no Java at all), we MUST keep the previous Java
    # — overwriting it with reflection text guarantees a compile error on the
    # next solver call AND uses up another refinement iteration.
    if _JAVA_ANCHOR_RE.search(candidate) and len(candidate) > 80:
        fixed_code = _force_class_name(_ensure_package(candidate), class_name)
        explanation = f"Refiner (Reflexion, iter {iteration})"
        status_msg = f"Refined (Reflexion-style, iter {iteration}/{MAX_REFINEMENT_ITERATIONS})"
    else:
        # Refiner produced no usable Java (truncated reflection / empty response).
        # Keep the previous Java unchanged; the iteration counter still advances
        # so the loop is bounded. Surface this in error_history.
        fixed_code = prev_model.java_code
        explanation = f"Refiner (Reflexion, iter {iteration}) — NO USABLE JAVA, kept previous"
        status_msg = f"Refined (no-op, iter {iteration}/{MAX_REFINEMENT_ITERATIONS}) — refiner output had no Java"

    refined_model = ChocoModel(
        java_code=fixed_code,
        class_name=class_name,
        explanation=explanation,
    )

    return {
        "choco_model": refined_model.model_dump(),
        "iteration": iteration,
        "current_step": "refined",
        "status": status_msg,
    }

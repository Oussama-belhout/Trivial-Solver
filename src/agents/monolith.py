"""Monolith Agent — the L0 fat agent that does ALL five behaviors itself.

At L0 a single LLM (the Monolith) handles formalization, modeling, validation,
refinement, and explanation by being invoked in three distinct **modes**:

  - `MODEL`   — combined formalize + model + (implicit) validate.
                Input: NL problem.  Output: Choco Java program.
  - `REFINE`  — read prior Java + solver/compiler error, produce fixed Java.
                Bounded by `MAX_REFINEMENT_ITERATIONS`.
  - `EXPLAIN` — read final Java + solver trace + stats, produce a faithful
                explanation grounded in the trace.

At L1+ each mode's responsibility is gradually delegated to a dedicated
specialist agent (Refiner at L1, Validator at L2, Formalizer at L3, Explainer
at L4).

The prompting variant is selected by env var `MONOLITH_PROMPTING`:
  - `few_shot`  (default) — worked examples per mode
  - `zero_shot`            — same system rules, no examples
  - `cot`                  — chain-of-thought (<think>...</think> + answer)
"""

from __future__ import annotations

import os
import re

from langchain_core.messages import HumanMessage, SystemMessage

from src.config import get_llm, invoke_with_retry, MAX_REFINEMENT_ITERATIONS
from src.state import PipelineState, ChocoModel, SolverResult
from src.prompts.monolith import (
    # MODEL mode
    MONOLITH_SYSTEM,            MONOLITH_HUMAN,
    MONOLITH_ZERO_SHOT_SYSTEM,  MONOLITH_ZERO_SHOT_HUMAN,
    MONOLITH_COT_SYSTEM,        MONOLITH_COT_HUMAN,
    # REFINE mode
    MONOLITH_REFINE_SYSTEM,
    MONOLITH_REFINE_FEW_SHOT_HUMAN,
    MONOLITH_REFINE_ZERO_SHOT_HUMAN,
    MONOLITH_REFINE_COT_HUMAN,
    # EXPLAIN mode
    MONOLITH_EXPLAIN_SYSTEM,
    MONOLITH_EXPLAIN_FEW_SHOT_HUMAN,
    MONOLITH_EXPLAIN_ZERO_SHOT_HUMAN,
    MONOLITH_EXPLAIN_COT_HUMAN,
)


# ── Prompt registry: (mode, variant) → (system, human_template) ──────────────


_PROMPTS: dict[str, dict[str, tuple[str, str]]] = {
    "MODEL": {
        "few_shot":  (MONOLITH_SYSTEM,           MONOLITH_HUMAN),
        "zero_shot": (MONOLITH_ZERO_SHOT_SYSTEM, MONOLITH_ZERO_SHOT_HUMAN),
        "cot":       (MONOLITH_COT_SYSTEM,       MONOLITH_COT_HUMAN),
    },
    "REFINE": {
        "few_shot":  (MONOLITH_REFINE_SYSTEM, MONOLITH_REFINE_FEW_SHOT_HUMAN),
        "zero_shot": (MONOLITH_REFINE_SYSTEM, MONOLITH_REFINE_ZERO_SHOT_HUMAN),
        "cot":       (MONOLITH_REFINE_SYSTEM, MONOLITH_REFINE_COT_HUMAN),
    },
    "EXPLAIN": {
        "few_shot":  (MONOLITH_EXPLAIN_SYSTEM, MONOLITH_EXPLAIN_FEW_SHOT_HUMAN),
        "zero_shot": (MONOLITH_EXPLAIN_SYSTEM, MONOLITH_EXPLAIN_ZERO_SHOT_HUMAN),
        "cot":       (MONOLITH_EXPLAIN_SYSTEM, MONOLITH_EXPLAIN_COT_HUMAN),
    },
}

_VALID_VARIANTS = {"few_shot", "zero_shot", "cot"}


def _current_variant() -> str:
    variant = os.getenv("MONOLITH_PROMPTING", "few_shot").lower()
    if variant not in _VALID_VARIANTS:
        raise ValueError(
            f"Unknown MONOLITH_PROMPTING={variant!r}; expected one of {sorted(_VALID_VARIANTS)}"
        )
    return variant


def _pick_prompts(mode: str) -> tuple[str, str, str]:
    """Return (variant, system_prompt, human_template) for a given mode."""
    variant = _current_variant()
    sys_p, human_t = _PROMPTS[mode][variant]
    return variant, sys_p, human_t


# ── Common helpers ────────────────────────────────────────────────────────────


_CLASS_NAME_DEFAULT = "MonolithSolver"
# Closed think block — strip greedily.
_THINK_BLOCK_CLOSED_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
# Unclosed <think> with no </think> — strip from <think> to end of text.
_THINK_BLOCK_OPEN_RE = re.compile(r"<think>.*", re.DOTALL | re.IGNORECASE)
# Code-fence variants seen in the wild: ```java\n…```  /  ```\n…```  /
# ```java …``` (no newline) /  ``` …``` (no newline). Closing fence may be
# absent if the model truncated; the extractor must still recover.
_FENCE_OPEN_RE = re.compile(r"```[a-zA-Z]*\s*\n?", re.IGNORECASE)
_FENCE_CLOSE_RE = re.compile(r"\n?\s*```")
# A real Java program always contains one of these anchors. Used as the
# last-resort recovery when fence extraction fails.
_JAVA_ANCHOR_RE = re.compile(r"^(package\s+\w|import\s+\w|public\s+class\s+\w)", re.MULTILINE)


def _derive_class_name(problem_description: str) -> str:
    """Generate a stable Java class name from a problem description."""
    words = re.sub(r"[^a-zA-Z0-9\s]", " ", problem_description).split()
    if not words:
        return _CLASS_NAME_DEFAULT
    head = "".join(w.capitalize() for w in words[:4])[:32]
    if not head or not head[0].isalpha():
        return _CLASS_NAME_DEFAULT
    return head + "Solver"


def _strip_think_block(text: str) -> str:
    """Remove <think>...</think> CoT scratchpad. Handles both closed and
    truncated/unclosed forms — the latter caused CoT compile errors when the
    open `<think>` tag bled into the .java source file.
    """
    text = _THINK_BLOCK_CLOSED_RE.sub("", text)
    text = _THINK_BLOCK_OPEN_RE.sub("", text)
    return text


def _extract_java_code(text: str) -> str:
    """Extract Java source from an LLM response.

    Robust against the response shapes that broke the original extractor:
      - ```java <code>``` (no newline after fence)
      - ``` <code> ``` (no language tag)
      - missing closing fence (model truncated mid-response)
      - leading prose / headers before the actual code
      - leftover backtick or `<think>` characters from unclosed CoT blocks
    """
    text = _strip_think_block(text).strip()

    # 1) Try to locate the opening fence and crop everything before it.
    open_m = _FENCE_OPEN_RE.search(text)
    if open_m:
        body = text[open_m.end():]
        close_m = _FENCE_CLOSE_RE.search(body)
        if close_m:
            body = body[:close_m.start()]
        text = body.strip()

    # 2) Strip any stray backticks the regex above may have left dangling.
    text = text.strip("` \n\t")

    # 3) If the result still doesn't look like Java, fall back to the first
    #    line that begins with `package`, `import`, or `public class`.
    anchor = _JAVA_ANCHOR_RE.search(text)
    if anchor:
        text = text[anchor.start():]

    return text.strip()


def _ensure_package(java_code: str) -> str:
    if "package runner;" not in java_code:
        return "package runner;\n\n" + java_code
    return java_code


def _force_class_name(java_code: str, requested: str) -> str:
    """Rewrite the public class declaration to match the requested name.

    The bridge writes the .java file using `requested` and the JVM requires the
    public class name to match the file name. Best-effort regex rewrite.
    """
    match = re.search(r"public\s+class\s+(\w+)", java_code)
    if not match:
        return java_code
    actual = match.group(1)
    if actual == requested:
        return java_code
    return re.sub(rf"\bclass\s+{re.escape(actual)}\b", f"class {requested}", java_code)


def _truncate(text: str | None, limit: int) -> str:
    """Truncate long blobs (stdout/stderr/stack traces) for prompt insertion."""
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... [truncated]"


# ── MODEL mode ────────────────────────────────────────────────────────────────


def monolith_model_node(state: PipelineState) -> dict:
    """L0 monolith — MODEL mode. NL → Java in a single LLM call."""
    problem_description = state["problem_description"]
    class_name = _derive_class_name(problem_description)
    variant, system_prompt, human_template = _pick_prompts("MODEL")

    human_content = (
        human_template
        .replace("{problem_description}", problem_description)
        .replace("{class_name}", class_name)
    )
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_content),
    ]

    response = invoke_with_retry(get_llm(), messages)
    java_code = _force_class_name(_ensure_package(_extract_java_code(response.content)), class_name)

    model = ChocoModel(
        java_code=java_code,
        class_name=class_name,
        explanation=f"Monolith MODEL (L0, {variant})",
    )
    return {
        "choco_model": model.model_dump(),
        "current_step": "modeled",
        "status": f"Choco model generated (monolith MODEL / {variant})",
    }


# ── REFINE mode ───────────────────────────────────────────────────────────────


def monolith_refine_node(state: PipelineState) -> dict:
    """L0 monolith — REFINE mode. Fix the failed Java given the solver error.

    Increments `iteration` so the workflow can bound the loop with
    MAX_REFINEMENT_ITERATIONS. Replaces `choco_model.java_code` with the fix.
    """
    problem_description = state["problem_description"]
    iteration = state.get("iteration", 0) + 1
    variant, system_prompt, human_template = _pick_prompts("REFINE")

    if "choco_model" not in state:
        # Should not happen under L0 wiring, but degrade gracefully.
        return {
            "current_step": "refined",
            "status": "Refine skipped (no choco_model in state)",
            "iteration": iteration,
        }

    prev_model = ChocoModel(**state["choco_model"])
    class_name = prev_model.class_name

    solver_dict = state.get("solver_result") or {}
    raw_status = solver_dict.get("status", "unknown")
    error_status = raw_status.value if hasattr(raw_status, "value") else str(raw_status)
    error_message = solver_dict.get("error_message", "") or ""

    error_history_lines = state.get("error_history", []) or []
    error_history_text = "\n".join(error_history_lines) if error_history_lines else "(none)"

    human_content = (
        human_template
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
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_content),
    ]

    response = invoke_with_retry(get_llm(temperature=0.2), messages)
    fixed_code = _force_class_name(_ensure_package(_extract_java_code(response.content)), class_name)

    refined_model = ChocoModel(
        java_code=fixed_code,
        class_name=class_name,
        explanation=f"Monolith REFINE (L0, {variant}, iter {iteration})",
    )
    return {
        "choco_model": refined_model.model_dump(),
        "iteration": iteration,
        "current_step": "refined",
        "status": f"Refined (monolith REFINE / {variant}, iter {iteration}/{MAX_REFINEMENT_ITERATIONS})",
    }


# ── EXPLAIN mode ──────────────────────────────────────────────────────────────


def monolith_explain_node(state: PipelineState) -> dict:
    """L0 monolith — EXPLAIN mode. Narrate the solver outcome from the trace.

    Writes the resulting prose to `state['explanation']`. Runs unconditionally
    after the solver finishes (success OR refinement-exhausted failure).
    """
    problem_description = state["problem_description"]
    iterations_used = state.get("iteration", 0)
    variant, system_prompt, human_template = _pick_prompts("EXPLAIN")

    if "choco_model" not in state:
        return {
            "explanation": "(no model was generated — nothing to explain)",
            "current_step": "explained",
            "status": "Explain skipped (no choco_model in state)",
        }

    final_model = ChocoModel(**state["choco_model"])

    solver_dict = state.get("solver_result") or {}
    raw_status = solver_dict.get("status", "unknown")
    final_status = raw_status.value if hasattr(raw_status, "value") else str(raw_status)
    solver_result = SolverResult(**solver_dict) if solver_dict else None

    solution_text = solver_result.solution_text if solver_result else ""
    monitor_traces = "\n".join(solver_result.monitor_traces) if solver_result and solver_result.monitor_traces else "(none)"
    solver_stats_dict = solver_result.statistics if solver_result else {}
    solver_stats_text = (
        "\n".join(f"  {k}: {v}" for k, v in solver_stats_dict.items())
        if solver_stats_dict else "(none)"
    )
    error_message = solver_result.error_message if solver_result else ""

    human_content = (
        human_template
        .replace("{problem_description}", problem_description)
        .replace("{class_name}", final_model.class_name)
        .replace("{final_status}", final_status)
        .replace("{iterations_used}", str(iterations_used))
        .replace("{final_java_code}", _truncate(final_model.java_code, 4000))
        .replace("{solution_text}", _truncate(solution_text, 1500) or "(none)")
        .replace("{monitor_traces}", _truncate(monitor_traces, 1500))
        .replace("{solver_stats}", _truncate(solver_stats_text, 1000))
        .replace("{error_message}", _truncate(error_message, 1000) or "(none)")
    )
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_content),
    ]

    response = invoke_with_retry(get_llm(), messages)
    explanation = _strip_think_block(response.content).strip()

    return {
        "explanation": explanation,
        "current_step": "explained",
        "status": f"Explained (monolith EXPLAIN / {variant})",
    }


# ── Back-compat alias ─────────────────────────────────────────────────────────
# Older code paths and tests refer to `monolith_node` (the original single-mode
# function). Alias to the MODEL mode so they keep working.
monolith_node = monolith_model_node

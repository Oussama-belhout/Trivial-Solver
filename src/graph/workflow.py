"""LangGraph workflow — orchestrates the multi-agent CSP solving pipeline.

This file supports two modes:

1. **Legacy mode** — `build_workflow()` with no arguments returns the original
   inherited dynamic-router graph (formalizer → modeler → validator → solver →
   refiner ↺ → explainer), with `skip_agents` as the runtime gate. `run.py`
   still uses this.

2. **PDA ablation mode** — `build_workflow(level=N)` returns a level-specific
   graph for the Progressive Decomposition Ablation study (see docs/plan.md).
   Each level wires only the nodes the rung calls for. L0 is the monolith
   baseline; L1+ are added incrementally as each previous level is validated.
"""

from langgraph.graph import StateGraph, END

from src.state import PipelineState, SolverStatus
from src.config import MAX_REFINEMENT_ITERATIONS
from src.agents.formalizer import formalizer_node
from src.agents.modeler import modeler_node
from src.agents.validator import validator_node
from src.agents.solver import solver_node
from src.agents.refiner import refiner_node
from src.agents.explainer import explainer_node
from src.agents.monolith import (
    monolith_node,            # legacy alias = monolith_model_node
    monolith_model_node,
    monolith_refine_node,
    monolith_explain_node,
)


# ── PDA — Level 0 (Monolith) ──────────────────────────────────────────────────


def _build_l0() -> "StateGraph":
    """L0 — Fat Monolith. Single LLM agent does all 5 behaviors via 3 modes.

    Topology:

        START
          |
          v
        monolith_model  -->  solver  -->  (success or iter>=MAX) --> monolith_explain --> END
                              ^                                          ^
                              |                                          |
                          monolith_refine  <--  (fail and iter<MAX) -----+

    Refinement loop bounded by MAX_REFINEMENT_ITERATIONS (inherited config).
    Explanation runs unconditionally after the solver finishes — success or
    failure — so explanation/faithfulness fields are populated at L0 too.
    """
    workflow = StateGraph(PipelineState)

    workflow.add_node("monolith_model",   monolith_model_node)
    workflow.add_node("monolith_refine",  monolith_refine_node)
    workflow.add_node("monolith_explain", monolith_explain_node)
    workflow.add_node("solver",           solver_node)

    workflow.set_entry_point("monolith_model")
    workflow.add_edge("monolith_model", "solver")

    def _route_after_solver(state: PipelineState) -> str:
        solver_result = state.get("solver_result", {}) or {}
        raw_status = solver_result.get("status", "")
        status = raw_status.value if hasattr(raw_status, "value") else str(raw_status)

        if status == SolverStatus.SUCCESS.value:
            return "monolith_explain"
        if state.get("iteration", 0) >= MAX_REFINEMENT_ITERATIONS:
            return "monolith_explain"
        return "monolith_refine"

    workflow.add_conditional_edges(
        "solver",
        _route_after_solver,
        {
            "monolith_refine":  "monolith_refine",
            "monolith_explain": "monolith_explain",
        },
    )
    workflow.add_edge("monolith_refine",  "solver")
    workflow.add_edge("monolith_explain", END)

    return workflow.compile()


# ── PDA — Levels 1..4 (stubs; implement after L0 validates) ───────────────────


def _build_l1() -> "StateGraph":
    """L1 — Refiner split. The monolith handles formalize + model + explain;
    refinement is delegated to a dedicated Reflexion-style Refiner agent.

    Topology (same shape as L0, but the refine node is the specialist):

        START
          |
          v
        monolith_model  -->  solver  -->  (success or iter>=MAX) --> monolith_explain --> END
                              ^                                          ^
                              |                                          |
                            refiner  <----  (fail and iter<MAX) ---------+

    The Refiner uses Reflexion-style prompting per docs/plan.md:
    `<reflection>...</reflection>` self-critique before emitting the fix.
    """
    workflow = StateGraph(PipelineState)

    workflow.add_node("monolith_model",   monolith_model_node)
    workflow.add_node("refiner",          refiner_node)
    workflow.add_node("monolith_explain", monolith_explain_node)
    workflow.add_node("solver",           solver_node)

    workflow.set_entry_point("monolith_model")
    workflow.add_edge("monolith_model", "solver")

    def _route_after_solver(state: PipelineState) -> str:
        solver_result = state.get("solver_result", {}) or {}
        raw_status = solver_result.get("status", "")
        status = raw_status.value if hasattr(raw_status, "value") else str(raw_status)

        if status == SolverStatus.SUCCESS.value:
            return "monolith_explain"
        if state.get("iteration", 0) >= MAX_REFINEMENT_ITERATIONS:
            return "monolith_explain"
        return "refiner"

    workflow.add_conditional_edges(
        "solver",
        _route_after_solver,
        {
            "refiner":          "refiner",
            "monolith_explain": "monolith_explain",
        },
    )
    workflow.add_edge("refiner",          "solver")
    workflow.add_edge("monolith_explain", END)

    return workflow.compile()


def _build_l2() -> "StateGraph":
    """L2 — Validator split. Three specialized roles.

    Topology:

        START
          |
          v
        monolith_model --> validator --> (valid OR iter>=MAX) --> solver
                              |                                     |
                              +-- (invalid AND iter<MAX) --> refiner
                                                                 ^
                                                                 |
                              solver --> (success OR iter>=MAX) --> monolith_explain --> END
                              solver --> (fail AND iter<MAX) ----> refiner --> validator (re-check)

    The Validator uses Adversarial CoT (NL-grounded since L2 has no Formalizer);
    when it marks the model invalid it also writes a synthetic `solver_result`
    so the refiner has an `error_message` to react to without invoking Choco.
    The Refiner stays Reflexion-style (inherited from L1).
    Refiner output loops back through the validator — pre-solver gate
    short-circuits doomed refinement loops (see plan.md L2 hypothesis).
    """
    workflow = StateGraph(PipelineState)

    workflow.add_node("monolith_model",   monolith_model_node)
    workflow.add_node("validator",        validator_node)
    workflow.add_node("refiner",          refiner_node)
    workflow.add_node("monolith_explain", monolith_explain_node)
    workflow.add_node("solver",           solver_node)

    workflow.set_entry_point("monolith_model")
    workflow.add_edge("monolith_model", "validator")

    def _route_after_validator(state: PipelineState) -> str:
        """Valid → solver. Invalid AND iter<MAX → refiner. Invalid AND iter≥MAX → solver
        (give up gating; let Choco produce a real error for the explanation step)."""
        validation = state.get("validation", {}) or {}
        if validation.get("is_valid", False):
            return "solver"
        if state.get("iteration", 0) >= MAX_REFINEMENT_ITERATIONS:
            return "solver"
        return "refiner"

    workflow.add_conditional_edges(
        "validator",
        _route_after_validator,
        {"solver": "solver", "refiner": "refiner"},
    )

    def _route_after_solver(state: PipelineState) -> str:
        solver_result = state.get("solver_result", {}) or {}
        raw_status = solver_result.get("status", "")
        status = raw_status.value if hasattr(raw_status, "value") else str(raw_status)

        if status == SolverStatus.SUCCESS.value:
            return "monolith_explain"
        if state.get("iteration", 0) >= MAX_REFINEMENT_ITERATIONS:
            return "monolith_explain"
        return "refiner"

    workflow.add_conditional_edges(
        "solver",
        _route_after_solver,
        {"refiner": "refiner", "monolith_explain": "monolith_explain"},
    )

    # Refiner re-runs through the validator — that's the whole point of the
    # pre-solver gate at L2.
    workflow.add_edge("refiner",          "validator")
    workflow.add_edge("monolith_explain", END)

    return workflow.compile()


def _build_l3() -> "StateGraph":
    """L3 — Formalizer split. Four specialized roles.

    Topology:

        START
          |
          v
        formalizer --> modeler --> validator --> (valid OR iter>=MAX) --> solver
                                       |                                    |
                                       +-- (invalid AND iter<MAX) -> refiner
                                                                       ^
                                                                       |
                                       solver --> (success OR iter>=MAX) --> monolith_explain --> END
                                       solver --> (fail AND iter<MAX) ----> refiner --> validator (re-check)

    The Formalizer uses structured output (Pydantic CSPSpecification via
    `with_structured_output`) per plan.md L3 prompting. The Modeler consumes the
    spec and emits Java. The Validator now runs on the formal spec (L3+ path),
    not the NL description. The Refiner is unchanged (still Reflexion-style)
    and keeps using the NL problem description plus the failure trace —
    by design the Refiner is spec-agnostic.

    `monolith_explain` is reused as the explanation node: the plan assigns
    "model + explain" to the Modeler at L3, and the explain prompt only depends
    on `problem_description`, `choco_model`, and `solver_result` — no spec
    needed — so reusing the existing explain node fulfills the modeler's
    explain duty without new prompt code.
    """
    workflow = StateGraph(PipelineState)

    workflow.add_node("formalizer",       formalizer_node)
    workflow.add_node("modeler",          modeler_node)
    workflow.add_node("validator",        validator_node)
    workflow.add_node("refiner",          refiner_node)
    workflow.add_node("monolith_explain", monolith_explain_node)
    workflow.add_node("solver",           solver_node)

    workflow.set_entry_point("formalizer")
    workflow.add_edge("formalizer", "modeler")
    workflow.add_edge("modeler",    "validator")

    def _route_after_validator(state: PipelineState) -> str:
        validation = state.get("validation", {}) or {}
        if validation.get("is_valid", False):
            return "solver"
        if state.get("iteration", 0) >= MAX_REFINEMENT_ITERATIONS:
            return "solver"
        return "refiner"

    workflow.add_conditional_edges(
        "validator",
        _route_after_validator,
        {"solver": "solver", "refiner": "refiner"},
    )

    def _route_after_solver(state: PipelineState) -> str:
        solver_result = state.get("solver_result", {}) or {}
        raw_status = solver_result.get("status", "")
        status = raw_status.value if hasattr(raw_status, "value") else str(raw_status)
        if status == SolverStatus.SUCCESS.value:
            return "monolith_explain"
        if state.get("iteration", 0) >= MAX_REFINEMENT_ITERATIONS:
            return "monolith_explain"
        return "refiner"

    workflow.add_conditional_edges(
        "solver",
        _route_after_solver,
        {"refiner": "refiner", "monolith_explain": "monolith_explain"},
    )

    workflow.add_edge("refiner",          "validator")
    workflow.add_edge("monolith_explain", END)

    return workflow.compile()


def _build_l4() -> "StateGraph":
    raise NotImplementedError("L4 not yet implemented — validate L3 first.")


_LEVEL_BUILDERS = {
    0: _build_l0,
    1: _build_l1,
    2: _build_l2,
    3: _build_l3,
    4: _build_l4,
}


# ── Legacy — inherited dynamic-router graph (kept for run.py back-compat) ─────


def route_after_validation(state: PipelineState) -> str:
    """Route based on validation result: proceed to solver or go back to refiner."""
    validation = state.get("validation", {})
    if validation.get("is_valid", False):
        return "solver"
    iteration = state.get("iteration", 0)
    if iteration >= MAX_REFINEMENT_ITERATIONS:
        return "solver"
    return "refiner"


def route_after_solver(state: PipelineState) -> str:
    """Route based on solver result: explain success or refine failure."""
    solver_result = state.get("solver_result", {})
    status = solver_result.get("status", "")

    if status == SolverStatus.SUCCESS.value:
        return "explainer"
    iteration = state.get("iteration", 0)
    if iteration >= MAX_REFINEMENT_ITERATIONS:
        return "explainer"
    return "refiner"


SEQUENCE = ["formalizer", "modeler", "validator", "solver", "explainer"]


def dynamic_router(state: PipelineState, current_node: str) -> str:
    """Find the next node in SEQUENCE that is not in skip_agents."""
    skip_agents = state.get("skip_agents", [])
    try:
        current_idx = SEQUENCE.index(current_node)
    except ValueError:
        return END

    for i in range(current_idx + 1, len(SEQUENCE)):
        next_node = SEQUENCE[i]
        if next_node not in skip_agents:
            return next_node
    return END


def _build_legacy() -> "StateGraph":
    """Inherited dynamic-router graph. Used by run.py for the full pipeline."""
    workflow = StateGraph(PipelineState)

    workflow.add_node("formalizer", formalizer_node)
    workflow.add_node("modeler", modeler_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("solver", solver_node)
    workflow.add_node("refiner", refiner_node)
    workflow.add_node("explainer", explainer_node)

    workflow.add_conditional_edges(
        "__start__",
        lambda state: dynamic_router(state, "") if dynamic_router(state, "") != END else "formalizer",
    )

    workflow.add_conditional_edges("formalizer", lambda state: dynamic_router(state, "formalizer"))
    workflow.add_conditional_edges("modeler", lambda state: dynamic_router(state, "modeler"))

    def handle_validator(state: PipelineState) -> str:
        validation = state.get("validation", {})
        if validation.get("is_valid", False):
            return dynamic_router(state, "validator")
        iteration = state.get("iteration", 0)
        if iteration >= MAX_REFINEMENT_ITERATIONS:
            return dynamic_router(state, "validator")
        if "refiner" in state.get("skip_agents", []):
            return dynamic_router(state, "validator")
        return "refiner"

    workflow.add_conditional_edges("validator", handle_validator)

    def handle_solver(state: PipelineState) -> str:
        solver_result = state.get("solver_result", {})
        status = solver_result.get("status", "")
        if status == SolverStatus.SUCCESS.value:
            return dynamic_router(state, "solver")
        iteration = state.get("iteration", 0)
        if iteration >= MAX_REFINEMENT_ITERATIONS:
            return dynamic_router(state, "solver")
        if "refiner" in state.get("skip_agents", []):
            return dynamic_router(state, "solver")
        return "refiner"

    workflow.add_conditional_edges("solver", handle_solver)

    def handle_refiner(state: PipelineState) -> str:
        return dynamic_router(state, "formalizer")

    workflow.add_conditional_edges("refiner", handle_refiner)
    workflow.add_conditional_edges("explainer", lambda state: dynamic_router(state, "explainer"))

    return workflow.compile()


# ── Public API ────────────────────────────────────────────────────────────────


def build_workflow(level: int | None = None):
    """Build a CSP solving pipeline.

    - `level=None` (default): legacy inherited graph — used by run.py.
    - `level=0..4`: PDA ablation level (see docs/plan.md).
    """
    if level is None:
        return _build_legacy()
    if level not in _LEVEL_BUILDERS:
        raise ValueError(f"Unknown level {level}; expected 0..4")
    return _LEVEL_BUILDERS[level]()


# ── Convenience wrappers (kept for back-compat) ───────────────────────────────


def run_pipeline(problem_description: str, level: int | None = None) -> dict:
    """Run the pipeline once and return the final state."""
    graph = build_workflow(level=level)
    initial_state = {
        "problem_description": problem_description,
        "iteration": 0,
        "error_history": [],
        "current_step": "starting",
        "status": "Pipeline started",
        "messages": [],
        "skip_agents": [],
    }
    return graph.invoke(initial_state)


def stream_pipeline(problem_description: str, level: int | None = None):
    """Yield streaming updates from the pipeline."""
    graph = build_workflow(level=level)
    initial_state = {
        "problem_description": problem_description,
        "iteration": 0,
        "error_history": [],
        "current_step": "starting",
        "status": "Pipeline started",
        "messages": [],
        "skip_agents": [],
    }
    for event in graph.stream(initial_state, stream_mode="updates"):
        yield event

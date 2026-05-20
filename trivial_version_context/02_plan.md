# 02 — Plan: Progressive Delegation Ablation (PDA)



## Reframing (lock-in change, 2026-05-04)

The earlier framing was **additive**: each level *adds* a new behavior. Replaced with a **delegation framing**: all five behaviors are present at every level; the only thing that changes is how they are **delegated across agents**. This makes the study answer the actual research question — *"what is the effect of adding delegation (introducing an extra agent and migrating responsibility to a multi-agent system) on the performance of a CSP-solving pipeline?"*

## The five behaviors (constant across all levels)

1. **Formalization** — extract variables, domains, constraints from the NL description.
2. **Modeling**       — generate compilable Choco Java code that implements the formalization.
3. **Validation**     — semantic pre-solver check that the model captures the problem.
4. **Refinement**     — read solver / compiler / validator failure and produce a fixed model. Bounded retry loop (`MAX_REFINEMENT_ITERATIONS`, default 3) exists at **every** level.
5. **Explanation**    — post-solver narrative grounded in the actual solver trace (variable assignments, monitor traces, statistics).

## Methodology

Start with the simplest viable delegation (one agent does all five behaviors). At each rung, **split out exactly one behavior into its own dedicated agent**. The behavior left unspecialized is performed by whichever agent is "general purpose" at that level. The deterministic Choco solver is fixed and is **not** an LLM agent.

A **plateau** is a finding, not a failure — it tells you which delegations matter for Q1 (solving) vs. Q2 (explanation).

## The 4-rung delegation ladder

| Level | # agents | Behavior → agent mapping |
|---|---|---|
| **L0 — Monolith** | 1 | Monolith does all 5 behaviors (formalize + model + validate + refine + explain) by being re-invoked in three modes: `MODEL`, `REFINE`, `EXPLAIN`. Refinement loop bounded by `MAX_REFINEMENT_ITERATIONS`. |
| **L1 — Refiner split** | 2 | Monolith: formalize + model + validate + explain.  **Refiner**: refine (specialized). |
| **L2 — Validator split** | 3 | Monolith: formalize + model + explain.  **Validator**: validate (pre-solver gate).  Refiner: refine. |
| **L3 — Formalizer split** | 4 | **Formalizer**: formalize (NL → JSON spec).  Modeler: model + explain.  Validator.  Refiner. |


4 configurations × 12 benchmarks = **48 runs** for the headline curve. Optional bake-off at L0 across three prompting techniques (zero-shot, few-shot, CoT) adds 24 more runs.

## Locked hypotheses (committed before measurement)

| Level | Hypothesis vs. previous level | Speaks to |
|---|---|---|
| **L0** | Baseline. Monolith juggling 5 behaviors will fail on hard problems and on syntactic edge cases. Refinement loop will recover some compile errors. | Q1 |
| **L1** | **Up**, primarily on syntactic / compilation failures. Specialized refiner reads errors more carefully than a monolith doing refinement as a side task. | Q1, Q3 |
| **L2** | **Up slightly**; **mean refinement iterations down**. Pre-solver semantic gate short-circuits doomed refinement loops. | Q1, Q3 |
| **L3** | **Up on complex problems**; flat on small problems; **mean tokens / call drops**. Decoupling formalization from modeling reduces per-call cognitive load. | Q1 |

## Prompting technique — the newly-split agent uses

The technique listed below is the one used by the **newly-specialized agent at that level**. Agents that were already split keep their previous level's technique. Monolith always uses few-shot for its retained behaviors.

| Level | Newly-split agent | Technique it uses |
|---|---|---|
| L0 | (Monolith — all behaviors) | Few-shot (1–2 worked examples) |
| L1 | Refiner | Reflexion-style (read previous error, rewrite) |
| L2 | Validator | Adversarial CoT (find what's wrong before saying it's right) |
| L3 | Formalizer | Structured output (Pydantic schema via `with_structured_output`) |

Optional sidebar at L0: bake-off of zero-shot vs. few-shot vs. CoT on the monolith's MODEL mode. Stored as `results/mono_{variant}.json`.

## Metrics — cheap and deterministic for the curve

| Metric | Source | Q | Question it answers |
|---|---|---|---|
| Success rate | Choco produced valid solution? (boolean) | Q1 | Does it solve? |
| First-shot success rate | Same, but `iterations == 0` | Q1 | Base capability without retry |
| Mean refinement iterations | State counter (incremented on each refiner call) | Q3 | Does the refinement loop converge? |
| Compilation failure rate | Maven exit code | Q1 | Which errors does the LLM make? |
| Wall time (LLM vs JVM) | Already traced | — | Cost story |
| Solver stats (backtracks, propagations, nodes) | Choco output | Q1 | Proves real solver was used |
| Mean tokens per call (per agent) | LangSmith | — | The decoupling argument for L3 |
| Faithfulness (regex) | `evaluate.py:_faithfulness_score` — variable-name overlap + ≥1 numeric stat | Q2 | Is the explanation grounded in the trace? |

LLM-as-judge faithfulness is deferred — escalate only for L0 vs. L3 comparison if the regex signal is ambiguous.

## CSPLib

12 inherited benchmarks include CSPLib classics (4-Queens / 8-Queens prob054, Magic Square prob019, SEND+MORE=MONEY prob023, Graph Coloring prob004, Latin Square prob003, Sudoku prob028). Cite the prob-IDs in the report — external validity earned, zero new code.

## Repo layout

```
src/
  graph/workflow.py        ← build_workflow(level: int) wires per-level delegation
  agents/
    monolith.py            ← multi-mode (MODEL / REFINE / EXPLAIN); used at L0–L2 in shrinking roles
    formalizer.py          ← used at L3+
    modeler.py             ← used at L3+
    validator.py           ← used at L2+
    refiner.py             ← used at L1+
    solver.py              ← deterministic Choco bridge (NOT an LLM)
  prompts/
    monolith.py            ← MODEL/REFINE/EXPLAIN × {zero_shot, few_shot, cot}
    {refiner,validator,formalizer,modeler}.py
  state.py
  config.py
evaluate.py                ← --level {0..3} [--prompting {zero_shot,few_shot,cot}]
make_curve.py              ← reads results/, emits one figure
results/
  level_0.json … level_3.json
  mono_zero_shot.json mono_few_shot.json mono_cot.json   (L0 prompting bake-off)
docs/
  foundations.md  hypotheses.md  plan.md
```

## 2.5-hour time budget (revised)

| Block | Min | Task |
|---|---|---|
| 0:00–0:15 | 15 | Re-lock hypotheses (this doc + docs/foundations.md). |
| 0:15–0:45 | 30 | Implement L0 fat monolith (MODEL/REFINE/EXPLAIN modes + refinement loop + 3 prompting variants). |
| 0:45–1:00 | 15 | Run L0 grid × 3 prompting variants → `mono_*.json`. |
| 1:00–1:15 | 15 | Implement L1 (split refiner out; monolith keeps the rest). Run grid → `level_1.json`. |
| 1:15–1:30 | 15 | Implement L2 (split validator out). Run grid → `level_2.json`. |
| 1:30–1:45 | 15 | Implement L3 (split formalizer / modeler; modeler also explains). Run grid → `level_3.json`. |

| 1:45–2:15 | 30 | Plot curve. Per-level paragraph: hypothesis vs. result. |

## Tweaks the user already accepted (carried over)

1. **Reuse, don't rebuild.** Inherit existing agents; re-wire the graph via the `level` parameter.
2. **Lock hypotheses upfront.** 15-minute non-negotiable cost.
3. **One model, one prompting technique per level** for the headline.
4. **Plateau is a result.** L3 not moving success rate is still evidence that delegation gains are marginal on Q1 at this scale.
5. **Token budget per call** is the empirical decoupling argument at L3.
6. **Choco is deterministic** — say so explicitly early in the report.
7. **Faithfulness LLM-judge deferred** — regex first.

## New tweaks accepted with this re-framing (2026-05-04)

8. **All behaviors exist at every level.** Refinement loop is universal; explanation is universal.
9. **Delegation order locked**: refiner → validator → formalizer.
10. **Monolith is multi-mode**, not a single-shot agent. At L0 it wears 5 hats; at higher levels it sheds hats one by one.

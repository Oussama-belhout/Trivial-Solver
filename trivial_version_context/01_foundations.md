# 01 — Foundations (First Principles)

## The single sentence

We are studying whether a stochastic system (an LLM) can drive a deterministic system (a constraint solver) to **solve, explain, and improve** on combinatorial problems given only a natural-language description.

The pipeline is **not the project**. The pipeline is the *instrument* used to interrogate the question.

## The three foundational questions

| # | Question | What it really asks |
|---|----------|---------------------|
| **Q1** | Can we solve a problem from its description? | Is the NL → formal model → solution chain reliable enough to be useful? |
| **Q2** | Can the LLM explain *how* and *why* a solution was reached? | Can the system produce **faithful** explanations grounded in the actual solver trace, not post-hoc storytelling? |
| **Q3** | Can we automatically improve the solving and/or the explanation? | Does iteration (refinement, agent decomposition) **converge**, **stagnate**, or **degrade**? |

Hierarchy: Q1 is necessary, Q2 differentiates this from "just a solver," Q3 is the meta-question.

**Test for any change you propose:** does it move evidence about Q1, Q2, or Q3? If none, don't do it.

## The triad applied to every design decision

For each agent or pipeline change, you must be able to fill in:

- **Comment? (How / Conception, with argumentation)** — why this decomposition? An agent earns its place only if its prompt context, output schema, or temperature is incompatible with another agent's. Otherwise it's decoration.
- **Pour quoi? (For what / Examples)** — which benchmark problem class exposes the failure that this agent corrects?
- **Quelle efficacité? (Evaluation)** — what is the measured ablation delta when this agent is removed?

If any of those three are blank, the agent does not survive the report.

## Project framing

This is a **scientific study with an XAI sub-angle**, not a deployable tool:

- **Path A (spine):** empirical study answering Q1/Q2/Q3 with numbers.
- **Path C (sub-angle):** explanation faithfulness — the most differentiated angle vs. existing "LLM + solver" work.

We deliberately reject:
- Engineering-heavy "polish the tool" path (no UI work, no broader problem zoo).

## What you track (preview — full list in `02_plan.md`)

Cheap & deterministic: success rate, refinement iterations, compilation failure rate, wall time, solver statistics (backtracks, propagations, nodes), token usage per agent.

Expensive & limited: explanation faithfulness — start with a regex check (variable-name overlap + reference to ≥1 solver statistic), only escalate to LLM-as-judge for L0 vs. L3 if time allows.

# CSP Solver — Progressive Decomposition Ablation (Trivial-First Rebuild)

You are helping rebuild a CSP-solving multi-agent system **from a trivial baseline upward**, so that every added agent is justified by a measured performance delta.

## One-line goal
Demonstrate that each LLM agent in a CSP-solving pipeline earns its place via measured ablation, producing a monotonic (or plateauing) success-rate curve across 4 increments L0 → L3.

## How to read this folder

Read these in order **before writing any code**:

1. `01_foundations.md` — why this project exists (first principles, Q1/Q2/Q3).
2. `02_plan.md` — what to build, in 4 increments, with hypotheses locked in advance.
3. `03_inheritance.md` — what to copy from the previous project, what to leave behind.

## Hard constraints (do not violate)

- **Time budget: 2h30 total.** Treat this as a sprint, not a refactor.
- **No new features.** If something is not in `02_plan.md`, do not build it.
- **The Choco solver is deterministic — it is NOT an LLM agent.** "Adding an agent" only ever means adding an *LLM* node.
- **Lock hypotheses BEFORE running.** The science is in committing to predictions and reporting hits/misses, not post-hoc storytelling.
- **Reuse, don't rebuild.** The previous project's agents, prompts, and Choco bridge are inherited (see `03_inheritance.md`).
- **One model, one prompting technique per level** for the headline curve. Provider ablation is a sidebar at most.

## First action

Before writing code, confirm with the user:
1. Which level you're implementing first (default: L0).
2. That `01_foundations.md`, `02_plan.md`, `03_inheritance.md` have been read.
3. Whether the inherited files from the old project have been copied over.

Do **not** assume; ask.

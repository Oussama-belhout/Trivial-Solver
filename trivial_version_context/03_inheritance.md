# 03 — Inheritance: What to Copy from the Old Project

The old project lives at `C:\Users\belho\OneDrive\Documents\UNICA M1 COURSES\DS4H\firstShowcase - Kaggle`. Most of its code is sound and should be reused as-is. Do not rebuild what already works.

## COPY (drop into the new project unchanged)

| Path | Why |
|---|---|
| `src/agents/formalizer.py` | Used at L3 (and the spec it produces is consumed by other levels). |
| `src/agents/modeler.py` | Used at L3. |
| `src/agents/validator.py` | Used at L2+. |
| `src/agents/refiner.py` | Used at L1+. |
| `src/agents/solver.py` | Wraps the deterministic Choco run; not an LLM. |
| `src/prompts/*.py` | All prompt templates. May tweak per level (one technique per level — see plan). |
| `src/choco/bridge.py` | Compiles + runs LLM-generated Java with Maven. Don't touch. |
| `src/choco/parser.py` | Extracts solutions and Choco statistics. Don't touch. |
| `src/state.py` | Pydantic + TypedDict state schema. Already has `skip_agents` — extend, don't replace. |
| `src/config.py` | LLM provider abstraction (Groq / GPT-4o / Ollama / Kaggle ...ect ), retry logic. |
| `benchmarks.py` | The 12 CSP benchmarks (incl. CSPLib classics). |
| `requirements.txt` | Dependencies. |
| `choco_runner/` | The Java/Maven project skeleton the bridge writes into. |
| `run.py` | CLI entry point — needed for the end-to-end sanity test (see bottom of this file). |

## How inference works

`src/config.py` is a **multi-provider LLM abstraction** with retry logic. Out of the box it supports:

| Provider | Notes | Use when |
|---|---|---|
| **Groq** (default) | Free API, fast. Models: `groq_llama70b`, `groq_llama8b`, `groq_gemma9b`. | Default for the headline curve. |
| GPT-4o | Paid. | Only if you want a closed-model comparison row. |
| Ollama | Fully local. | Offline / deterministic-pipeline runs. |
| Kaggle | Self-hosted GPU via ngrok (see optional below). | Only if Groq is rate-limited AND you want a self-hosted open model. |
... and others

For the 4-level ablation you only need **Groq** + a working `GROQ_API_KEY` in `.env`. No Kaggle setup required.

## OPTIONAL (copy only if you want Kaggle GPU inference)

| Path | Why optional |
|---|---|
| `kaggle_server.py` | Standalone Flask server you paste into a Kaggle notebook to host an open model on a free T4 GPU. Only needed if you want to use `LLM_PROVIDER=kaggle`. |
| `architecture.md` (Kaggle setup section only) | Step-by-step instructions for pasting `kaggle_server.py` into a notebook and getting an ngrok URL. Reference only — do not let it bleed into the new project's docs. |

## REWRITE (small, surgical changes)

| Path | Change |
|---|---|
| `src/graph/workflow.py` | Add `build_workflow(level: int) -> CompiledGraph`. Re-wire which nodes are present per level (see L0..L3 in `02_plan.md`). The old file already has a `skip_agents` mechanism — extend it. |
| `evaluate.py` | Add `--level {0,1,2,3}` flag. Emit one JSON per run with the metric set defined in `02_plan.md`. |

## CREATE (new files)

| Path | Purpose |
|---|---|
| `src/agents/monolith.py` | The single-shot agent for L0. NL → Java in one prompt. Does not call the formalizer / modeler / validator / refiner chain. Reuses the Choco bridge. |
| `src/prompts/monolith.py` | Few-shot prompt template for L0 (1–2 worked examples). |
| `make_curve.py` | Reads `results/level_*.json`, writes `results/curve.png` (success rate vs. level) plus a small table per level. |
| `docs/foundations.md`, `docs/hypotheses.md`, `docs/plan.md` | Copies of the corresponding files in this context folder, committed as the report scaffold. |

## DO NOT COPY (out of scope for this sprint)

| Path | Why excluded |
|---|---|
| `app.py` (Streamlit UI) | Not needed for the study. |
| `midterm_report.tex` | Old report. The new one is built from the curve + per-level paragraphs. |
| `out.log`, `__pycache__/`, `venv/` | Junk. |

## Sanity checks before coding

1. Confirm `mvn` and `java 17+` are on PATH (the bridge needs them).
2. Confirm `.env` contains a working `GROQ_API_KEY` (default model: Groq Llama 3.3 70B).
3. Confirm `LANGSMITH_API_KEY` is set if you want token-per-call traces (used for the L3 decoupling argument).
4. Run one inherited end-to-end test (`python run.py "4-queens"`) BEFORE editing anything, to confirm the inherited code still works in the new repo.

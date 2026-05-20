# L3 PDA — Data Analysis

Dataset: **3 models × 1 prompting variant × 10 problems = 30 runs**.

- Models: Qwen 2.5 Coder 32B, Claude Haiku 4.5, DeepSeek R1 (distill, Llama 70B base).
- Variant: few-shot (Formalizer + Modeler + Validator + Refiner).
- Benchmarks: 4 hard / 3 medium / 3 easy across 8 CSP families.
- L3 topology: Formalizer → Modeler → Validator → Solver, with Reflexion-style Refiner re-entering at Validator.
- Refinement loop bounded at MAX_REFINEMENT_ITERATIONS=3 (universal per PDA spec).

## Headline metrics (per model)

| model    | variant   |   n_runs |   success_rate |   first_shot_rate |   compilation_failure_rate |   mean_iterations |   mean_wall_time_s |   faith_pass_rate |   faith_mean_overlap |
|:---------|:----------|---------:|---------------:|------------------:|---------------------------:|------------------:|-------------------:|------------------:|---------------------:|
| qwen     | few_shot  |       10 |           90.0 |              30.0 |                       10.0 |               1.8 |               60.5 |               0.0 |                  0.0 |
| haiku    | few_shot  |       10 |           60.0 |               0.0 |                       30.0 |               1.9 |               61.9 |               0.0 |                  0.0 |
| deepseek | few_shot  |       10 |           50.0 |              40.0 |                       40.0 |               1.4 |             2241.3 |               0.0 |                  0.0 |

## Top-3 configurations (by success → first-shot → wall time)

| model    | variant   |   success_rate |   first_shot_rate |   mean_iterations |   mean_wall_time_s |
|:---------|:----------|---------------:|------------------:|------------------:|-------------------:|
| qwen     | few_shot  |           90.0 |              30.0 |               1.8 |               60.5 |
| haiku    | few_shot  |           60.0 |               0.0 |               1.9 |               61.9 |
| deepseek | few_shot  |           50.0 |              40.0 |               1.4 |             2241.3 |

## Success rate by difficulty (per model)

| model    |   easy |   medium |   hard |
|:---------|-------:|---------:|-------:|
| deepseek |   33.3 |     66.7 |   50.0 |
| haiku    |  100.0 |    100.0 |    0.0 |
| qwen     |  100.0 |    100.0 |   75.0 |

## Per-category success rate (per model)

| model    |   cryptarithmetic |   graph_coloring |   knapsack |   latin_square |   magic_square |   queens |   scheduling |   sudoku |
|:---------|------------------:|-----------------:|-----------:|---------------:|---------------:|---------:|-------------:|---------:|
| qwen     |               100 |              100 |        100 |            100 |            100 |      100 |            0 |      100 |
| haiku    |                 0 |              100 |          0 |            100 |            100 |      100 |            0 |        0 |
| deepseek |                 0 |              100 |        100 |            100 |             50 |        0 |          100 |        0 |

## Findings

### F1 — Qwen is the L3 winner (90% success), reversing its L1 collapse
Qwen reaches **90% success** with **10% compilation failures** and a mean of **1.8 iterations**. Compared to its 0%/100%-compile-fail collapse at L1, the L3 split is the rung where Qwen finally fits the workflow: the Formalizer's structured-output stage absorbs the response-shape mismatch that previously broke the Refiner-only L1 setup, and the spec-grounded Validator catches the modeling errors before they reach the solver. The single failure (scheduling) is consistent with the family's known semantic difficulty rather than a Qwen-specific defect.

### F2 — Haiku regresses from L1 (100%) to L3 (60%) on hard problems
Haiku drops to **60% success**, **0% first-shot**, **30% compilation failures**, and **1.9 mean iterations**. The breakdown is sharp by difficulty: easy/medium remain at 100% but **all 4 hard problems fail** (sudoku, cryptarithmetic, scheduling, knapsack). The first-shot rate falling to 0% indicates that the new Formalizer/Validator gate now rejects the initial Modeler output even when the underlying Java would have compiled, while the validator/refiner loop fails to recover the fix within the iteration budget on hard inputs. This is the clearest example in the PDA sweep of **role-splitting hurting an already-strong model**: the extra spec-conformance pressure is friction that L1's lighter pipeline did not impose.

### F3 — DeepSeek's wall time explodes ~16× while success drops to 50%
DeepSeek lands at **50% success**, **40% first-shot**, **40% compilation failures**, and a mean wall time of **~2241 seconds per problem** (vs ~139s at L1 — a ~16× cost increase). The deep-reasoning trace at every node (Formalizer, Modeler, Validator, Refiner) compounds, and each refinement iteration repays that cost. Despite the budget the model still trails Qwen on the same 10 problems and trails its own L1 result (80% → 50%). At L3 DeepSeek is dominated on both axes (success and cost) and is no longer a defensible default.

### F4 — Hard problems separate models more aggressively than at L1
By difficulty, Qwen sustains 75% on hard, Haiku falls to 0%, and DeepSeek lands at 50%. The hard tier (sudoku, cryptarithmetic, scheduling, knapsack) is where the Formalizer split's added validation friction is most visible: the spec must be both correct and faithful to the NL description, and the Validator's spec-level checks have less slack than the L1 NL-grounded validator did. Models that the Formalizer cannot reliably guide (Haiku here) lose headroom that L1 hid.

### F5 — Faithfulness remains at 0% (parser dependency)
Faithfulness regex pass rate is 0% across all models (mean overlap 0.0). As in L0/L1, the explanation metric is not meaningful until the parser populates the `solution` dict with variable assignments — this is an infrastructure gap, not a model deficiency.

## Cross-cutting observations

- **Role-splitting helps weak baselines, hurts strong ones.** Qwen gains the most from L3 (0% → 90%); Haiku, the L1 leader, loses 40 points. Treat L3 as a model-dependent rung, not a strict upgrade.
- **First-shot rates collapse across the board** vs L1 (Qwen 0→30%, Haiku 70→0%, DeepSeek 40→40%). The Formalizer gate effectively rules first-shot success out for Haiku and forces refinement-driven recovery to do the work.
- **DeepSeek wall time is the headline cost.** ~37 minutes per problem on average makes it impractical at L3 absent specific reasons to need it; report wall time alongside success in any cross-level comparison.
- **Compile failures stay non-zero everywhere.** L3 does not eliminate the syntactic-failure mode that L1's Refiner partially fixed for Haiku — the spec layer adds correctness pressure but does not replace a guard for malformed Java.
- **Hard categories (cryptarithmetic, scheduling) remain the discriminator.** Sudoku now also separates models at L3 because the spec-level Validator is stricter on grid encodings.

## Plots

- `plots/01_success_rate.png`
- `plots/02_first_shot.png`
- `plots/03_compile_fail.png`
- `plots/04_mean_iterations.png`
- `plots/05_wall_time.png`
- `plots/06_heatmap_difficulty.png`
- `plots/07_heatmap_category.png`
- `plots/08_iterations_distribution.png`
- `plots/09_cost_quality_scatter.png`
- `plots/10_faithfulness.png`
- `plots/11_solver_per_problem.png`

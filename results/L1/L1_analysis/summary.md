# L1 PDA — Data Analysis

Dataset: **3 models × 1 prompting variant × 10 problems = 30 runs**.

- Models: Qwen 2.5 Coder 32B, Claude Haiku 4.5, DeepSeek R1 (distill, Llama 70B base).
- Variant: few-shot (monolith) + reflexive refiner per plan.
- Benchmarks: 4 hard / 3 medium / 3 easy across 8 CSP families.
- Refinement loop bounded at MAX_REFINEMENT_ITERATIONS=3 (universal per PDA spec).

## Headline metrics (per model)

| model    | variant   |   n_runs |   success_rate |   first_shot_rate |   compilation_failure_rate |   mean_iterations |   mean_wall_time_s |   faith_pass_rate |   faith_mean_overlap |
|:---------|:----------|---------:|---------------:|------------------:|---------------------------:|------------------:|-------------------:|------------------:|---------------------:|
| qwen     | few_shot  |       10 |            0.0 |               0.0 |                      100.0 |               3.0 |               23.1 |               0.0 |                  0.0 |
| haiku    | few_shot  |       10 |          100.0 |              70.0 |                        0.0 |               0.5 |               19.5 |               0.0 |                  0.0 |
| deepseek | few_shot  |       10 |           80.0 |              40.0 |                       20.0 |               1.1 |              139.3 |               0.0 |                  0.0 |

## Top-3 configurations (by success → first-shot → wall time)

| model    | variant   |   success_rate |   first_shot_rate |   mean_iterations |   mean_wall_time_s |
|:---------|:----------|---------------:|------------------:|------------------:|-------------------:|
| haiku    | few_shot  |          100.0 |              70.0 |               0.5 |               19.5 |
| deepseek | few_shot  |           80.0 |              40.0 |               1.1 |              139.3 |
| qwen     | few_shot  |            0.0 |               0.0 |               3.0 |               23.1 |

## Success rate by difficulty (per model)

| model    |   easy |   medium |   hard |
|:---------|-------:|---------:|-------:|
| deepseek |  100.0 |    100.0 |   50.0 |
| haiku    |  100.0 |    100.0 |  100.0 |
| qwen     |    0.0 |      0.0 |    0.0 |

## Per-category success rate (per model)

| model    |   cryptarithmetic |   graph_coloring |   knapsack |   latin_square |   magic_square |   queens |   scheduling |   sudoku |
|:---------|------------------:|-----------------:|-----------:|---------------:|---------------:|---------:|-------------:|---------:|
| qwen     |                 0 |                0 |          0 |              0 |              0 |        0 |            0 |        0 |
| haiku    |               100 |              100 |        100 |            100 |            100 |      100 |          100 |      100 |
| deepseek |                 0 |              100 |        100 |            100 |            100 |      100 |            0 |      100 |

## Findings

### F1 — L1 refiner split removes compile failures for Haiku
Haiku reaches **100% success** with **0% compilation failures** and a mean of **0.5 iterations**, matching the L1 hypothesis that a specialized refiner reduces syntactic/compile errors while keeping iteration counts low. This is a tangible win over L0 for the strongest model (few-shot baseline).

### F2 — DeepSeek improves but still fails on cryptarithmetic and scheduling
DeepSeek reaches **80% success** (2 compile failures) with mean iterations **1.1**. The failures are concentrated in SEND+MORE=MONEY and Job Scheduling, suggesting the refiner improves syntactic recovery but does not consistently rescue semantic modeling errors in the hardest formalization families.

### F3 — Qwen collapses at L1 with 100% compilation errors
Qwen reports **0% success** and **100% compilation failures** at L1. This is a reversal from L0 and likely indicates a mismatch between the refiner prompt and Qwen's response shape (e.g., markdown fences or hidden reasoning leaking into Java). If Qwen is to be retained for L1+, it needs prompt hardening or an extraction guard similar to the L0 fix.

### F4 — Faithfulness remains at 0% (parser dependency)

Faithfulness regex pass rate is 0% across all models. As in L0, the explanation metric is not meaningful until the parser populates the `solution` dict with variable assignments.

## Cross-cutting observations

- The L1 delegation (refiner split) mainly shifts **compile failure rate** and **iterations**, not raw success for strong models.
- DeepSeek remains significantly slower than Haiku even at L1, so per-level cost comparisons should report wall time alongside success.
- The hardest families (cryptarithmetic, scheduling) still separate models; category heatmaps remain the clearest failure signal.

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

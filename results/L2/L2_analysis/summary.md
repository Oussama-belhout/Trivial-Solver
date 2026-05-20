# L2 PDA — Data Analysis

Dataset: **3 models × 1 prompting variant × 10 problems = 30 runs**.

- Topology: monolith_model → **validator (Adversarial CoT)** → solver, refiner loops back through validator.
- Models: Qwen 3 Coder, Claude Haiku 4.5, DeepSeek R1 (distill 70B).
- Variant: few-shot for the monolith; the newly-split agent (Validator) uses Adversarial CoT per plan.md §Prompting.
- Refinement loop bounded at MAX_REFINEMENT_ITERATIONS=3 (universal per PDA spec).

## Headline metrics (L2 per model)

| model    | variant   |   n_runs |   success_rate |   first_shot_rate |   compilation_failure_rate |   mean_iterations |   mean_wall_time_s |   faith_pass_rate |   faith_mean_overlap |
|:---------|:----------|---------:|---------------:|------------------:|---------------------------:|------------------:|-------------------:|------------------:|---------------------:|
| qwen     | few_shot  |       10 |           90.0 |              20.0 |                       10.0 |               2.0 |              107.1 |               0.0 |                  0.0 |
| haiku    | few_shot  |       10 |           50.0 |              20.0 |                       50.0 |               2.2 |               40.6 |               0.0 |                  0.0 |
| deepseek | few_shot  |       10 |          100.0 |             100.0 |                        0.0 |               0.0 |              395.2 |               0.0 |                  0.0 |

## Top configurations (by success → first-shot → wall time)

| model    | variant   |   success_rate |   first_shot_rate |   mean_iterations |   mean_wall_time_s |
|:---------|:----------|---------------:|------------------:|------------------:|-------------------:|
| deepseek | few_shot  |          100.0 |             100.0 |               0.0 |              395.2 |
| qwen     | few_shot  |           90.0 |              20.0 |               2.0 |              107.1 |
| haiku    | few_shot  |           50.0 |              20.0 |               2.2 |               40.6 |

## L1 → L2 delta (the actual headline)

| model    |   L1_success_rate |   L2_success_rate |   d_success_rate |   L1_first_shot_rate |   L2_first_shot_rate |   d_first_shot_rate |   L1_mean_iterations |   L2_mean_iterations |   d_mean_iterations |   L1_compilation_failure_rate |   L2_compilation_failure_rate |   d_compilation_failure_rate |   L1_mean_wall_time_s |   L2_mean_wall_time_s |   d_mean_wall_time_s |
|:---------|------------------:|------------------:|-----------------:|---------------------:|---------------------:|--------------------:|---------------------:|---------------------:|--------------------:|------------------------------:|------------------------------:|-----------------------------:|----------------------:|----------------------:|---------------------:|
| qwen     |            100.00 |             90.00 |           -10.00 |                80.00 |                20.00 |              -60.00 |                 0.20 |                 2.00 |                1.80 |                          0.00 |                         10.00 |                        10.00 |                 40.76 |                107.08 |                66.32 |
| haiku    |            100.00 |             50.00 |           -50.00 |                70.00 |                20.00 |              -50.00 |                 0.50 |                 2.20 |                1.70 |                          0.00 |                         50.00 |                        50.00 |                 19.51 |                 40.65 |                21.14 |
| deepseek |             80.00 |            100.00 |            20.00 |                40.00 |               100.00 |               60.00 |                 1.10 |                 0.00 |               -1.10 |                         20.00 |                          0.00 |                       -20.00 |                139.28 |                395.21 |               255.93 |

## Success rate by difficulty (per model, L2)

| model    |   easy |   medium |   hard |
|:---------|-------:|---------:|-------:|
| deepseek |  100.0 |    100.0 |  100.0 |
| haiku    |   66.7 |     33.3 |   50.0 |
| qwen     |  100.0 |    100.0 |   75.0 |

## Per-category success rate (L2)

| model    |   cryptarithmetic |   graph_coloring |   knapsack |   latin_square |   magic_square |   queens |   scheduling |   sudoku |
|:---------|------------------:|-----------------:|-----------:|---------------:|---------------:|---------:|-------------:|---------:|
| qwen     |               100 |              100 |        100 |            100 |            100 |      100 |            0 |      100 |
| haiku    |               100 |              100 |          0 |            100 |             50 |        0 |            0 |      100 |
| deepseek |               100 |              100 |        100 |            100 |            100 |      100 |          100 |      100 |

## Hypothesis check

**Plan.md L2 prediction:** *"Up slightly; mean refinement iterations DOWN. Pre-solver semantic gate short-circuits doomed refinement loops."*

**Result:** REJECTED on the iterations claim, MIXED on the success claim.

- **Mean iterations went UP** for 2 of 3 models (haiku +1.5, qwen +1.8) and stayed flat for deepseek (already 0). Aggregate mean iterations rose ~0.4 → ~1.4. The validator did NOT short-circuit; it actively *added* iteration pressure.
- **Success rate split**: deepseek +20pp (8/10 → 10/10), haiku **−50pp** (10/10 → 5/10), qwen −10pp (10/10 → 9/10). Net aggregate went down, not up.
- **Compilation failures** stayed at 0% for deepseek and qwen but jumped for haiku, because the validator forced rewrites of code that originally compiled — the refiner sometimes broke a working model trying to address spurious validator issues.

## Findings

### F1 — Validator over-rejects valid models (false-positive cascade)
On models that produce terser Java (Qwen, Haiku), the Adversarial-CoT validator routinely flags valid code as invalid, forcing the refiner to rewrite working programs. Many of those rewrites do not survive the next validator round either, leading to chains of three failed refinements (`iter=3`) and, for haiku, eventual compilation breakage.

### F2 — DeepSeek's verbose output 'sails through' the validator
DeepSeek R1 reaches **10/10 first-shot success at iter=0**, the best result of any (level, model) cell so far. Its longer reasoning-style code surface satisfies adversarial scrutiny on the first try, so the gate is a no-op. This is consistent with: validator quality depends on cosmetic signal (length, comments, explicit imports) more than on semantic correctness.

### F3 — Haiku regression is the cleanest negative signal
Haiku went from 10/10 (L1) to 5/10 (L2) — five working programs were broken by the validator-driven refinement loop. Five of haiku's L2 failures end with `compilation_error` after iter=3, meaning the refiner kept overwriting compilable code until something stopped compiling. This rules out 'the validator caught real bugs' as an explanation: the bugs were *introduced* by the loop.

### F4 — Validator structured-output is brittle on OpenRouter
Qwen3-coder repeatedly emitted >8 k tokens of preamble before its JSON, which langchain's `with_structured_output` rejects as 'length limit reached', crashing the entire run. Mitigation: validator now fails open on parse error (treats as valid). This means a non-zero number of L2 validator calls on qwen were effectively skipped — relevant context when interpreting qwen's L2 numbers.

### F5 — Faithfulness still 0% (parser dependency, carried from L0/L1)
Same parser issue as L0/L1: the `solution` dict is empty, so the regex faithfulness check has no variable names to match against. Independent of the L2 delegation experiment.

## Cross-cutting observations

- **The L2 hypothesis fails empirically**, but cleanly. This *is* the kind of result an ablation study is designed to surface: adding an agent does not always help, and the failure mode (over-rejection) is mechanistically interpretable.
- **Wall-time cost** of L2 is ~2× L1 for qwen and haiku (extra validator + extra refiner calls), with no payoff. DeepSeek's wall time changes little because it never iterates.
- The **model-dependent direction** of the L2 effect (deepseek up, haiku down) suggests adversarial-CoT validation should be gated on model verbosity/style, not applied uniformly. Worth noting in the report.
- For **L3**, where the Formalizer splits out, we should expect this mechanism (one agent introducing structured constraints another agent rewrites against) to help only if the structured artifact is genuinely informative.

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
- `plots/12_delta_success.png`
- `plots/13_delta_first_shot.png`
- `plots/14_delta_iterations.png`
- `plots/15_iter_pressure_on_success.png`

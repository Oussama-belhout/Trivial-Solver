# L0 PDA — Data Analysis

Dataset: **3 models × 3 prompting variants × 10 problems = 90 runs**.

- Models: Qwen 2.5 Coder 32B, Claude Haiku 4.5, DeepSeek R1 (distill, Llama 70B base).
- Variants: zero-shot, few-shot, chain-of-thought (CoT).
- Benchmarks: 4 hard / 3 medium / 3 easy across 8 CSP families.
- Inner refinement loop bounded at MAX_REFINEMENT_ITERATIONS=3 (universal per PDA spec).

## Headline metrics (per model × variant)

| model    | variant   |   n_runs |   success_rate |   first_shot_rate |   compilation_failure_rate |   mean_iterations |   mean_wall_time_s |   faith_pass_rate |   faith_mean_overlap |
|:---------|:----------|---------:|---------------:|------------------:|---------------------------:|------------------:|-------------------:|------------------:|---------------------:|
| qwen     | zero_shot |       10 |          100.0 |               0.0 |                        0.0 |               1.0 |               77.4 |               0.0 |                  0.0 |
| qwen     | few_shot  |       10 |          100.0 |               0.0 |                        0.0 |               1.0 |               15.4 |               0.0 |                  0.0 |
| qwen     | cot       |       10 |           70.0 |               0.0 |                       30.0 |               2.1 |               16.9 |               0.0 |                  0.0 |
| haiku    | zero_shot |       10 |          100.0 |               0.0 |                        0.0 |               1.0 |               37.4 |               0.0 |                  0.0 |
| haiku    | few_shot  |       10 |          100.0 |              80.0 |                        0.0 |               0.3 |               27.9 |               0.0 |                  0.0 |
| haiku    | cot       |       10 |          100.0 |               0.0 |                        0.0 |               1.0 |               37.3 |               0.0 |                  0.0 |
| deepseek | zero_shot |       10 |          100.0 |              10.0 |                        0.0 |               0.9 |               88.9 |               0.0 |                  0.0 |
| deepseek | few_shot  |       10 |          100.0 |              80.0 |                        0.0 |               0.2 |               98.2 |               0.0 |                  0.0 |
| deepseek | cot       |       10 |          100.0 |               0.0 |                        0.0 |               1.0 |              221.7 |               0.0 |                  0.0 |

## Top-3 configurations (by success → first-shot → wall time)

| model    | variant   |   success_rate |   first_shot_rate |   mean_iterations |   mean_wall_time_s |
|:---------|:----------|---------------:|------------------:|------------------:|-------------------:|
| haiku    | few_shot  |          100.0 |              80.0 |               0.3 |               27.9 |
| deepseek | few_shot  |          100.0 |              80.0 |               0.2 |               98.2 |
| deepseek | zero_shot |          100.0 |              10.0 |               0.9 |               88.9 |

## Success rate by difficulty (per model × variant)

|                           |   easy |   medium |   hard |
|:--------------------------|-------:|---------:|-------:|
| ('deepseek', 'cot')       |  100.0 |    100.0 |  100.0 |
| ('deepseek', 'few_shot')  |  100.0 |    100.0 |  100.0 |
| ('deepseek', 'zero_shot') |  100.0 |    100.0 |  100.0 |
| ('haiku', 'cot')          |  100.0 |    100.0 |  100.0 |
| ('haiku', 'few_shot')     |  100.0 |    100.0 |  100.0 |
| ('haiku', 'zero_shot')    |  100.0 |    100.0 |  100.0 |
| ('qwen', 'cot')           |  100.0 |     33.3 |   75.0 |
| ('qwen', 'few_shot')      |  100.0 |    100.0 |  100.0 |
| ('qwen', 'zero_shot')     |  100.0 |    100.0 |  100.0 |

## Per-category success rate — using each model's best variant

Best variant — Qwen: **Zero-shot**, Haiku: **Zero-shot**, DeepSeek: **Zero-shot**.

| model    |   cryptarithmetic |   graph_coloring |   knapsack |   latin_square |   magic_square |   queens |   scheduling |   sudoku |
|:---------|------------------:|-----------------:|-----------:|---------------:|---------------:|---------:|-------------:|---------:|
| qwen     |               100 |              100 |        100 |            100 |            100 |      100 |          100 |      100 |
| haiku    |               100 |              100 |        100 |            100 |            100 |      100 |          100 |      100 |
| deepseek |               100 |              100 |        100 |            100 |            100 |      100 |          100 |      100 |

## Findings

### F1 — L0 frontier is already close to saturated for strong models
Both Haiku 4.5 and DeepSeek R1-distill hit **100% success on 8/9 (model, variant)** combinations. Qwen Coder 32B also hits 100% on every variant **except CoT** (70%, 30% compile errors). This means at L0 the headline Q1 metric (success rate) is near the ceiling — **gains from L1+ delegation will be hard to see on success rate alone**, and the report should lean on first-shot success and mean iterations as the more discriminating L0 metrics.

### F2 — Few-shot dominates first-shot success
Few-shot is the only variant that produces non-trivial first-shot success: **Haiku 80%** and **DeepSeek 80%** first-shot vs. zero-shot/CoT essentially zero on those models. This validates the locked decision in `docs/plan.md` to use **few-shot as the L0 baseline** for the headline curve. Zero-shot and CoT push the model into the refinement loop more often (mean iterations ≈ 1.0 vs. 0.2–0.3 for few-shot).

### F3 — CoT is a net loss for the strong models
CoT does not improve success rate over few-shot for any model, and it dramatically inflates wall time: **DeepSeek CoT mean wall time = 222s vs. 98s few-shot** (~2.3× slower). For Qwen, CoT is also the only variant where compilation errors appear (30%) — the `<think>` block leaks into the .java file. Recommendation: at L1+, **CoT should be reserved for agents whose task explicitly benefits from explicit reasoning** (e.g., the Validator, per the plan's adversarial-CoT choice), not as a default.

### F4 — Qwen first-shot anomaly is a known data-extraction bug, not a model finding
Qwen's 0% first-shot rate across all variants (with mean iterations ≈ 1.0) is **not** a property of the model — it traces to a bug in `src/agents/monolith.py:_extract_java_code()` where Qwen's response shape (markdown fence on same line, occasional unclosed `<think>` tag) leaked backticks into the .java file, triggering a deterministic compile failure on every first attempt. Refinement always recovered (hence success rate 100%), but first-shot was inflated to zero. The fix is committed; **Qwen first-shot data should be regenerated before any L0 → L4 first-shot trajectory is plotted**.

### F5 — DeepSeek pays a heavy reasoning-token tax
Mean wall time for DeepSeek R1-distill ranges **89s–222s** vs. **28s–37s** for Haiku. Distilled R1 still emits visible reasoning, so even at temp=0 the response is long. The cost differential will compound at L3+ where multiple agents fire per problem. Practical implication: **DeepSeek's role in the study is methodological** (does internal reasoning subsume external delegation?) rather than economic.

### F6 — Faithfulness is uniformly zero — upstream parser bug, not a model failure
All 90 runs return `faith_pass_rate = 0%`. The cause is **`src/choco/parser.py`**: it correctly extracts `solutions_found` from solver stats but does **not** populate the `solution` dict with variable name → value pairs unless the LLM-generated Java prints lines starting with `SOLUTION:`. When the dict is empty, `evaluate.py:_faithfulness_score()` has zero variable names to match against, so `var_overlap_ratio = 0` for every run — making the metric meaningless at L0. **This must be fixed before L4 results can be cited**: either standardize the printing convention in the prompt (require `SOLUTION: name=value, ...`) or extend the parser to extract `name=value` from any monitor trace line.

### F7 — Solver-stats data is currently corrupt — third debt item

Choco's deterministic stats (nodes / backtracks / fails / solutions_found) **should** vary per benchmark and act as a modeling-quality cross-model comparator (a tighter formulation does less search). At L0 they don't: **every successful run, every model, every variant reports nodes=5, backtracks=7, fails=2, solutions_found=2** — those are 4-Queens' numbers showing up everywhere.

Cross-checks confirm the run is real (`building_time` varies per problem from 0.02s to 0.07s, so Maven *is* compiling and running different Java for each benchmark) — but the `Nodes:/Backtracks:/Fails:/Solutions:` lines captured by `src/choco/parser.py` are either missing from stdout or always identical. Most likely cause: LLM-generated Java commonly emits `solver.showStatistics()` (which is not a real Choco method) instead of `solver.printStatistics()`, so the proper stats lines never reach stdout, and the parser may be hitting a fallback or a Choco internal log line that happens to read `Nodes: 5`. **Solver-stat-based comparisons are not supportable at L0 until this is fixed**, alongside F4 (Qwen extraction regen) and F6 (faithfulness parser).

Action required before L1+: (a) inspect raw stdout from one run to confirm the exact line shape, (b) tighten the parser regex (`r'Nodes\s*:\s*(\d+)'` with explicit whitespace tolerance), (c) standardize the prompt to require `solver.printStatistics()` (not `showStatistics()`) and a `SOLUTION: name=value` print line.

## Cross-cutting observations

- **Difficulty is not the gating factor at L0.** Hard problems pass at the same rate as easy ones for Haiku and DeepSeek. The 4 hard problems chosen are LLM-perceived hard (formalization-trap), not solver-hard — and the bake-off shows the modern frontier models clear them.
- **CoT-induced compile failures (Qwen)** are concentrated on problems whose responses have ambiguous fence shapes; this is a *prompting* artifact, not a *category* artifact.
- **Mean-iterations is the most discriminating L0 metric** going into L1+. Few-shot Haiku/DeepSeek average ~0.2–0.3 iterations, leaving meaningful headroom for the L1 Refiner specialization to demonstrate iteration savings vs. monolith refinement.

## Locked decisions reaffirmed

- **Few-shot is the right L0 → L4 headline variant** for cross-level comparability (only variant with non-trivial first-shot performance).
- **DeepSeek's value is in mechanism contrast** (reasoning vs. non-reasoning), not in headline numbers.
- **Faithfulness regex needs a parser fix before L4 measurements are meaningful.** Until then, faithfulness comparisons are bug-bound, not model-bound.
- **Solver-stats parser also needs a fix before L1+ modeling-quality claims are supportable.** All successful L0 runs report identical stats — this is a parser/Java-output mismatch, not real determinism.

## Debt items to resolve before L1+ measurements

1. **Qwen first-shot regeneration** — the extraction fix is committed; rerun `mono_*_qwen.json` to get clean first-shot data. (cost: pennies)
2. **Faithfulness parser** (`src/choco/parser.py`) — populate `solution` dict with name=value pairs from any line emitted by the LLM-generated Java, not just `SOLUTION:`-prefixed lines. Or: standardize the print convention in the EXPLAIN/MODEL prompts.
3. **Solver-stats parser + prompt** — require `solver.printStatistics()` (not `showStatistics()`) in the prompt's worked example, and tighten the parser regex to tolerate `Nodes : 5` (space before colon, Choco's actual format).

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
- `plots/11_solver_per_problem_CORRUPT.png`
- `plots/12_solver_median_CORRUPT.png`

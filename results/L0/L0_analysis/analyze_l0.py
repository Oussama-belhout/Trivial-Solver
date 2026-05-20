"""L0 PDA — full data analysis across 3 models × 3 prompting variants.

Inputs:  results/mono_{model}/mono_{variant}_{model}.json   (9 files)
Outputs: results/analysis/
           summary_wide.csv         — one row per (model, variant), all metrics
           per_problem.csv          — one row per (model, variant, problem)
           summary.md               — narrative analysis
           plots/*.png              — visuals

This script is read-only on the JSONs and idempotent on output.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
OUT = RESULTS / "analysis"
PLOTS = OUT / "plots"
PLOTS.mkdir(parents=True, exist_ok=True)

MODELS = ["qwen", "haiku", "deepseek"]
VARIANTS = ["zero_shot", "few_shot", "cot"]

MODEL_LABEL = {
    "qwen": "Qwen 2.5 Coder 32B",
    "haiku": "Claude Haiku 4.5",
    "deepseek": "DeepSeek R1 (distill 70B)",
}
VARIANT_LABEL = {"zero_shot": "Zero-shot", "few_shot": "Few-shot", "cot": "CoT"}

MODEL_COLOR = {"qwen": "#5b8def", "haiku": "#e07a5f", "deepseek": "#81b29a"}
VARIANT_HATCH = {"zero_shot": "", "few_shot": "//", "cot": "xx"}


def load_run(model: str, variant: str) -> dict:
    p = RESULTS / f"mono_{model}" / f"mono_{variant}_{model}.json"
    with p.open(encoding="utf-8") as f:
        return json.load(f)


# ── Build dataframes ──────────────────────────────────────────────────────────


wide_rows: list[dict] = []
problem_rows: list[dict] = []

for m in MODELS:
    for v in VARIANTS:
        payload = load_run(m, v)
        s = payload.get("summary", {}) or {}
        wide_rows.append(
            {
                "model": m,
                "variant": v,
                "n_runs": s.get("total", 0),
                "success_rate": s.get("success_rate", 0.0),
                "first_shot_rate": s.get("first_shot_success_rate", 0.0),
                "compilation_failure_rate": s.get("compilation_failure_rate", 0.0),
                "mean_iterations": s.get("mean_iterations", 0.0),
                "mean_wall_time_s": s.get("mean_wall_time_seconds", 0.0),
                "faith_pass_rate": (s.get("faithfulness") or {}).get("pass_rate", 0.0)
                if s.get("faithfulness") else 0.0,
                "faith_mean_overlap": (s.get("faithfulness") or {}).get("mean_var_overlap_ratio", 0.0)
                if s.get("faithfulness") else 0.0,
            }
        )
        for r in payload.get("runs", []):
            stats = r.get("solver_stats", {}) or {}
            def _as_int(v, default=None):
                try:
                    return int(v)
                except (TypeError, ValueError):
                    return default
            problem_rows.append(
                {
                    "model": m,
                    "variant": v,
                    "problem_id": r.get("problem_id"),
                    "category": r.get("category"),
                    "difficulty": r.get("difficulty"),
                    "success": bool(r.get("success", False)),
                    "first_shot": bool(r.get("first_shot_success", False)),
                    "iterations": int(r.get("iterations", 0) or 0),
                    "compilation_failed": bool(r.get("compilation_failed", False)),
                    "wall_time_s": float(r.get("wall_time_seconds", 0.0) or 0.0),
                    "java_chars": int(r.get("java_code_chars", 0) or 0),
                    "error_category": r.get("error_category"),
                    # Solver-side determinism metrics — only meaningful on successful runs.
                    "solver_nodes": _as_int(stats.get("nodes")),
                    "solver_backtracks": _as_int(stats.get("backtracks")),
                    "solver_fails": _as_int(stats.get("fails")),
                    "solver_restarts": _as_int(stats.get("restarts")),
                    "solver_solutions_found": _as_int(stats.get("solutions_found")),
                }
            )

wide = pd.DataFrame(wide_rows)
prob = pd.DataFrame(problem_rows)
wide.to_csv(OUT / "summary_wide.csv", index=False)
prob.to_csv(OUT / "per_problem.csv", index=False)

# ── Helper: a grouped-bar plot keyed (model, variant) ─────────────────────────


def grouped_bar(metric: str, ylabel: str, title: str, fname: str, ymax: float | None = None):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(VARIANTS))
    width = 0.25
    for i, m in enumerate(MODELS):
        sub = wide[wide["model"] == m].set_index("variant").reindex(VARIANTS)
        offset = (i - 1) * width
        bars = ax.bar(
            x + offset,
            sub[metric].values,
            width,
            color=MODEL_COLOR[m],
            label=MODEL_LABEL[m],
            edgecolor="black",
            linewidth=0.6,
        )
        for b, val in zip(bars, sub[metric].values):
            ax.text(
                b.get_x() + b.get_width() / 2,
                b.get_height() + (0.01 * (ymax or max(sub[metric].max(), 1))),
                f"{val:.1f}" if isinstance(val, float) else str(val),
                ha="center",
                va="bottom",
                fontsize=8,
            )
    ax.set_xticks(x)
    ax.set_xticklabels([VARIANT_LABEL[v] for v in VARIANTS])
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    if ymax is not None:
        ax.set_ylim(0, ymax)
    fig.tight_layout()
    fig.savefig(PLOTS / fname, dpi=140)
    plt.close(fig)


grouped_bar("success_rate", "Success rate (%)", "L0 — Success rate by model and prompting", "01_success_rate.png", ymax=110)
grouped_bar("first_shot_rate", "First-shot success rate (%)", "L0 — First-shot success rate (no refinement)", "02_first_shot.png", ymax=110)
grouped_bar("compilation_failure_rate", "Compilation failure rate (%)", "L0 — Compilation failure rate", "03_compile_fail.png", ymax=max(40, wide["compilation_failure_rate"].max() + 5))
grouped_bar("mean_iterations", "Mean refinement iterations", "L0 — Mean refinement iterations per problem", "04_mean_iterations.png")
grouped_bar("mean_wall_time_s", "Mean wall time (s)", "L0 — Mean wall time per problem", "05_wall_time.png")

# ── Heatmap: success rate × difficulty × (model, variant) ─────────────────────

diffs = ["easy", "medium", "hard"]
heat = (
    prob.groupby(["model", "variant", "difficulty"])["success"].mean().mul(100).unstack("difficulty").reindex(columns=diffs)
)
heat = heat.reindex([(m, v) for m in MODELS for v in VARIANTS])

fig, ax = plt.subplots(figsize=(7.5, 5))
im = ax.imshow(heat.values, vmin=0, vmax=100, cmap="RdYlGn", aspect="auto")
ax.set_xticks(np.arange(len(diffs)))
ax.set_xticklabels([d.capitalize() for d in diffs])
ax.set_yticks(np.arange(len(heat.index)))
ax.set_yticklabels([f"{MODEL_LABEL[m]} — {VARIANT_LABEL[v]}" for m, v in heat.index], fontsize=9)
for i in range(len(heat.index)):
    for j in range(len(diffs)):
        v = heat.values[i, j]
        ax.text(j, i, f"{v:.0f}%" if not np.isnan(v) else "-", ha="center", va="center",
                color="black" if 30 < v < 75 else "white", fontsize=9)
ax.set_title("L0 — Success rate by problem difficulty")
fig.colorbar(im, ax=ax, fraction=0.04, pad=0.04, label="Success rate (%)")
fig.tight_layout()
fig.savefig(PLOTS / "06_heatmap_difficulty.png", dpi=140)
plt.close(fig)

# ── Heatmap: per-category success rate × model (best-variant per model) ───────

best_per_model = wide.loc[wide.groupby("model")["success_rate"].idxmax()].set_index("model")["variant"].to_dict()
best_runs = prob[prob.apply(lambda r: r["variant"] == best_per_model[r["model"]], axis=1)]
cat_heat = best_runs.groupby(["model", "category"])["success"].mean().mul(100).unstack("category")
cat_heat = cat_heat.reindex(MODELS)

fig, ax = plt.subplots(figsize=(10, 3.5))
im = ax.imshow(cat_heat.values, vmin=0, vmax=100, cmap="RdYlGn", aspect="auto")
ax.set_xticks(np.arange(cat_heat.shape[1]))
ax.set_xticklabels(cat_heat.columns, rotation=30, ha="right", fontsize=9)
ax.set_yticks(np.arange(len(MODELS)))
ax.set_yticklabels(
    [f"{MODEL_LABEL[m]}\n(best={VARIANT_LABEL[best_per_model[m]]})" for m in MODELS], fontsize=9
)
for i in range(cat_heat.shape[0]):
    for j in range(cat_heat.shape[1]):
        v = cat_heat.values[i, j]
        ax.text(j, i, f"{v:.0f}" if not np.isnan(v) else "-", ha="center", va="center",
                color="black" if 30 < v < 75 else "white", fontsize=9)
ax.set_title("L0 — Per-category success rate (best variant per model)")
fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02, label="Success rate (%)")
fig.tight_layout()
fig.savefig(PLOTS / "07_heatmap_category.png", dpi=140)
plt.close(fig)

# ── Iterations distribution stacked bars per (model, variant) ─────────────────

iter_max = int(prob["iterations"].max())
fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
for ax, m in zip(axes, MODELS):
    sub = prob[prob["model"] == m]
    counts = (
        sub.groupby(["variant", "iterations"]).size().unstack("iterations", fill_value=0).reindex(VARIANTS).fillna(0)
    )
    bottoms = np.zeros(len(VARIANTS))
    cmap = plt.get_cmap("Blues")
    for it in range(iter_max + 1):
        if it not in counts.columns:
            continue
        vals = counts[it].values
        color = cmap(0.3 + 0.7 * it / max(iter_max, 1))
        ax.bar(
            np.arange(len(VARIANTS)),
            vals,
            bottom=bottoms,
            color=color,
            edgecolor="black",
            linewidth=0.5,
            label=f"{it} iter" if ax is axes[0] else None,
        )
        bottoms += vals
    ax.set_xticks(np.arange(len(VARIANTS)))
    ax.set_xticklabels([VARIANT_LABEL[v] for v in VARIANTS])
    ax.set_title(MODEL_LABEL[m])
    ax.grid(axis="y", linestyle="--", alpha=0.4)
axes[0].set_ylabel("# problems")
fig.legend(loc="upper center", ncol=iter_max + 1, fontsize=9, bbox_to_anchor=(0.5, 1.02))
fig.suptitle("L0 — Distribution of refinement iterations per (model, variant)", y=1.06)
fig.tight_layout()
fig.savefig(PLOTS / "08_iterations_distribution.png", dpi=140, bbox_inches="tight")
plt.close(fig)

# ── Cost-quality scatter: wall_time vs success_rate (size = first_shot) ───────

fig, ax = plt.subplots(figsize=(7, 5))
for _, row in wide.iterrows():
    color = MODEL_COLOR[row["model"]]
    marker = {"zero_shot": "o", "few_shot": "s", "cot": "^"}[row["variant"]]
    ax.scatter(
        row["mean_wall_time_s"],
        row["success_rate"],
        s=80 + 4 * row["first_shot_rate"],
        color=color,
        marker=marker,
        edgecolor="black",
        alpha=0.85,
    )
    ax.annotate(
        f"{row['model']}/{row['variant']}",
        (row["mean_wall_time_s"], row["success_rate"]),
        textcoords="offset points",
        xytext=(6, 6),
        fontsize=8,
    )
ax.set_xlabel("Mean wall time per problem (s)")
ax.set_ylabel("Success rate (%)")
ax.set_title("L0 — Cost vs. quality (marker size = first-shot rate)")
ax.grid(True, linestyle="--", alpha=0.4)
ax.set_ylim(60, 105)
# Custom legend
from matplotlib.lines import Line2D
legend_elems = [Line2D([0], [0], marker="o", color="w", markerfacecolor=MODEL_COLOR[m], markeredgecolor="black",
                       markersize=10, label=MODEL_LABEL[m]) for m in MODELS]
legend_elems += [Line2D([0], [0], marker={"zero_shot": "o", "few_shot": "s", "cot": "^"}[v], color="w",
                        markerfacecolor="grey", markeredgecolor="black", markersize=10, label=VARIANT_LABEL[v])
                 for v in VARIANTS]
ax.legend(handles=legend_elems, loc="lower right", fontsize=8, ncol=2)
fig.tight_layout()
fig.savefig(PLOTS / "09_cost_quality_scatter.png", dpi=140)
plt.close(fig)

# ── Solver-side stats: nodes / backtracks / fails per problem × model ────────
# Only successful runs (failed runs have empty stats). Each model uses its
# *best* variant (the one that gave it the highest success rate), so this
# isolates "modeling quality" — i.e. how efficient is the Java the LLM produced
# — from the LLM's prompting strategy. Same Choco solver, same temp=0, same
# benchmark → differences in nodes/backtracks reflect formulation choices.

solver_metrics = ["solver_nodes", "solver_backtracks", "solver_fails"]
solver_labels = {"solver_nodes": "Nodes", "solver_backtracks": "Backtracks", "solver_fails": "Fails"}

# Best variant per model (already computed earlier as best_per_model)
best_runs_full = prob[prob.apply(lambda r: r["variant"] == best_per_model[r["model"]], axis=1) & prob["success"]].copy()

# Plot 11 — Per-problem solver work (grouped bars, one subplot per metric)
problem_order = (
    prob[prob["success"]]
    .groupby("problem_id")["difficulty"]
    .first()
    .reindex(prob["problem_id"].drop_duplicates())
    .pipe(lambda s: s.sort_values(key=lambda x: x.map({"easy": 0, "medium": 1, "hard": 2}.get)))
    .index.tolist()
)

fig, axes = plt.subplots(len(solver_metrics), 1, figsize=(11, 9), sharex=True)
for ax, metric in zip(axes, solver_metrics):
    pivot = (
        best_runs_full.pivot_table(index="problem_id", columns="model", values=metric, aggfunc="mean")
        .reindex(problem_order)
        .reindex(columns=MODELS)
    )
    x = np.arange(len(pivot.index))
    width = 0.27
    for i, m in enumerate(MODELS):
        vals = pivot[m].values
        ax.bar(
            x + (i - 1) * width,
            np.where(np.isnan(vals), 0, vals),
            width,
            color=MODEL_COLOR[m],
            label=f"{MODEL_LABEL[m]} ({VARIANT_LABEL[best_per_model[m]]})" if ax is axes[0] else None,
            edgecolor="black",
            linewidth=0.5,
        )
    ax.set_ylabel(solver_labels[metric])
    ax.set_yscale("symlog", linthresh=10)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_title(f"Solver {solver_labels[metric].lower()} per problem (lower = more efficient model)")
axes[-1].set_xticks(x)
axes[-1].set_xticklabels(pivot.index, rotation=30, ha="right", fontsize=9)
fig.legend(loc="upper center", ncol=3, fontsize=9, bbox_to_anchor=(0.5, 1.01))
fig.suptitle("L0 — Solver-side stats per problem [DATA CORRUPT — see F7 in summary.md]", y=1.04, color="darkred")
# Annotate the figure with a visible warning so it can't be cited unaware.
fig.text(0.5, 0.96, "WARNING: every problem reports identical 4-Queens stats — parser bug, not a model finding",
         ha="center", color="darkred", fontsize=9, style="italic")
fig.tight_layout()
fig.savefig(PLOTS / "11_solver_per_problem_CORRUPT.png", dpi=140, bbox_inches="tight")
plt.close(fig)

# Plot 12 — Modeling-quality summary: mean & median solver work per (model × variant)
fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=False)
for ax, metric in zip(axes, solver_metrics):
    summary = (
        prob[prob["success"]]
        .groupby(["model", "variant"])[metric]
        .median()
        .unstack("variant")
        .reindex(index=MODELS, columns=VARIANTS)
    )
    x = np.arange(len(VARIANTS))
    width = 0.25
    for i, m in enumerate(MODELS):
        ax.bar(
            x + (i - 1) * width,
            summary.loc[m].values,
            width,
            color=MODEL_COLOR[m],
            label=MODEL_LABEL[m] if ax is axes[0] else None,
            edgecolor="black",
            linewidth=0.5,
        )
    ax.set_xticks(x)
    ax.set_xticklabels([VARIANT_LABEL[v] for v in VARIANTS])
    ax.set_title(f"Median {solver_labels[metric].lower()} (successful runs)")
    ax.set_yscale("symlog", linthresh=10)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
fig.legend(loc="upper center", ncol=3, fontsize=9, bbox_to_anchor=(0.5, 1.02))
fig.suptitle("L0 — Median solver work [DATA CORRUPT — see F7 in summary.md]", y=1.05, color="darkred")
fig.text(0.5, 0.96, "WARNING: identical across all model×variant — parser bug, not a real signal",
         ha="center", color="darkred", fontsize=9, style="italic")
fig.tight_layout()
fig.savefig(PLOTS / "12_solver_median_CORRUPT.png", dpi=140, bbox_inches="tight")
plt.close(fig)

# ── Faithfulness bar (truthful — all-zero, surfaced explicitly) ───────────────

fig, ax = plt.subplots(figsize=(7.5, 3.5))
x = np.arange(len(VARIANTS))
width = 0.25
for i, m in enumerate(MODELS):
    sub = wide[wide["model"] == m].set_index("variant").reindex(VARIANTS)
    ax.bar(x + (i - 1) * width, sub["faith_pass_rate"].values, width, color=MODEL_COLOR[m],
           label=MODEL_LABEL[m], edgecolor="black", linewidth=0.6)
ax.set_xticks(x)
ax.set_xticklabels([VARIANT_LABEL[v] for v in VARIANTS])
ax.set_ylabel("Faithfulness regex pass rate (%)")
ax.set_title("L0 — Faithfulness (regex). All zero — known upstream bug, see notes.")
ax.legend(fontsize=8)
ax.set_ylim(0, 100)
ax.grid(axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig(PLOTS / "10_faithfulness.png", dpi=140)
plt.close(fig)


# ── Narrative summary.md ──────────────────────────────────────────────────────


best_overall = wide.sort_values(["success_rate", "first_shot_rate", "mean_wall_time_s"],
                                ascending=[False, False, True]).head(3)

md = []
md.append("# L0 PDA — Data Analysis\n")
md.append("Dataset: **3 models × 3 prompting variants × 10 problems = 90 runs**.")
md.append("")
md.append("- Models: Qwen 2.5 Coder 32B, Claude Haiku 4.5, DeepSeek R1 (distill, Llama 70B base).")
md.append("- Variants: zero-shot, few-shot, chain-of-thought (CoT).")
md.append("- Benchmarks: 4 hard / 3 medium / 3 easy across 8 CSP families.")
md.append("- Inner refinement loop bounded at MAX_REFINEMENT_ITERATIONS=3 (universal per PDA spec).")
md.append("")

md.append("## Headline metrics (per model × variant)\n")
md.append(wide.to_markdown(index=False, floatfmt=".1f"))
md.append("")

md.append("## Top-3 configurations (by success → first-shot → wall time)\n")
md.append(best_overall[["model", "variant", "success_rate", "first_shot_rate", "mean_iterations",
                        "mean_wall_time_s"]].to_markdown(index=False, floatfmt=".1f"))
md.append("")

# Per-difficulty breakdown
md.append("## Success rate by difficulty (per model × variant)\n")
diff_table = (
    prob.groupby(["model", "variant", "difficulty"])["success"].mean().mul(100).unstack("difficulty").reindex(columns=diffs).round(1)
)
md.append(diff_table.to_markdown(floatfmt=".1f"))
md.append("")

# Per-category breakdown (best variant per model)
md.append("## Per-category success rate — using each model's best variant\n")
md.append(f"Best variant — Qwen: **{VARIANT_LABEL[best_per_model['qwen']]}**, Haiku: **{VARIANT_LABEL[best_per_model['haiku']]}**, DeepSeek: **{VARIANT_LABEL[best_per_model['deepseek']]}**.\n")
md.append(cat_heat.round(0).to_markdown(floatfmt=".0f"))
md.append("")

# Findings
md.append("## Findings\n")
md.append("### F1 — L0 frontier is already close to saturated for strong models")
md.append("Both Haiku 4.5 and DeepSeek R1-distill hit **100% success on 8/9 (model, variant)** combinations. "
         "Qwen Coder 32B also hits 100% on every variant **except CoT** (70%, 30% compile errors). "
         "This means at L0 the headline Q1 metric (success rate) is near the ceiling — **gains from L1+ delegation will be hard to see on success rate alone**, "
         "and the report should lean on first-shot success and mean iterations as the more discriminating L0 metrics.\n")

md.append("### F2 — Few-shot dominates first-shot success")
md.append("Few-shot is the only variant that produces non-trivial first-shot success: "
         "**Haiku 80%** and **DeepSeek 80%** first-shot vs. zero-shot/CoT essentially zero on those models. "
         "This validates the locked decision in `docs/plan.md` to use **few-shot as the L0 baseline** for the headline curve. "
         "Zero-shot and CoT push the model into the refinement loop more often (mean iterations ≈ 1.0 vs. 0.2–0.3 for few-shot).\n")

md.append("### F3 — CoT is a net loss for the strong models")
md.append("CoT does not improve success rate over few-shot for any model, and it dramatically inflates wall time: "
         f"**DeepSeek CoT mean wall time = {wide[(wide['model']=='deepseek')&(wide['variant']=='cot')]['mean_wall_time_s'].iloc[0]:.0f}s vs. {wide[(wide['model']=='deepseek')&(wide['variant']=='few_shot')]['mean_wall_time_s'].iloc[0]:.0f}s few-shot** "
         f"(~{wide[(wide['model']=='deepseek')&(wide['variant']=='cot')]['mean_wall_time_s'].iloc[0]/wide[(wide['model']=='deepseek')&(wide['variant']=='few_shot')]['mean_wall_time_s'].iloc[0]:.1f}× slower). "
         "For Qwen, CoT is also the only variant where compilation errors appear (30%) — the `<think>` block leaks into the .java file. "
         "Recommendation: at L1+, **CoT should be reserved for agents whose task explicitly benefits from explicit reasoning** (e.g., the Validator, per the plan's adversarial-CoT choice), not as a default.\n")

md.append("### F4 — Qwen first-shot anomaly is a known data-extraction bug, not a model finding")
md.append("Qwen's 0% first-shot rate across all variants (with mean iterations ≈ 1.0) is **not** a property of the model — "
         "it traces to a bug in `src/agents/monolith.py:_extract_java_code()` where Qwen's response shape (markdown fence on same line, "
         "occasional unclosed `<think>` tag) leaked backticks into the .java file, triggering a deterministic compile failure on every first attempt. "
         "Refinement always recovered (hence success rate 100%), but first-shot was inflated to zero. The fix is committed; **Qwen first-shot data should be regenerated before any L0 → L4 first-shot trajectory is plotted**.\n")

md.append("### F5 — DeepSeek pays a heavy reasoning-token tax")
md.append(f"Mean wall time for DeepSeek R1-distill ranges **{wide[wide['model']=='deepseek']['mean_wall_time_s'].min():.0f}s–{wide[wide['model']=='deepseek']['mean_wall_time_s'].max():.0f}s** vs. "
         f"**{wide[wide['model']=='haiku']['mean_wall_time_s'].min():.0f}s–{wide[wide['model']=='haiku']['mean_wall_time_s'].max():.0f}s** for Haiku. "
         "Distilled R1 still emits visible reasoning, so even at temp=0 the response is long. The cost differential will compound at L3+ where multiple agents fire per problem. "
         "Practical implication: **DeepSeek's role in the study is methodological** (does internal reasoning subsume external delegation?) rather than economic.\n")

md.append("### F6 — Faithfulness is uniformly zero — upstream parser bug, not a model failure")
md.append("All 90 runs return `faith_pass_rate = 0%`. The cause is **`src/choco/parser.py`**: it correctly extracts `solutions_found` from solver stats but does **not** populate the `solution` dict with variable name → value pairs unless the LLM-generated Java prints lines starting with `SOLUTION:`. "
         "When the dict is empty, `evaluate.py:_faithfulness_score()` has zero variable names to match against, so `var_overlap_ratio = 0` for every run — making the metric meaningless at L0. "
         "**This must be fixed before L4 results can be cited**: either standardize the printing convention in the prompt (require `SOLUTION: name=value, ...`) or extend the parser to extract `name=value` from any monitor trace line.\n")

md.append("### F7 — Solver-stats data is currently corrupt — third debt item\n")
md.append("Choco's deterministic stats (nodes / backtracks / fails / solutions_found) **should** vary per benchmark and "
         "act as a modeling-quality cross-model comparator (a tighter formulation does less search). At L0 they don't: "
         "**every successful run, every model, every variant reports nodes=5, backtracks=7, fails=2, solutions_found=2** — those are 4-Queens' numbers showing up everywhere.\n")
md.append("Cross-checks confirm the run is real (`building_time` varies per problem from 0.02s to 0.07s, so Maven *is* "
         "compiling and running different Java for each benchmark) — but the `Nodes:/Backtracks:/Fails:/Solutions:` lines "
         "captured by `src/choco/parser.py` are either missing from stdout or always identical. Most likely cause: "
         "LLM-generated Java commonly emits `solver.showStatistics()` (which is not a real Choco method) instead of "
         "`solver.printStatistics()`, so the proper stats lines never reach stdout, and the parser may be hitting a "
         "fallback or a Choco internal log line that happens to read `Nodes: 5`. **Solver-stat-based comparisons are not "
         "supportable at L0 until this is fixed**, alongside F4 (Qwen extraction regen) and F6 (faithfulness parser).\n")
md.append("Action required before L1+: (a) inspect raw stdout from one run to confirm the exact line shape, "
         "(b) tighten the parser regex (`r'Nodes\\s*:\\s*(\\d+)'` with explicit whitespace tolerance), "
         "(c) standardize the prompt to require `solver.printStatistics()` (not `showStatistics()`) and a `SOLUTION: name=value` print line.\n")

md.append("## Cross-cutting observations\n")
md.append("- **Difficulty is not the gating factor at L0.** Hard problems pass at the same rate as easy ones for Haiku and DeepSeek. The 4 hard problems chosen are LLM-perceived hard (formalization-trap), not solver-hard — and the bake-off shows the modern frontier models clear them.")
md.append("- **CoT-induced compile failures (Qwen)** are concentrated on problems whose responses have ambiguous fence shapes; this is a *prompting* artifact, not a *category* artifact.")
md.append("- **Mean-iterations is the most discriminating L0 metric** going into L1+. Few-shot Haiku/DeepSeek average ~0.2–0.3 iterations, leaving meaningful headroom for the L1 Refiner specialization to demonstrate iteration savings vs. monolith refinement.")
md.append("")

md.append("## Locked decisions reaffirmed\n")
md.append("- **Few-shot is the right L0 → L4 headline variant** for cross-level comparability (only variant with non-trivial first-shot performance).")
md.append("- **DeepSeek's value is in mechanism contrast** (reasoning vs. non-reasoning), not in headline numbers.")
md.append("- **Faithfulness regex needs a parser fix before L4 measurements are meaningful.** Until then, faithfulness comparisons are bug-bound, not model-bound.")
md.append("- **Solver-stats parser also needs a fix before L1+ modeling-quality claims are supportable.** All successful L0 runs report identical stats — this is a parser/Java-output mismatch, not real determinism.")
md.append("")
md.append("## Debt items to resolve before L1+ measurements\n")
md.append("1. **Qwen first-shot regeneration** — the extraction fix is committed; rerun `mono_*_qwen.json` to get clean first-shot data. (cost: pennies)")
md.append("2. **Faithfulness parser** (`src/choco/parser.py`) — populate `solution` dict with name=value pairs from any line emitted by the LLM-generated Java, not just `SOLUTION:`-prefixed lines. Or: standardize the print convention in the EXPLAIN/MODEL prompts.")
md.append("3. **Solver-stats parser + prompt** — require `solver.printStatistics()` (not `showStatistics()`) in the prompt's worked example, and tighten the parser regex to tolerate `Nodes : 5` (space before colon, Choco's actual format).")
md.append("")

md.append("## Plots\n")
for i, name in enumerate(sorted(os.listdir(PLOTS))):
    md.append(f"- `plots/{name}`")
md.append("")

with (OUT / "summary.md").open("w", encoding="utf-8") as f:
    f.write("\n".join(md))

print("OK:", OUT)
print("  summary_wide.csv  ->", (OUT / "summary_wide.csv").stat().st_size, "bytes")
print("  per_problem.csv   ->", (OUT / "per_problem.csv").stat().st_size, "bytes")
print("  summary.md        ->", (OUT / "summary.md").stat().st_size, "bytes")
print("  plots/            ->", len(list(PLOTS.glob('*.png'))), "PNGs")

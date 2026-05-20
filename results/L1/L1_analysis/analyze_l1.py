"""L1 PDA — full data analysis across 3 models × 1 prompting variant.

Inputs:  results/L1/duo_{model}.json   (3 files)
Outputs: results/L1/analysis/
           summary_wide.csv         — one row per model, all metrics
           per_problem.csv          — one row per (model, problem)
           summary.md               — narrative analysis
           plots/*.png              — visuals

This script is read-only on the JSONs and idempotent on output.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
LEVEL_DIR = BASE.parent
PLOTS = BASE / "plots"
PLOTS.mkdir(parents=True, exist_ok=True)

MODELS = ["qwen", "haiku", "deepseek"]
VARIANTS = ["few_shot"]

MODEL_LABEL = {
    "qwen": "Qwen 2.5 Coder 32B",
    "haiku": "Claude Haiku 4.5",
    "deepseek": "DeepSeek R1 (distill 70B)",
}
VARIANT_LABEL = {"few_shot": "Few-shot"}

MODEL_COLOR = {"qwen": "#5b8def", "haiku": "#e07a5f", "deepseek": "#81b29a"}


def load_run(model: str) -> dict:
    p = LEVEL_DIR / f"duo_{model}.json"
    with p.open(encoding="utf-8") as f:
        return json.load(f)


# ── Build dataframes ──────────────────────────────────────────────────────────

wide_rows: list[dict] = []
problem_rows: list[dict] = []

for m in MODELS:
    payload = load_run(m)
    s = payload.get("summary", {}) or {}
    prompting = payload.get("prompting", "few_shot")
    wide_rows.append(
        {
            "model": m,
            "variant": prompting,
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
                "variant": prompting,
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
                "solver_nodes": _as_int(stats.get("nodes")),
                "solver_backtracks": _as_int(stats.get("backtracks")),
                "solver_fails": _as_int(stats.get("fails")),
                "solver_restarts": _as_int(stats.get("restarts")),
                "solver_solutions_found": _as_int(stats.get("solutions_found")),
            }
        )

wide = pd.DataFrame(wide_rows)
prob = pd.DataFrame(problem_rows)
wide.to_csv(BASE / "summary_wide.csv", index=False)
prob.to_csv(BASE / "per_problem.csv", index=False)


# ── Helper: a grouped-bar plot keyed by model ─────────────────────────────────


def grouped_bar(metric: str, ylabel: str, title: str, fname: str, ymax: float | None = None):
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
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


grouped_bar("success_rate", "Success rate (%)", "L1 — Success rate by model", "01_success_rate.png", ymax=110)

grouped_bar(
    "first_shot_rate",
    "First-shot success rate (%)",
    "L1 — First-shot success rate (no refinement)",
    "02_first_shot.png",
    ymax=110,
)

grouped_bar(
    "compilation_failure_rate",
    "Compilation failure rate (%)",
    "L1 — Compilation failure rate",
    "03_compile_fail.png",
    ymax=max(40, wide["compilation_failure_rate"].max() + 5),
)

grouped_bar(
    "mean_iterations",
    "Mean refinement iterations",
    "L1 — Mean refinement iterations per problem",
    "04_mean_iterations.png",
)


grouped_bar(
    "mean_wall_time_s",
    "Mean wall time (s)",
    "L1 — Mean wall time per problem",
    "05_wall_time.png",
)


# ── Heatmap: success rate × difficulty × model ───────────────────────────────

diffs = ["easy", "medium", "hard"]
heat = (
    prob.groupby(["model", "difficulty"])["success"].mean().mul(100).unstack("difficulty").reindex(columns=diffs)
)
heat = heat.reindex(MODELS)

fig, ax = plt.subplots(figsize=(7.5, 3.4))
im = ax.imshow(heat.values, vmin=0, vmax=100, cmap="RdYlGn", aspect="auto")
ax.set_xticks(np.arange(len(diffs)))
ax.set_xticklabels([d.capitalize() for d in diffs])
ax.set_yticks(np.arange(len(heat.index)))
ax.set_yticklabels([MODEL_LABEL[m] for m in heat.index], fontsize=9)
for i in range(len(heat.index)):
    for j in range(len(diffs)):
        v = heat.values[i, j]
        ax.text(j, i, f"{v:.0f}%" if not np.isnan(v) else "-", ha="center", va="center",
                color="black" if 30 < v < 75 else "white", fontsize=9)
ax.set_title("L1 — Success rate by problem difficulty")
fig.colorbar(im, ax=ax, fraction=0.04, pad=0.04, label="Success rate (%)")
fig.tight_layout()
fig.savefig(PLOTS / "06_heatmap_difficulty.png", dpi=140)
plt.close(fig)


# ── Heatmap: per-category success rate × model ───────────────────────────────

cat_heat = prob.groupby(["model", "category"])["success"].mean().mul(100).unstack("category")
cat_heat = cat_heat.reindex(MODELS)

fig, ax = plt.subplots(figsize=(10, 3.2))
im = ax.imshow(cat_heat.values, vmin=0, vmax=100, cmap="RdYlGn", aspect="auto")
ax.set_xticks(np.arange(cat_heat.shape[1]))
ax.set_xticklabels(cat_heat.columns, rotation=30, ha="right", fontsize=9)
ax.set_yticks(np.arange(len(MODELS)))
ax.set_yticklabels([MODEL_LABEL[m] for m in MODELS], fontsize=9)
for i in range(cat_heat.shape[0]):
    for j in range(cat_heat.shape[1]):
        v = cat_heat.values[i, j]
        ax.text(j, i, f"{v:.0f}" if not np.isnan(v) else "-", ha="center", va="center",
                color="black" if 30 < v < 75 else "white", fontsize=9)
ax.set_title("L1 — Per-category success rate")
fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02, label="Success rate (%)")
fig.tight_layout()
fig.savefig(PLOTS / "07_heatmap_category.png", dpi=140)
plt.close(fig)


# ── Iterations distribution stacked bars per model ───────────────────────────

iter_max = int(prob["iterations"].max()) if len(prob) else 0
fig, ax = plt.subplots(figsize=(7.5, 4))
counts = (
    prob.groupby(["model", "iterations"]).size().unstack("iterations", fill_value=0).reindex(MODELS).fillna(0)
)
bottoms = np.zeros(len(MODELS))
cmap = plt.get_cmap("Blues")
for it in range(iter_max + 1):
    if it not in counts.columns:
        continue
    vals = counts[it].values
    color = cmap(0.3 + 0.7 * it / max(iter_max, 1))
    ax.bar(
        np.arange(len(MODELS)),
        vals,
        bottom=bottoms,
        color=color,
        edgecolor="black",
        linewidth=0.5,
        label=f"{it} iter",
    )
    bottoms += vals
ax.set_xticks(np.arange(len(MODELS)))
ax.set_xticklabels([MODEL_LABEL[m] for m in MODELS])
ax.set_ylabel("# problems")
ax.set_title("L1 — Distribution of refinement iterations per model")
ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.legend(loc="upper right", fontsize=8)
fig.tight_layout()
fig.savefig(PLOTS / "08_iterations_distribution.png", dpi=140)
plt.close(fig)


# ── Cost-quality scatter: wall_time vs success_rate (size = first_shot) ───────

fig, ax = plt.subplots(figsize=(6.6, 4.6))
for _, row in wide.iterrows():
    color = MODEL_COLOR[row["model"]]
    ax.scatter(
        row["mean_wall_time_s"],
        row["success_rate"],
        s=80 + 4 * row["first_shot_rate"],
        color=color,
        marker="s",
        edgecolor="black",
        alpha=0.85,
    )
    ax.annotate(
        f"{row['model']}",
        (row["mean_wall_time_s"], row["success_rate"]),
        textcoords="offset points",
        xytext=(6, 6),
        fontsize=8,
    )
ax.set_xlabel("Mean wall time per problem (s)")
ax.set_ylabel("Success rate (%)")
ax.set_title("L1 — Cost vs. quality (size = first-shot rate)")
ax.grid(True, linestyle="--", alpha=0.4)
ax.set_ylim(0, 105)
fig.tight_layout()
fig.savefig(PLOTS / "09_cost_quality_scatter.png", dpi=140)
plt.close(fig)


# ── Faithfulness bar (likely zero; surfaced explicitly) ──────────────────────

fig, ax = plt.subplots(figsize=(7.2, 3.2))
ax.bar(
    np.arange(len(MODELS)),
    wide.set_index("model").reindex(MODELS)["faith_pass_rate"].values,
    color=[MODEL_COLOR[m] for m in MODELS],
    edgecolor="black",
    linewidth=0.6,
)
ax.set_xticks(np.arange(len(MODELS)))
ax.set_xticklabels([MODEL_LABEL[m] for m in MODELS])
ax.set_ylabel("Faithfulness regex pass rate (%)")
ax.set_title("L1 — Faithfulness (regex)")
ax.set_ylim(0, 100)
ax.grid(axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig(PLOTS / "10_faithfulness.png", dpi=140)
plt.close(fig)


# ── Solver-side stats: per-problem for each model (successful only) ──────────

solver_metrics = ["solver_nodes", "solver_backtracks", "solver_fails"]
solver_labels = {"solver_nodes": "Nodes", "solver_backtracks": "Backtracks", "solver_fails": "Fails"}

best_runs_full = prob[prob["success"]].copy()

problem_order = (
    prob[prob["success"]]
    .groupby("problem_id")["difficulty"]
    .first()
    .reindex(prob["problem_id"].drop_duplicates())
    .pipe(lambda s: s.sort_values(key=lambda x: x.map({"easy": 0, "medium": 1, "hard": 2}.get)))
    .index.tolist()
)

fig, axes = plt.subplots(len(solver_metrics), 1, figsize=(11, 8.5), sharex=True)
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
            label=MODEL_LABEL[m] if ax is axes[0] else None,
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

# Detect possible stats corruption (all-successful runs identical stats).
stats_cols = ["solver_nodes", "solver_backtracks", "solver_fails", "solver_solutions_found"]
unique_stats = best_runs_full[stats_cols].dropna().drop_duplicates()
if len(unique_stats) <= 1 and len(best_runs_full) > 0:
    fig.suptitle("L1 — Solver-side stats per problem [POSSIBLY CORRUPT]", y=1.03, color="darkred")
    fig.text(
        0.5,
        0.965,
        "WARNING: identical solver stats across problems; verify parser/Java output",
        ha="center",
        color="darkred",
        fontsize=9,
        style="italic",
    )
else:
    fig.suptitle("L1 — Solver-side stats per problem", y=1.03)

fig.tight_layout()
fig.savefig(PLOTS / "11_solver_per_problem.png", dpi=140, bbox_inches="tight")
plt.close(fig)


# ── Narrative summary.md ──────────────────────────────────────────────────────

best_overall = wide.sort_values(["success_rate", "first_shot_rate", "mean_wall_time_s"],
                                ascending=[False, False, True]).head(3)

md = []
md.append("# L1 PDA — Data Analysis\n")
md.append("Dataset: **3 models × 1 prompting variant × 10 problems = 30 runs**.")
md.append("")
md.append("- Models: Qwen 2.5 Coder 32B, Claude Haiku 4.5, DeepSeek R1 (distill, Llama 70B base).")
md.append("- Variant: few-shot (monolith) + reflexive refiner per plan.")
md.append("- Benchmarks: 4 hard / 3 medium / 3 easy across 8 CSP families.")
md.append("- Refinement loop bounded at MAX_REFINEMENT_ITERATIONS=3 (universal per PDA spec).")
md.append("")

md.append("## Headline metrics (per model)\n")
md.append(wide.to_markdown(index=False, floatfmt=".1f"))
md.append("")

md.append("## Top-3 configurations (by success → first-shot → wall time)\n")
md.append(best_overall[["model", "variant", "success_rate", "first_shot_rate", "mean_iterations",
                        "mean_wall_time_s"]].to_markdown(index=False, floatfmt=".1f"))
md.append("")

# Per-difficulty breakdown
md.append("## Success rate by difficulty (per model)\n")
diff_table = (
    prob.groupby(["model", "difficulty"])["success"].mean().mul(100).unstack("difficulty").reindex(columns=diffs).round(1)
)
md.append(diff_table.to_markdown(floatfmt=".1f"))
md.append("")

# Per-category breakdown
md.append("## Per-category success rate (per model)\n")
md.append(cat_heat.round(0).to_markdown(floatfmt=".0f"))
md.append("")

# Findings
md.append("## Findings\n")

md.append("### F1 — L1 refiner split removes compile failures for Haiku")
md.append("Haiku reaches **100% success** with **0% compilation failures** and a mean of **0.5 iterations**, "
         "matching the L1 hypothesis that a specialized refiner reduces syntactic/compile errors while keeping iteration counts low. "
         "This is a tangible win over L0 for the strongest model (few-shot baseline).\n")

md.append("### F2 — DeepSeek improves but still fails on cryptarithmetic and scheduling")
md.append("DeepSeek reaches **80% success** (2 compile failures) with mean iterations **1.1**. The failures are concentrated in "
         "SEND+MORE=MONEY and Job Scheduling, suggesting the refiner improves syntactic recovery but does not consistently rescue "
         "semantic modeling errors in the hardest formalization families.\n")

md.append("### F3 — Qwen collapses at L1 with 100% compilation errors")
md.append("Qwen reports **0% success** and **100% compilation failures** at L1. This is a reversal from L0 and likely indicates "
         "a mismatch between the refiner prompt and Qwen's response shape (e.g., markdown fences or hidden reasoning leaking into Java). "
         "If Qwen is to be retained for L1+, it needs prompt hardening or an extraction guard similar to the L0 fix.\n")

md.append("### F4 — Faithfulness remains at 0% (parser dependency)\n")
md.append("Faithfulness regex pass rate is 0% across all models. As in L0, the explanation metric is not meaningful until the parser "
         "populates the `solution` dict with variable assignments.\n")

md.append("## Cross-cutting observations\n")
md.append("- The L1 delegation (refiner split) mainly shifts **compile failure rate** and **iterations**, not raw success for strong models.")
md.append("- DeepSeek remains significantly slower than Haiku even at L1, so per-level cost comparisons should report wall time alongside success.")
md.append("- The hardest families (cryptarithmetic, scheduling) still separate models; category heatmaps remain the clearest failure signal.")
md.append("")

md.append("## Plots\n")
for name in sorted(p.name for p in PLOTS.glob("*.png")):
    md.append(f"- `plots/{name}`")
md.append("")

with (BASE / "summary.md").open("w", encoding="utf-8") as f:
    f.write("\n".join(md))

print("OK:", BASE)
print("  summary_wide.csv  ->", (BASE / "summary_wide.csv").stat().st_size, "bytes")
print("  per_problem.csv   ->", (BASE / "per_problem.csv").stat().st_size, "bytes")
print("  summary.md        ->", (BASE / "summary.md").stat().st_size, "bytes")
print("  plots/            ->", len(list(PLOTS.glob('*.png'))), "PNGs")

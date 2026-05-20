"""L2 PDA — full data analysis across 3 models × 1 prompting variant.

Inputs:
  results/L2/L2_few_shot_{model}.json     (3 files, current level)
  results/L1/duo_{model}.json             (3 files, for L1->L2 delta)

Outputs: results/L2/analysis/
           summary_wide.csv         — one row per model, all metrics (L2)
           per_problem.csv          — one row per (model, problem)
           l1_vs_l2.csv             — per-model delta table
           summary.md               — narrative analysis with hypothesis check
           plots/*.png              — visuals incl. L1->L2 deltas

Read-only on the JSONs. Idempotent on output.
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
L1_DIR = LEVEL_DIR.parent / "L1"
PLOTS = BASE / "plots"
PLOTS.mkdir(parents=True, exist_ok=True)

MODELS = ["qwen", "haiku", "deepseek"]
VARIANTS = ["few_shot"]

MODEL_LABEL = {
    "qwen": "Qwen 3 Coder",
    "haiku": "Claude Haiku 4.5",
    "deepseek": "DeepSeek R1 (distill 70B)",
}
VARIANT_LABEL = {"few_shot": "Few-shot"}
MODEL_COLOR = {"qwen": "#5b8def", "haiku": "#e07a5f", "deepseek": "#81b29a"}


def load_run(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _as_int(v, default=None):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


# ── Build dataframes (L2) ─────────────────────────────────────────────────────

wide_rows: list[dict] = []
problem_rows: list[dict] = []

for m in MODELS:
    payload = load_run(LEVEL_DIR / f"L2_few_shot_{m}.json")
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


# ── L1 baseline (for delta) ───────────────────────────────────────────────────

l1_wide_rows: list[dict] = []
for m in MODELS:
    p = L1_DIR / f"duo_{m}.json"
    if not p.exists():
        continue
    payload = load_run(p)
    s = payload.get("summary", {}) or {}
    l1_wide_rows.append(
        {
            "model": m,
            "L1_success_rate": s.get("success_rate", 0.0),
            "L1_first_shot_rate": s.get("first_shot_success_rate", 0.0),
            "L1_mean_iterations": s.get("mean_iterations", 0.0),
            "L1_compilation_failure_rate": s.get("compilation_failure_rate", 0.0),
            "L1_mean_wall_time_s": s.get("mean_wall_time_seconds", 0.0),
        }
    )
l1_wide = pd.DataFrame(l1_wide_rows)

delta = wide.merge(l1_wide, on="model", how="left")
delta["d_success_rate"] = delta["success_rate"] - delta["L1_success_rate"]
delta["d_first_shot_rate"] = delta["first_shot_rate"] - delta["L1_first_shot_rate"]
delta["d_mean_iterations"] = delta["mean_iterations"] - delta["L1_mean_iterations"]
delta["d_compilation_failure_rate"] = delta["compilation_failure_rate"] - delta["L1_compilation_failure_rate"]
delta["d_mean_wall_time_s"] = delta["mean_wall_time_s"] - delta["L1_mean_wall_time_s"]
delta_keep = [
    "model",
    "L1_success_rate", "success_rate", "d_success_rate",
    "L1_first_shot_rate", "first_shot_rate", "d_first_shot_rate",
    "L1_mean_iterations", "mean_iterations", "d_mean_iterations",
    "L1_compilation_failure_rate", "compilation_failure_rate", "d_compilation_failure_rate",
    "L1_mean_wall_time_s", "mean_wall_time_s", "d_mean_wall_time_s",
]
delta = delta[delta_keep].rename(columns={
    "success_rate": "L2_success_rate",
    "first_shot_rate": "L2_first_shot_rate",
    "mean_iterations": "L2_mean_iterations",
    "compilation_failure_rate": "L2_compilation_failure_rate",
    "mean_wall_time_s": "L2_mean_wall_time_s",
})
delta.to_csv(BASE / "l1_vs_l2.csv", index=False)


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


grouped_bar("success_rate", "Success rate (%)", "L2 — Success rate by model", "01_success_rate.png", ymax=110)
grouped_bar("first_shot_rate", "First-shot success rate (%)", "L2 — First-shot success rate", "02_first_shot.png", ymax=110)
grouped_bar(
    "compilation_failure_rate",
    "Compilation failure rate (%)",
    "L2 — Compilation failure rate",
    "03_compile_fail.png",
    ymax=max(60, wide["compilation_failure_rate"].max() + 10),
)
grouped_bar("mean_iterations", "Mean refinement iterations", "L2 — Mean refinement iterations", "04_mean_iterations.png")
grouped_bar("mean_wall_time_s", "Mean wall time (s)", "L2 — Mean wall time per problem", "05_wall_time.png")


# ── L1 -> L2 delta plots (the headline of this level) ────────────────────────

def delta_bar(metric_l2: str, metric_l1: str, ylabel: str, title: str, fname: str, ymax: float | None = None):
    fig, ax = plt.subplots(figsize=(8, 4.4))
    x = np.arange(len(MODELS))
    width = 0.38
    l1_vals = [delta.loc[delta["model"] == m, metric_l1].values[0] for m in MODELS]
    l2_vals = [delta.loc[delta["model"] == m, metric_l2].values[0] for m in MODELS]
    ax.bar(x - width/2, l1_vals, width, color="lightgrey", edgecolor="black", linewidth=0.6, label="L1")
    ax.bar(x + width/2, l2_vals, width,
           color=[MODEL_COLOR[m] for m in MODELS], edgecolor="black", linewidth=0.6, label="L2")
    for xi, l1v, l2v in zip(x, l1_vals, l2_vals):
        ax.text(xi - width/2, l1v + 0.5, f"{l1v:.1f}", ha="center", fontsize=8)
        ax.text(xi + width/2, l2v + 0.5, f"{l2v:.1f}", ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_LABEL[m] for m in MODELS])
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(fontsize=9)
    if ymax is not None:
        ax.set_ylim(0, ymax)
    fig.tight_layout()
    fig.savefig(PLOTS / fname, dpi=140)
    plt.close(fig)


delta_bar("L2_success_rate", "L1_success_rate", "Success rate (%)",
          "L1 → L2 success-rate change (validator split)", "12_delta_success.png", ymax=110)
delta_bar("L2_first_shot_rate", "L1_first_shot_rate", "First-shot success (%)",
          "L1 → L2 first-shot change", "13_delta_first_shot.png", ymax=110)
delta_bar("L2_mean_iterations", "L1_mean_iterations", "Mean refinement iterations",
          "L1 → L2 mean iterations (lower is better)", "14_delta_iterations.png")


# ── Heatmap: success rate × difficulty × model ────────────────────────────────

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
ax.set_title("L2 — Success rate by problem difficulty")
fig.colorbar(im, ax=ax, fraction=0.04, pad=0.04, label="Success rate (%)")
fig.tight_layout()
fig.savefig(PLOTS / "06_heatmap_difficulty.png", dpi=140)
plt.close(fig)


# ── Heatmap: per-category success rate × model ────────────────────────────────

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
ax.set_title("L2 — Per-category success rate")
fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02, label="Success rate (%)")
fig.tight_layout()
fig.savefig(PLOTS / "07_heatmap_category.png", dpi=140)
plt.close(fig)


# ── Iterations distribution stacked bars per model ────────────────────────────

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
ax.set_title("L2 — Distribution of refinement iterations per model")
ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.legend(loc="upper right", fontsize=8)
fig.tight_layout()
fig.savefig(PLOTS / "08_iterations_distribution.png", dpi=140)
plt.close(fig)


# ── Cost-quality scatter ──────────────────────────────────────────────────────

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
ax.set_title("L2 — Cost vs. quality (size = first-shot rate)")
ax.grid(True, linestyle="--", alpha=0.4)
ax.set_ylim(0, 105)
fig.tight_layout()
fig.savefig(PLOTS / "09_cost_quality_scatter.png", dpi=140)
plt.close(fig)


# ── Faithfulness ──────────────────────────────────────────────────────────────

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
ax.set_title("L2 — Faithfulness (regex)")
ax.set_ylim(0, 100)
ax.grid(axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig(PLOTS / "10_faithfulness.png", dpi=140)
plt.close(fig)


# ── Solver-side stats per problem (successful runs only) ─────────────────────

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

if len(best_runs_full) and problem_order:
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

    stats_cols = ["solver_nodes", "solver_backtracks", "solver_fails", "solver_solutions_found"]
    unique_stats = best_runs_full[stats_cols].dropna().drop_duplicates()
    if len(unique_stats) <= 1 and len(best_runs_full) > 0:
        fig.suptitle("L2 — Solver-side stats per problem [POSSIBLY CORRUPT]", y=1.03, color="darkred")
        fig.text(0.5, 0.965,
                 "WARNING: identical solver stats across problems; verify parser/Java output",
                 ha="center", color="darkred", fontsize=9, style="italic")
    else:
        fig.suptitle("L2 — Solver-side stats per problem", y=1.03)
    fig.tight_layout()
    fig.savefig(PLOTS / "11_solver_per_problem.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


# ── Validator-specific signal: how often validator forced refinement ──────────
# A model that hits iter>=1 on a problem it eventually solves means the
# validator gate (or a real solver fail at iter=0) forced extra work.
# At L2 this is a proxy for "validator over-rejected".

succ = prob[prob["success"]].copy()
succ_breakdown = (
    succ.groupby("model")["iterations"]
    .agg(iter0_count=lambda s: (s == 0).sum(),
         iter_ge1_count=lambda s: (s >= 1).sum(),
         iter_ge2_count=lambda s: (s >= 2).sum(),
         iter_eq3_count=lambda s: (s == 3).sum())
    .reindex(MODELS)
    .fillna(0)
    .astype(int)
)
fig, ax = plt.subplots(figsize=(8, 4.2))
x = np.arange(len(MODELS))
width = 0.2
ax.bar(x - 1.5*width, succ_breakdown["iter0_count"], width, label="iter=0 (clean pass)",
       color="#81b29a", edgecolor="black", linewidth=0.6)
ax.bar(x - 0.5*width, succ_breakdown["iter_ge1_count"], width, label="iter≥1",
       color="#f4a261", edgecolor="black", linewidth=0.6)
ax.bar(x + 0.5*width, succ_breakdown["iter_ge2_count"], width, label="iter≥2",
       color="#e76f51", edgecolor="black", linewidth=0.6)
ax.bar(x + 1.5*width, succ_breakdown["iter_eq3_count"], width, label="iter=3 (hit cap)",
       color="#9d0208", edgecolor="black", linewidth=0.6)
for xi, m in enumerate(MODELS):
    for off, col in zip([-1.5, -0.5, 0.5, 1.5],
                        ["iter0_count", "iter_ge1_count", "iter_ge2_count", "iter_eq3_count"]):
        v = succ_breakdown.loc[m, col]
        ax.text(xi + off*width, v + 0.05, str(int(v)), ha="center", fontsize=8)
ax.set_xticks(x)
ax.set_xticklabels([MODEL_LABEL[m] for m in MODELS])
ax.set_ylabel("# successful problems")
ax.set_title("L2 — Successful runs by iteration depth (validator-induced refinement pressure)")
ax.legend(fontsize=8)
ax.grid(axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig(PLOTS / "15_iter_pressure_on_success.png", dpi=140)
plt.close(fig)


# ── Narrative summary.md ──────────────────────────────────────────────────────

best_overall = wide.sort_values(
    ["success_rate", "first_shot_rate", "mean_wall_time_s"],
    ascending=[False, False, True],
).head(3)

md: list[str] = []
md.append("# L2 PDA — Data Analysis\n")
md.append("Dataset: **3 models × 1 prompting variant × 10 problems = 30 runs**.\n")
md.append("- Topology: monolith_model → **validator (Adversarial CoT)** → solver, refiner loops back through validator.")
md.append("- Models: Qwen 3 Coder, Claude Haiku 4.5, DeepSeek R1 (distill 70B).")
md.append("- Variant: few-shot for the monolith; the newly-split agent (Validator) uses Adversarial CoT per plan.md §Prompting.")
md.append("- Refinement loop bounded at MAX_REFINEMENT_ITERATIONS=3 (universal per PDA spec).")
md.append("")

md.append("## Headline metrics (L2 per model)\n")
md.append(wide.to_markdown(index=False, floatfmt=".1f"))
md.append("")

md.append("## Top configurations (by success → first-shot → wall time)\n")
md.append(best_overall[["model", "variant", "success_rate", "first_shot_rate", "mean_iterations",
                        "mean_wall_time_s"]].to_markdown(index=False, floatfmt=".1f"))
md.append("")

md.append("## L1 → L2 delta (the actual headline)\n")
md.append(delta.round(2).to_markdown(index=False, floatfmt=".2f"))
md.append("")

# Per-difficulty breakdown
md.append("## Success rate by difficulty (per model, L2)\n")
diff_table = (
    prob.groupby(["model", "difficulty"])["success"].mean().mul(100).unstack("difficulty").reindex(columns=diffs).round(1)
)
md.append(diff_table.to_markdown(floatfmt=".1f"))
md.append("")

md.append("## Per-category success rate (L2)\n")
md.append(cat_heat.round(0).to_markdown(floatfmt=".0f"))
md.append("")

# ── Findings ──
md.append("## Hypothesis check\n")
md.append("**Plan.md L2 prediction:** *\"Up slightly; mean refinement iterations DOWN. Pre-solver semantic gate short-circuits doomed refinement loops.\"*\n")
md.append("**Result:** REJECTED on the iterations claim, MIXED on the success claim.\n")

md.append("- **Mean iterations went UP** for 2 of 3 models (haiku +1.5, qwen +1.8) and stayed flat for deepseek (already 0). "
          "Aggregate mean iterations rose ~0.4 → ~1.4. The validator did NOT short-circuit; it actively *added* iteration pressure.")
md.append("- **Success rate split**: deepseek +20pp (8/10 → 10/10), haiku **−50pp** (10/10 → 5/10), qwen −10pp (10/10 → 9/10). "
          "Net aggregate went down, not up.")
md.append("- **Compilation failures** stayed at 0% for deepseek and qwen but jumped for haiku, because the validator forced "
          "rewrites of code that originally compiled — the refiner sometimes broke a working model trying to address spurious validator issues.")
md.append("")

md.append("## Findings\n")

md.append("### F1 — Validator over-rejects valid models (false-positive cascade)")
md.append("On models that produce terser Java (Qwen, Haiku), the Adversarial-CoT validator routinely flags valid code as invalid, "
          "forcing the refiner to rewrite working programs. Many of those rewrites do not survive the next validator round either, "
          "leading to chains of three failed refinements (`iter=3`) and, for haiku, eventual compilation breakage.\n")

md.append("### F2 — DeepSeek's verbose output 'sails through' the validator")
md.append("DeepSeek R1 reaches **10/10 first-shot success at iter=0**, the best result of any (level, model) cell so far. "
          "Its longer reasoning-style code surface satisfies adversarial scrutiny on the first try, so the gate is a no-op. "
          "This is consistent with: validator quality depends on cosmetic signal (length, comments, explicit imports) more than on semantic correctness.\n")

md.append("### F3 — Haiku regression is the cleanest negative signal")
md.append("Haiku went from 10/10 (L1) to 5/10 (L2) — five working programs were broken by the validator-driven refinement loop. "
          "Five of haiku's L2 failures end with `compilation_error` after iter=3, meaning the refiner kept overwriting compilable code "
          "until something stopped compiling. This rules out 'the validator caught real bugs' as an explanation: the bugs were *introduced* by the loop.\n")

md.append("### F4 — Validator structured-output is brittle on OpenRouter")
md.append("Qwen3-coder repeatedly emitted >8 k tokens of preamble before its JSON, which langchain's `with_structured_output` rejects "
          "as 'length limit reached', crashing the entire run. Mitigation: validator now fails open on parse error (treats as valid). "
          "This means a non-zero number of L2 validator calls on qwen were effectively skipped — relevant context when interpreting qwen's L2 numbers.\n")

md.append("### F5 — Faithfulness still 0% (parser dependency, carried from L0/L1)")
md.append("Same parser issue as L0/L1: the `solution` dict is empty, so the regex faithfulness check has no variable names to match against. "
          "Independent of the L2 delegation experiment.\n")

md.append("## Cross-cutting observations\n")
md.append("- **The L2 hypothesis fails empirically**, but cleanly. This *is* the kind of result an ablation study is designed to surface: "
          "adding an agent does not always help, and the failure mode (over-rejection) is mechanistically interpretable.")
md.append("- **Wall-time cost** of L2 is ~2× L1 for qwen and haiku (extra validator + extra refiner calls), with no payoff. "
          "DeepSeek's wall time changes little because it never iterates.")
md.append("- The **model-dependent direction** of the L2 effect (deepseek up, haiku down) suggests adversarial-CoT validation "
          "should be gated on model verbosity/style, not applied uniformly. Worth noting in the report.")
md.append("- For **L3**, where the Formalizer splits out, we should expect this mechanism (one agent introducing structured "
          "constraints another agent rewrites against) to help only if the structured artifact is genuinely informative.")
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
print("  l1_vs_l2.csv      ->", (BASE / "l1_vs_l2.csv").stat().st_size, "bytes")
print("  summary.md        ->", (BASE / "summary.md").stat().st_size, "bytes")
print("  plots/            ->", len(list(PLOTS.glob('*.png'))), "PNGs")

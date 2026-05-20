"""build the headline cross-level charts from the L0-L3 jsons.
quick script -- outputs into the same folder it lives in.
"""
import json, os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # results/

FILES = {
    "L0": {
        "qwen":     ROOT / "L0/mono_qwen/mono_few_shot_qwen.json",
        "haiku":    ROOT / "L0/mono_haiku/mono_few_shot_haiku.json",
        "deepseek": ROOT / "L0/mono_deepseek/mono_few_shot_deepseek.json",
    },
    "L1": {
        "qwen":     ROOT / "L1/duo_qwen.json",
        "haiku":    ROOT / "L1/duo_haiku.json",
        "deepseek": ROOT / "L1/duo_deepseek.json",
    },
    "L2": {
        "qwen":     ROOT / "L2/L2_few_shot_qwen.json",
        "haiku":    ROOT / "L2/L2_few_shot_haiku.json",
        "deepseek": ROOT / "L2/L2_few_shot_deepseek.json",
    },
    "L3": {
        "qwen":     ROOT / "L3/L3_few_shot_qwen.json",
        "haiku":    ROOT / "L3/L3_few_shot_haiku.json",
        "deepseek": ROOT / "L3/L3_few_shot_deepseek.json",
    },
}

LEVELS = ["L0", "L1", "L2", "L3"]
MODELS = ["qwen", "haiku", "deepseek"]
LABEL  = {"qwen":"Qwen 2.5 Coder 32B","haiku":"Claude Haiku 4.5","deepseek":"DeepSeek R1 70B"}
COLOR  = {"qwen":"#5b8def","haiku":"#e07a5f","deepseek":"#81b29a"}

# pull metrics
S = {lvl:{} for lvl in LEVELS}
HARD = {lvl:{} for lvl in LEVELS}
for lvl in LEVELS:
    for m in MODELS:
        d = json.load(open(FILES[lvl][m], encoding="utf-8"))
        s = d.get("summary") or {}
        S[lvl][m] = s
        # hard tier successes from runs
        hard_succ = sum(1 for r in d["runs"] if r.get("difficulty")=="hard" and r.get("success"))
        HARD[lvl][m] = hard_succ

def levels_x(): return np.arange(len(LEVELS))

def line_chart(metric_key, ylabel, title, fname, ymax=None, mean=True):
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    x = levels_x()
    means = []
    for m in MODELS:
        ys = [S[lvl][m].get(metric_key, 0.0) for lvl in LEVELS]
        ax.plot(x, ys, marker="o", linewidth=2, color=COLOR[m], label=LABEL[m])
        for xi, yi in zip(x, ys):
            ax.annotate(f"{yi:.0f}" if abs(yi)>=1 else f"{yi:.1f}",
                        (xi, yi), textcoords="offset points", xytext=(0,7),
                        ha="center", fontsize=8, color=COLOR[m])
    if mean:
        ms = [np.mean([S[lvl][m].get(metric_key,0.0) for m in MODELS]) for lvl in LEVELS]
        ax.plot(x, ms, marker="s", linewidth=2.5, color="black",
                linestyle="--", label="mean (3 models)")
        for xi, yi in zip(x, ms):
            ax.annotate(f"{yi:.1f}", (xi, yi), textcoords="offset points",
                        xytext=(0,-14), ha="center", fontsize=8.5, color="black")
    ax.set_xticks(x); ax.set_xticklabels(LEVELS)
    ax.set_xlabel("Delegation level (more agents -->)")
    ax.set_ylabel(ylabel); ax.set_title(title)
    if ymax is not None: ax.set_ylim(0, ymax)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(loc="best", fontsize=9)
    fig.tight_layout()
    fig.savefig(HERE / fname, dpi=150)
    plt.close(fig)

# 01 — headline: success rate falling
line_chart("success_rate", "Success rate (%)",
           "Success rate vs. delegation depth -- monotonic decline",
           "01_success_rate_curve.png", ymax=110)

# 02 — compile failures rising
line_chart("compilation_failure_rate", "Compilation-failure rate (%)",
           "Compilation failures rise as the pipeline gets deeper",
           "02_compile_failure_curve.png", ymax=60)

# 03 — iterations rising
line_chart("mean_iterations", "Mean refinement iterations",
           "Refinement iterations climb as agents are added",
           "03_iterations_curve.png", ymax=3.2)

# 04 — first-shot collapse
line_chart("first_shot_success_rate", "First-shot success rate (%)",
           "First-shot success collapses once the validator enters",
           "04_first_shot_curve.png", ymax=110)

# 05 — hard-tier success grouped bars
fig, ax = plt.subplots(figsize=(7.6, 4.4))
x = levels_x(); width=0.25
for i, m in enumerate(MODELS):
    vals = [HARD[lvl][m] for lvl in LEVELS]
    bars = ax.bar(x + (i-1)*width, vals, width, color=COLOR[m],
                  label=LABEL[m], edgecolor="black", linewidth=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x()+b.get_width()/2, v+0.05, str(v),
                ha="center", fontsize=8.5)
totals = [sum(HARD[lvl][m] for m in MODELS) for lvl in LEVELS]
ax2 = ax.twinx()
ax2.plot(x, totals, marker="D", color="black", linewidth=2, label="Total /12")
for xi, t in zip(x, totals):
    ax2.annotate(f"{t}/12", (xi, t), textcoords="offset points",
                 xytext=(0,8), ha="center", fontsize=9, color="black")
ax2.set_ylim(0, 13); ax2.set_ylabel("Total hard-tier successes (out of 12)")
ax.set_xticks(x); ax.set_xticklabels(LEVELS)
ax.set_xlabel("Delegation level")
ax.set_ylabel("Hard-tier successes per model (/4)")
ax.set_title("Hard-tier collapse: 12/12 -> 5/12 across the ladder")
ax.set_ylim(0, 5)
ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.legend(loc="upper left", fontsize=9)
ax2.legend(loc="upper right", fontsize=9)
fig.tight_layout()
fig.savefig(HERE / "05_hard_tier_collapse.png", dpi=150)
plt.close(fig)

# 06 — wall time across levels (log scale, shows DeepSeek tail)
fig, ax = plt.subplots(figsize=(7.2, 4.4))
for m in MODELS:
    ys = [S[lvl][m].get("mean_wall_time_seconds", 0.0) for lvl in LEVELS]
    ax.plot(x, ys, marker="o", linewidth=2, color=COLOR[m], label=LABEL[m])
    for xi, yi in zip(x, ys):
        ax.annotate(f"{yi:.0f}s", (xi, yi), textcoords="offset points",
                    xytext=(0,7), ha="center", fontsize=8, color=COLOR[m])
ax.set_yscale("log")
ax.set_xticks(x); ax.set_xticklabels(LEVELS)
ax.set_xlabel("Delegation level")
ax.set_ylabel("Mean wall time per problem (s, log scale)")
ax.set_title("Wall time -- DeepSeek explodes at L3 (5h 55min on SEND+MORE=MONEY)")
ax.grid(axis="y", which="both", linestyle="--", alpha=0.4)
ax.legend(loc="best", fontsize=9)
fig.tight_layout()
fig.savefig(HERE / "06_wall_time_curve.png", dpi=150)
plt.close(fig)

# 07 — Haiku compile-fail evolution (the key M3 evidence)
fig, ax = plt.subplots(figsize=(7.0, 4.0))
ys = [S[lvl]["haiku"].get("compilation_failure_rate", 0.0) for lvl in LEVELS]
bars = ax.bar(x, ys, color="#e07a5f", edgecolor="black", linewidth=0.6)
for b, v in zip(bars, ys):
    ax.text(b.get_x()+b.get_width()/2, v+1, f"{v:.0f}%",
            ha="center", fontsize=10)
ax.set_xticks(x); ax.set_xticklabels(LEVELS)
ax.set_xlabel("Delegation level")
ax.set_ylabel("Compile-failure rate (%)")
ax.set_title("Haiku: compile failures introduced by the validator-refiner loop\n(0% at L0/L1 -> 50% at L2)")
ax.set_ylim(0, 60)
ax.grid(axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig(HERE / "07_haiku_compile_failures.png", dpi=150)
plt.close(fig)

print("done.")
print("charts in:", HERE)
for f in sorted(HERE.glob("*.png")):
    print("  ", f.name)

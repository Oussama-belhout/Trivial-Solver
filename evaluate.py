"""
CSP Solver — Level Ablation Runner (PDA)
─────────────────────────────────────────
Runs the level-N graph across the 12 inherited benchmarks and writes one
results/level_{N}.json file with per-run metrics + an aggregated summary.

Usage:
  python evaluate.py --level 0                       # all 12 benchmarks at L0
  python evaluate.py --level 1 --problems 4queens    # subset for debugging
  python evaluate.py --level 0 --output results      # custom output dir
  python evaluate.py --list                          # list benchmarks & exit

Each run captures: success, first-shot success, refinement iterations,
compilation-failure flag, wall time, solver statistics, error category, and
the generated Java's character length. Faithfulness regex is computed only
when an explanation is produced (L4).
"""

import argparse
import json
import os
import re
import sys
import time
import traceback
from datetime import datetime
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from benchmarks import BENCHMARKS, get_benchmark, list_benchmark_ids


# ── Model tag derivation (so 3 models do not overwrite each other) ────────────


def _model_short(model_name: str) -> str:
    """Filesystem-safe short tag for the current model.

    Honors MODEL_TAG env var if set; else strips OR's `vendor/` prefix and
    common `-instruct` / `-it` / `-chat` suffixes from MODEL_NAME.
    """
    override = os.getenv("MODEL_TAG", "").strip()
    if override:
        return re.sub(r"[^a-z0-9]+", "-", override.lower()).strip("-")[:24]
    slug = (model_name or "unknown").split("/")[-1]
    for suffix in ("-instruct", "-it", "-chat"):
        if slug.endswith(suffix):
            slug = slug[: -len(suffix)]
    return re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")[:24] or "unknown"


# ── Faithfulness regex (Q2 metric, only meaningful at L4) ─────────────────────


_NUMERIC_STAT_RE = re.compile(
    r"\b(?:nodes?|backtracks?|propagations?|fails?|solutions?|time)\b\s*[:=]?\s*\d",
    re.IGNORECASE,
)


def _faithfulness_score(explanation: str, solution: dict, solver_stats: dict) -> dict | None:
    """Cheap regex check: does the explanation reference real variable names AND
    at least one numeric solver statistic? Returns None when no explanation
    exists (L0-L3 paths). Returns a small dict otherwise.
    """
    if not explanation:
        return None
    var_names = list(solution.keys())
    name_hits = [v for v in var_names if v and v in explanation]
    var_overlap_ratio = (len(name_hits) / len(var_names)) if var_names else 0.0
    has_stat = bool(_NUMERIC_STAT_RE.search(explanation))
    return {
        "var_names_total": len(var_names),
        "var_names_referenced": len(name_hits),
        "var_overlap_ratio": round(var_overlap_ratio, 3),
        "mentions_numeric_stat": has_stat,
        "passes": var_overlap_ratio >= 0.5 and has_stat,
    }


# ── Single run ────────────────────────────────────────────────────────────────


# Short tags so LangSmith traces read "L0-haiku-few-4q" instead of "LangGraph"
_PROBLEM_SHORT = {
    "4queens":          "4q",
    "8queens":          "8q",
    "sudoku_9x9":       "sud9",
    "magic_square_3x3": "ms3",
    "magic_square_4x4": "ms4",
    "graph_color_7":    "gc7",
    "send_more_money":  "smm",
    "job_scheduling":   "jobsched",
    "latin_square_4x4": "ls4",
    "knapsack_5":       "knap5",
}

_VARIANT_SHORT = {"zero_shot": "zero", "few_shot": "few", "cot": "cot"}


def _trace_name(level: int, problem_id: str | None) -> str:
    """Build a short LangSmith run_name: e.g. 'L1-haiku-few-4q'."""
    model_tag = _model_short(os.getenv("MODEL_NAME", "unknown"))
    variant = os.getenv("MONOLITH_PROMPTING", "few_shot").lower()
    variant_tag = _VARIANT_SHORT.get(variant, variant[:4])
    pid = problem_id or "unk"
    pid_tag = _PROBLEM_SHORT.get(pid, pid[:8])
    return f"L{level}-{model_tag}-{variant_tag}-{pid_tag}"


def _run_single(problem_desc: str, level: int, problem_id: str | None = None) -> dict[str, Any]:
    """Run the level-N graph once on a single problem; return a metrics dict."""
    # Re-import the workflow each time so any env-driven config changes apply.
    from src.graph.workflow import build_workflow

    graph = build_workflow(level=level)

    initial_state = {
        "problem_description": problem_desc,
        "iteration": 0,
        "error_history": [],
        "current_step": "starting",
        "status": "Pipeline started",
        "messages": [],
        "skip_agents": [],
    }
    trace_name = _trace_name(level, problem_id)
    invoke_config = {"run_name": trace_name, "tags": [f"L{level}", f"problem={problem_id or 'unknown'}"]}

    result: dict[str, Any] = {
        "success": False,
        "first_shot_success": False,
        "error_category": "unknown",
        "iterations": 0,
        "wall_time_seconds": 0.0,
        "compilation_failed": False,
        "java_code_chars": 0,
        "solver_stats": {},
        "solution": {},
        "error_message": "",
        "explanation": "",
        "faithfulness": None,
    }

    start = time.time()
    try:
        final_state = graph.invoke(initial_state, config=invoke_config)
    except Exception as exc:
        result["wall_time_seconds"] = round(time.time() - start, 2)
        result["error_category"] = "pipeline_exception"
        result["error_message"] = (str(exc) + "\n" + traceback.format_exc())[:1000]
        return result

    elapsed = time.time() - start
    result["wall_time_seconds"] = round(elapsed, 2)

    iterations = final_state.get("iteration", 0)
    result["iterations"] = iterations

    choco_model = final_state.get("choco_model") or {}
    result["java_code_chars"] = len(choco_model.get("java_code", "") or "")

    solver_result = final_state.get("solver_result") or {}
    raw_status = solver_result.get("status", "unknown")
    # status may come back as a SolverStatus enum or a string depending on dump path
    status = raw_status.value if hasattr(raw_status, "value") else str(raw_status)
    result["compilation_failed"] = status == "compilation_error"

    if status == "success":
        result["success"] = True
        result["first_shot_success"] = iterations == 0
        result["error_category"] = "none"
        result["solver_stats"] = solver_result.get("statistics", {}) or {}
        result["solution"] = solver_result.get("solution", {}) or {}
    else:
        result["success"] = False
        result["first_shot_success"] = False
        result["error_category"] = status
        result["error_message"] = (solver_result.get("error_message", "") or "")[:1000]

    explanation = final_state.get("explanation", "") or ""
    result["explanation"] = explanation
    result["faithfulness"] = _faithfulness_score(
        explanation,
        result["solution"],
        result["solver_stats"],
    )
    result["error_history"] = final_state.get("error_history", []) or []

    return result


# ── Aggregation ───────────────────────────────────────────────────────────────


def _summarize(runs: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(runs)
    if total == 0:
        return {"total": 0}

    successes = sum(1 for r in runs if r["success"])
    first_shot = sum(1 for r in runs if r["first_shot_success"])
    compilation_failures = sum(1 for r in runs if r["compilation_failed"])
    iters = [r["iterations"] for r in runs]
    times = [r["wall_time_seconds"] for r in runs]

    error_breakdown: dict[str, int] = {}
    for r in runs:
        cat = r["error_category"]
        error_breakdown[cat] = error_breakdown.get(cat, 0) + 1

    by_difficulty: dict[str, dict[str, int]] = {}
    for r in runs:
        d = r.get("difficulty", "unknown")
        bucket = by_difficulty.setdefault(d, {"total": 0, "successes": 0})
        bucket["total"] += 1
        if r["success"]:
            bucket["successes"] += 1

    by_category: dict[str, dict[str, int]] = {}
    for r in runs:
        c = r.get("category", "unknown")
        bucket = by_category.setdefault(c, {"total": 0, "successes": 0})
        bucket["total"] += 1
        if r["success"]:
            bucket["successes"] += 1

    faith_runs = [r["faithfulness"] for r in runs if r.get("faithfulness")]
    faith_summary = None
    if faith_runs:
        passes = sum(1 for f in faith_runs if f.get("passes"))
        faith_summary = {
            "n_with_explanation": len(faith_runs),
            "pass_rate": round(passes / len(faith_runs) * 100, 1),
            "mean_var_overlap_ratio": round(
                sum(f["var_overlap_ratio"] for f in faith_runs) / len(faith_runs), 3
            ),
        }

    return {
        "total": total,
        "successes": successes,
        "success_rate": round(successes / total * 100, 1),
        "first_shot_successes": first_shot,
        "first_shot_success_rate": round(first_shot / total * 100, 1),
        "compilation_failures": compilation_failures,
        "compilation_failure_rate": round(compilation_failures / total * 100, 1),
        "mean_iterations": round(sum(iters) / total, 2),
        "mean_wall_time_seconds": round(sum(times) / total, 2),
        "error_breakdown": error_breakdown,
        "by_difficulty": by_difficulty,
        "by_category": by_category,
        "faithfulness": faith_summary,
    }


# ── Driver ────────────────────────────────────────────────────────────────────


def run_level(
    level: int,
    problem_ids: list[str],
    output_dir: str,
    prompting: str | None = None,
) -> dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)

    # When prompting bake-off is requested, set the env var the monolith agent
    # reads and write to mono_{variant}_{model}.json. When unset, default
    # behaviour (level_{N}_{model}.json, agent uses MONOLITH_PROMPTING default
    # = few_shot). Model namespacing prevents the 3 OR models (qwen / haiku /
    # r1) from overwriting each other's results.
    model_short = _model_short(os.getenv("MODEL_NAME", "unknown"))
    if prompting is not None:
        os.environ["MONOLITH_PROMPTING"] = prompting
        if level == 0:
            out_name = f"mono_{prompting}_{model_short}.json"
        else:
            out_name = f"L{level}_{prompting}_{model_short}.json"
    else:
        out_name = f"level_{level}_{model_short}.json"
    out_path = os.path.join(output_dir, out_name)

    timestamp = datetime.now().isoformat(timespec="seconds")
    payload: dict[str, Any] = {
        "level": level,
        "prompting": prompting or os.getenv("MONOLITH_PROMPTING", "few_shot"),
        "timestamp": timestamp,
        "provider": os.getenv("LLM_PROVIDER", "unknown"),
        "model_name": os.getenv("MODEL_NAME", "unknown"),
        "kaggle_url": os.getenv("KAGGLE_INFERENCE_URL", "") if os.getenv("LLM_PROVIDER") == "kaggle" else "",
        "n_benchmarks": len(problem_ids),
        "runs": [],
        "summary": {},
    }

    print("=" * 64)
    print(f"  PDA Level {level} — {len(problem_ids)} benchmarks")
    print(f"  Provider:  {payload['provider']} | Model: {payload['model_name']} | Tag: {model_short}")
    print(f"  Prompting: {payload['prompting']}")
    print(f"  Output:    {out_path}")
    print("=" * 64)

    for idx, pid in enumerate(problem_ids, 1):
        bench = get_benchmark(pid)
        if not bench:
            print(f"  [{idx}/{len(problem_ids)}] ⚠ unknown benchmark: {pid}, skipping")
            continue

        print(f"\n  [{idx}/{len(problem_ids)}] {bench['name']} ({bench['difficulty']})")
        print("  " + "-" * 50)

        run_metrics = _run_single(bench["description"], level=level, problem_id=pid)
        run_entry: dict[str, Any] = {
            "problem_id": pid,
            "problem_name": bench["name"],
            "category": bench["category"],
            "difficulty": bench["difficulty"],
            **run_metrics,
        }
        payload["runs"].append(run_entry)

        marker = "OK " if run_metrics["success"] else "MISS"
        print(
            f"    [{marker}] {run_metrics['error_category']:<22} "
            f"iter={run_metrics['iterations']} "
            f"t={run_metrics['wall_time_seconds']}s "
            f"java_chars={run_metrics['java_code_chars']}"
        )

        # Save incrementally so a Ctrl+C still leaves usable data on disk.
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)

    payload["summary"] = _summarize(payload["runs"])

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

    return payload


def _print_summary(payload: dict[str, Any]) -> None:
    s = payload.get("summary", {})
    if not s:
        print("\n(no summary — empty run set)")
        return

    print("\n" + "=" * 64)
    print(f"  Summary — Level {payload['level']}")
    print("=" * 64)
    print(f"  Success rate:           {s['successes']}/{s['total']}  ({s['success_rate']}%)")
    print(f"  First-shot success:     {s['first_shot_successes']}/{s['total']}  ({s['first_shot_success_rate']}%)")
    print(f"  Compilation failures:   {s['compilation_failures']}/{s['total']}  ({s['compilation_failure_rate']}%)")
    print(f"  Mean iterations:        {s['mean_iterations']}")
    print(f"  Mean wall time:         {s['mean_wall_time_seconds']}s")
    print("\n  Error breakdown:")
    for cat, n in sorted(s["error_breakdown"].items(), key=lambda kv: -kv[1]):
        print(f"    {cat:<24} {n}")
    print("\n  By difficulty:")
    for d, b in s["by_difficulty"].items():
        print(f"    {d:<10} {b['successes']}/{b['total']}")
    print("\n  By category:")
    for c, b in s["by_category"].items():
        print(f"    {c:<18} {b['successes']}/{b['total']}")
    if s.get("faithfulness"):
        f = s["faithfulness"]
        print(f"\n  Faithfulness (regex): pass {f['pass_rate']}% over {f['n_with_explanation']} explained runs "
              f"(mean var-overlap {f['mean_var_overlap_ratio']})")
    print("=" * 64)


# ── CLI ───────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="CSP PDA Level-Ablation Runner")
    parser.add_argument("--level", type=int, choices=[0, 1, 2, 3, 4],
                        help="PDA level to run (0..4). Required unless --list is used.")
    parser.add_argument("--problems", nargs="*", default=None,
                        help="Benchmark IDs to run (default: all 12).")
    parser.add_argument("--prompting", choices=["zero_shot", "few_shot", "cot"], default=None,
                        help="L0 prompting bake-off variant. When set, output goes to "
                             "mono_{variant}.json (or L{n}_{variant}.json for n>0) "
                             "and the monolith agent picks this variant via env var.")
    parser.add_argument("--output", default="results",
                        help="Output directory (default: results/)")
    parser.add_argument("--list", action="store_true",
                        help="List benchmarks and exit.")
    args = parser.parse_args()

    if args.list:
        print(f"Available benchmarks ({len(BENCHMARKS)}):")
        for b in BENCHMARKS:
            print(f"  {b['id']:<22} {b['name']:<30} [{b['category']}] ({b['difficulty']})")
        return

    if args.level is None:
        parser.error("--level is required (0..4)")

    problem_ids = args.problems or list_benchmark_ids()
    for pid in problem_ids:
        if not get_benchmark(pid):
            print(f"Unknown benchmark id: {pid}")
            print(f"Available: {', '.join(list_benchmark_ids())}")
            sys.exit(2)

    payload = run_level(args.level, problem_ids, args.output, prompting=args.prompting)
    _print_summary(payload)


if __name__ == "__main__":
    main()

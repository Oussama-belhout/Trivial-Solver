"""Run L3 across the 3 PDA models sequentially.

Sets MODEL_NAME / MODEL_TAG via os.environ before evaluate.py so each sub-run
uses a fresh provider config. Output -> results/L3_few_shot_<tag>.json.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVALUATE_PATH = REPO_ROOT / "evaluate.py"

MODELS = [
    ("qwen/qwen3-coder",                       "qwen"),
    ("anthropic/claude-haiku-4.5",             "haiku"),
    ("deepseek/deepseek-r1-distill-llama-70b", "deepseek"),
]

for name, tag in MODELS:
    print(f"\n{'='*70}\n  L3 run: {name}  (tag={tag})\n{'='*70}", flush=True)
    env = os.environ.copy()
    env["MODEL_NAME"] = name
    env["MODEL_TAG"] = tag
    t0 = time.time()
    rc = subprocess.run(
        [sys.executable, "-u", str(EVALUATE_PATH), "--level", "3", "--prompting", "few_shot"],
        cwd=REPO_ROOT,
        env=env,
    ).returncode
    print(f"\n[{tag}] done in {time.time()-t0:.1f}s rc={rc}", flush=True)

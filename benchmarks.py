"""
CSP Solver -- Benchmark Suite
-----------------------------
10 CSP problem definitions for systematic evaluation and ablation study (PDA).
Curated split: 4 hard / 3 medium / 3 easy across 8 distinct CSP families.

Difficulty here reflects **LLM-perceived difficulty** (formalization + modeling
load), not classical CSP complexity. `knapsack_5` is trivial for Choco but
hard to formalize; `send_more_money` and `job_scheduling` are promoted to
"hard" for the same reason.
"""

BENCHMARKS = [
    # ── Queens ────────────────────────────────────────────────────────────────
    {
        "id": "4queens",
        "name": "4-Queens",
        "category": "queens",
        "difficulty": "easy",
        "description": (
            "Place 4 queens on a 4x4 chessboard such that no two queens "
            "threaten each other. No two queens can share the same row, "
            "column, or diagonal."
        ),
        "expected_num_variables": 4,
        "expected_has_solution": True,
        "expected_num_solutions": 2,
    },
    {
        "id": "8queens",
        "name": "8-Queens",
        "category": "queens",
        "difficulty": "medium",
        "description": (
            "Place 8 queens on an 8x8 chessboard such that no two queens "
            "threaten each other. No two queens can share the same row, "
            "column, or diagonal."
        ),
        "expected_num_variables": 8,
        "expected_has_solution": True,
        "expected_num_solutions": 92,
    },

    # ── Sudoku ────────────────────────────────────────────────────────────────
    {
        "id": "sudoku_9x9",
        "name": "9x9 Sudoku (Easy)",
        "category": "sudoku",
        "difficulty": "hard",
        "description": (
            "Solve a 9x9 Sudoku puzzle. Place digits 1-9 in a 9x9 grid so "
            "that each row, each column, and each 3x3 box contains all "
            "digits from 1 to 9. Given clues: "
            "Row 1: [5, 3, _, _, 7, _, _, _, _], "
            "Row 2: [6, _, _, 1, 9, 5, _, _, _], "
            "Row 3: [_, 9, 8, _, _, _, _, 6, _], "
            "Row 4: [8, _, _, _, 6, _, _, _, 3], "
            "Row 5: [4, _, _, 8, _, 3, _, _, 1], "
            "Row 6: [7, _, _, _, 2, _, _, _, 6], "
            "Row 7: [_, 6, _, _, _, _, 2, 8, _], "
            "Row 8: [_, _, _, 4, 1, 9, _, _, 5], "
            "Row 9: [_, _, _, _, 8, _, _, 7, 9]. "
            "Where _ means the cell needs to be filled."
        ),
        "expected_num_variables": 81,
        "expected_has_solution": True,
        "expected_num_solutions": 1,
    },

    # ── Magic Square ──────────────────────────────────────────────────────────
    {
        "id": "magic_square_3x3",
        "name": "3x3 Magic Square",
        "category": "magic_square",
        "difficulty": "easy",
        "description": (
            "Create a 3x3 magic square where all rows, all columns, and "
            "both diagonals sum to the same value (15). Use each integer "
            "from 1 to 9 exactly once."
        ),
        "expected_num_variables": 9,
        "expected_has_solution": True,
        "expected_num_solutions": 8,
    },
    {
        "id": "magic_square_4x4",
        "name": "4x4 Magic Square",
        "category": "magic_square",
        "difficulty": "medium",
        "description": (
            "Create a 4x4 magic square where all rows, all columns, and "
            "both main diagonals sum to the same value (34). Use each "
            "integer from 1 to 16 exactly once."
        ),
        "expected_num_variables": 16,
        "expected_has_solution": True,
        "expected_num_solutions": None,  # 880 essentially unique
    },

    # ── Graph Coloring ────────────────────────────────────────────────────────
    {
        "id": "graph_color_7",
        "name": "Graph Coloring (7 vertices)",
        "category": "graph_coloring",
        "difficulty": "medium",
        "description": (
            "Color 7 vertices of a graph with the following edges: "
            "(1-2, 1-3, 2-3, 2-4, 3-5, 4-5, 4-6, 5-7, 6-7) "
            "using at most 3 colors such that no two adjacent vertices "
            "share the same color. Colors are integers 1, 2, and 3."
        ),
        "expected_num_variables": 7,
        "expected_has_solution": True,
        "expected_num_solutions": None,
    },

    # ── Cryptarithmetic ───────────────────────────────────────────────────────
    {
        "id": "send_more_money",
        "name": "SEND + MORE = MONEY",
        "category": "cryptarithmetic",
        "difficulty": "hard",  # promoted: multi-digit arithmetic + uniqueness + no-leading-zero is an LLM-trap
        "description": (
            "Solve the cryptarithmetic puzzle: SEND + MORE = MONEY. "
            "Each letter represents a unique digit (0-9). "
            "S and M cannot be 0 (no leading zeros)."
        ),
        "expected_num_variables": 8,
        "expected_has_solution": True,
        "expected_num_solutions": 1,
    },

    # ── Scheduling ────────────────────────────────────────────────────────────
    {
        "id": "job_scheduling",
        "name": "Simple Job Scheduling",
        "category": "scheduling",
        "difficulty": "hard",  # promoted: optimization (makespan) + non-overlap = hardest LLM-modeling family
        "description": (
            "Schedule 3 jobs on 2 machines. Each job has 2 tasks that must "
            "be executed in order (task 1 before task 2). Each task takes "
            "a certain amount of time: "
            "Job 1: task1=3 units on machine 1, task2=2 units on machine 2. "
            "Job 2: task1=2 units on machine 2, task2=4 units on machine 1. "
            "Job 3: task1=1 unit on machine 1, task2=3 units on machine 2. "
            "No two tasks can use the same machine at the same time. "
            "Minimize the total completion time (makespan). "
            "Define start-time variables for each task with domain [0..20]."
        ),
        "expected_num_variables": 6,
        "expected_has_solution": True,
        "expected_num_solutions": None,
    },

    # ── Latin Square ──────────────────────────────────────────────────────────
    {
        "id": "latin_square_4x4",
        "name": "Latin Square 4x4",
        "category": "latin_square",
        "difficulty": "easy",
        "description": (
            "Fill a 4x4 grid with integers 1 to 4 such that each row and "
            "each column contains each integer exactly once. "
            "This is a Latin square of order 4."
        ),
        "expected_num_variables": 16,
        "expected_has_solution": True,
        "expected_num_solutions": None,
    },

    # ── Knapsack ──────────────────────────────────────────────────────────────
    {
        "id": "knapsack_5",
        "name": "Knapsack (5 items)",
        "category": "knapsack",
        "difficulty": "hard",
        "description": (
            "Solve a 0/1 knapsack problem with 5 items. "
            "Each item has a weight and a value: "
            "Item 1: weight=2, value=6. "
            "Item 2: weight=3, value=5. "
            "Item 3: weight=6, value=8. "
            "Item 4: weight=7, value=9. "
            "Item 5: weight=5, value=6. "
            "The knapsack capacity is 10. "
            "Each item is either included (1) or not (0). "
            "Maximize the total value while keeping total weight <= 10."
        ),
        "expected_num_variables": 5,
        "expected_has_solution": True,
        "expected_num_solutions": None,
    },
]


# ── Helper functions ──────────────────────────────────────────────────────────

def get_benchmark(benchmark_id: str) -> dict | None:
    """Get a benchmark by its ID."""
    for b in BENCHMARKS:
        if b["id"] == benchmark_id:
            return b
    return None


def get_benchmarks_by_category(category: str) -> list[dict]:
    """Get all benchmarks in a category."""
    return [b for b in BENCHMARKS if b["category"] == category]


def get_benchmarks_by_difficulty(difficulty: str) -> list[dict]:
    """Get all benchmarks at a difficulty level."""
    return [b for b in BENCHMARKS if b["difficulty"] == difficulty]


def list_benchmark_ids() -> list[str]:
    """List all benchmark IDs."""
    return [b["id"] for b in BENCHMARKS]


def summary_table() -> str:
    """Pretty-print a summary table of all benchmarks."""
    header = f"{'ID':<20} {'Name':<30} {'Category':<18} {'Difficulty':<10}"
    sep = "-" * len(header)
    lines = [header, sep]
    for b in BENCHMARKS:
        lines.append(f"{b['id']:<20} {b['name']:<30} {b['category']:<18} {b['difficulty']:<10}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(f"CSP Solver Benchmark Suite -- {len(BENCHMARKS)} problems\n")
    print(summary_table())
    print()
    print("Difficulty distribution:")
    for d in ("easy", "medium", "hard"):
        n = len(get_benchmarks_by_difficulty(d))
        print(f"  {d:<8} {n}")

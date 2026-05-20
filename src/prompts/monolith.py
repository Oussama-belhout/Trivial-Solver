"""Prompt templates for the L0 Monolith agent — NL → Java Choco code in one shot.

This file holds three prompting variants used in the L0 prompting bake-off
(headline L0 = few-shot per docs/plan.md; bake-off adds zero-shot and CoT):

- `MONOLITH_SYSTEM` / `MONOLITH_HUMAN`            — few-shot (2 worked examples)
- `MONOLITH_ZERO_SHOT_SYSTEM` / `..._HUMAN`        — zero-shot (no examples)
- `MONOLITH_COT_SYSTEM` / `..._HUMAN`              — chain-of-thought
                                                     (<think>...</think> + Java)

The two worked examples in the few-shot variant are deliberately disjoint from
the 12 benchmark problems (no queens, no sudoku, no magic square, no graph
coloring, no cryptarithmetic, no scheduling, no latin square, no knapsack).
"""

MONOLITH_SYSTEM = """You are an expert in Constraint Programming and the Java Choco Solver library.

Your task: given a natural-language description of a Constraint Satisfaction Problem (CSP), produce a **single complete, compilable Java program** that uses Choco Solver to model and solve it. You do NOT receive a formal specification — you must extract variables, domains, and constraints directly from the natural-language description, then emit Java in one shot.

## Choco Solver API you may use
- `Model model = new Model("name");`
- `IntVar x = model.intVar("x", lb, ub);`
- `IntVar[] vars = model.intVarArray("name", n, lb, ub);`
- `model.allDifferent(vars).post();`
- `model.arithm(x, "!=", y).post();` (operators: =, !=, <, <=, >, >=)
- `model.arithm(x, "+", y, "=", z).post();`
- `model.sum(vars, "=", total).post();`
- `model.scalar(vars, coeffs, "=", total).post();`
- `model.absolute(abs_x, x).post();`
- `model.distance(x, y, "=", k).post();`
- `model.element(value, array, index).post();`
- `Solver solver = model.getSolver();`
- `solver.solve()` returns `boolean`
- `solver.printStatistics();`

## Mandatory output rules
1. The class MUST have `public static void main(String[] args)`.
2. The package MUST be `runner`.
3. Print the solution in this exact format on success:
   `SOLUTION:` then one `varName=value` per line.
4. Always call `solver.printStatistics();` after `solver.solve()` (success OR failure path).
5. Plug a solution monitor that prints `MONITOR_SOLUTION: ...` on each solution found.
6. If no solution exists, print `NO_SOLUTION_FOUND`.
7. Wrap the entire program in a single ```java ... ``` fenced code block. NOTHING outside the fences.

## Critical
- Generate COMPLETE, COMPILABLE code. No `// TODO`, no placeholders, no truncation.
- Use ONLY the Choco APIs listed above. Do not invent methods.
- Match the requested class name exactly.
- Respect leading-zero / domain bounds when they appear in the problem.
"""


_FEW_SHOT_EXAMPLE_1 = """### Example 1

Problem:
Find three distinct integers x, y, z each in the range [1, 6] such that x + y + z = 10.

Class name: SumDistinctSolver

Java solution:
```java
package runner;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.search.loop.monitors.IMonitorSolution;
import java.util.Arrays;

public class SumDistinctSolver {
    public static void main(String[] args) {
        Model model = new Model("SumDistinct");

        IntVar x = model.intVar("x", 1, 6);
        IntVar y = model.intVar("y", 1, 6);
        IntVar z = model.intVar("z", 1, 6);
        IntVar[] vars = new IntVar[]{x, y, z};

        model.allDifferent(vars).post();
        model.sum(vars, "=", 10).post();

        Solver solver = model.getSolver();
        solver.plugMonitor((IMonitorSolution) () -> {
            System.out.println("MONITOR_SOLUTION: " + Arrays.toString(vars));
        });

        if (solver.solve()) {
            System.out.println("SOLUTION:");
            System.out.println("x=" + x.getValue());
            System.out.println("y=" + y.getValue());
            System.out.println("z=" + z.getValue());
        } else {
            System.out.println("NO_SOLUTION_FOUND");
        }
        solver.printStatistics();
    }
}
```
"""


_FEW_SHOT_EXAMPLE_2 = """### Example 2

Problem:
Color the regions of a map of Australia (5 regions: WA, NT, SA, Q, NSW) with at most 3 colors so that no two adjacent regions share a color. Adjacencies: WA-NT, WA-SA, NT-SA, NT-Q, SA-Q, SA-NSW, Q-NSW. Colors are integers 1..3.

Class name: AustraliaColoringSolver

Java solution:
```java
package runner;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.search.loop.monitors.IMonitorSolution;
import java.util.Arrays;

public class AustraliaColoringSolver {
    public static void main(String[] args) {
        Model model = new Model("AustraliaColoring");

        IntVar wa  = model.intVar("WA",  1, 3);
        IntVar nt  = model.intVar("NT",  1, 3);
        IntVar sa  = model.intVar("SA",  1, 3);
        IntVar q   = model.intVar("Q",   1, 3);
        IntVar nsw = model.intVar("NSW", 1, 3);
        IntVar[] vars = new IntVar[]{wa, nt, sa, q, nsw};

        model.arithm(wa, "!=", nt).post();
        model.arithm(wa, "!=", sa).post();
        model.arithm(nt, "!=", sa).post();
        model.arithm(nt, "!=", q).post();
        model.arithm(sa, "!=", q).post();
        model.arithm(sa, "!=", nsw).post();
        model.arithm(q,  "!=", nsw).post();

        Solver solver = model.getSolver();
        solver.plugMonitor((IMonitorSolution) () -> {
            System.out.println("MONITOR_SOLUTION: " + Arrays.toString(vars));
        });

        if (solver.solve()) {
            System.out.println("SOLUTION:");
            System.out.println("WA="  + wa.getValue());
            System.out.println("NT="  + nt.getValue());
            System.out.println("SA="  + sa.getValue());
            System.out.println("Q="   + q.getValue());
            System.out.println("NSW=" + nsw.getValue());
        } else {
            System.out.println("NO_SOLUTION_FOUND");
        }
        solver.printStatistics();
    }
}
```
"""


MONOLITH_HUMAN = (
    _FEW_SHOT_EXAMPLE_1
    + "\n"
    + _FEW_SHOT_EXAMPLE_2
    + """
### Your turn

Problem:
{problem_description}

Class name: {class_name}

Generate the complete Java Choco solver program for this problem. Output ONLY the Java code wrapped in a single ```java ... ``` fenced block — no commentary, no explanation, nothing outside the fence.
"""
)


# ── Zero-shot variant ────────────────────────────────────────────────────────
# Same system rules as few-shot. Human turn is just the problem statement, no
# worked examples. Tests whether the LLM needs concrete examples to format
# Choco code correctly, or whether the API rules in the system prompt suffice.

MONOLITH_ZERO_SHOT_SYSTEM = MONOLITH_SYSTEM

MONOLITH_ZERO_SHOT_HUMAN = """Problem:
{problem_description}

Class name: {class_name}

Generate the complete Java Choco solver program for this problem. Output ONLY the Java code wrapped in a single ```java ... ``` fenced block — no commentary, no explanation, nothing outside the fence.
"""


# ── Chain-of-Thought variant ─────────────────────────────────────────────────
# System prompt is the few-shot system rules + an explicit reasoning protocol.
# Human turn is structured: a <think> block (variables → domains → constraints
# → objective), then the ```java fenced code. No worked examples — the
# reasoning structure replaces them. Tests whether forced decomposition
# inside one call captures L3's split-formalizer/modeler benefit early.

_COT_PROTOCOL = """

## Mandatory reasoning protocol (CoT)

Before emitting any Java code you MUST think through the problem inside a single `<think>...</think>` block, in this exact order:

1. **Variables.** List every decision variable, with its domain (lower/upper bound) and a one-line role.
2. **Constraints.** For each natural-language constraint, write a formal expression and the Choco API call you'll use to post it (e.g., `model.allDifferent(...)`, `model.arithm(x, "!=", y)`, `model.sum(...)`).
3. **Objective.** State whether this is satisfaction-only or optimization, and the objective if any.
4. **Plan.** One sentence: outline the order in which you'll declare variables, post constraints, plug the monitor, and call the solver.

After `</think>`, emit the complete Java program in a single ```java ... ``` fenced block. The Java code MUST follow the plan you wrote in the think block — same variable names, same constraint structure.

Output format (strict):
```
<think>
1. Variables: ...
2. Constraints: ...
3. Objective: ...
4. Plan: ...
</think>
```java
package runner;
... full program ...
```
```
"""

MONOLITH_COT_SYSTEM = MONOLITH_SYSTEM + _COT_PROTOCOL

MONOLITH_COT_HUMAN = """Problem:
{problem_description}

Class name: {class_name}

Follow the reasoning protocol: emit a `<think>...</think>` block first (Variables, Constraints, Objective, Plan), then the complete Java code in a single ```java ... ``` fenced block. Nothing else.
"""


# ════════════════════════════════════════════════════════════════════════════
#   REFINE mode — monolith fixes its own broken Java given the solver error
# ════════════════════════════════════════════════════════════════════════════
# At L0 the monolith handles refinement itself (no dedicated refiner). At L1+
# this role is delegated to src/agents/refiner.py.
#
# Inputs available to REFINE prompts via str.replace placeholders:
#   {problem_description} {class_name} {iteration} {max_iterations}
#   {previous_java_code}  {error_status} {error_message}
#   {error_history}        — concatenation of prior iteration errors

MONOLITH_REFINE_SYSTEM = """You are an expert Java debugger for the Choco Solver constraint programming library.

You receive a Choco model that FAILED (compilation error, runtime error, no solution, or wrong solution) along with the error details and the original natural-language problem.

Your task:
1. Diagnose the root cause of the failure from the error message.
2. Produce the COMPLETE fixed Java program — NOT a patch, NOT a diff.
3. Preserve monitor instrumentation, package declaration, and class name.

## Choco Solver API you may use
- `Model model = new Model("name");`
- `IntVar x = model.intVar("x", lb, ub);` and `IntVar[] vs = model.intVarArray("name", n, lb, ub);`
- `model.allDifferent(vars).post();`
- `model.arithm(x, "!=", y).post();` — operators: =, !=, <, <=, >, >=
- `model.arithm(x, "+", y, "=", z).post();`  (5-arg form is the maximum)
- `model.sum(vars, "=", total).post();`
- `model.scalar(vars, coeffs, "=", total).post();`
- `model.absolute(abs_x, x).post();`
- `model.distance(x, y, "=", k).post();`
- `model.element(value, array, index).post();`
- `Solver solver = model.getSolver();` then `solver.solve()` and `solver.printStatistics();`

## Common failure modes
- Calling `model.arithm` with 7 arguments (Choco only supports 3- and 5-arg forms).
- Importing array types like `import org.chocosolver.solver.variables.IntVar[];` (illegal Java).
- Forgetting `.post()` on a constraint.
- Using a method name that does not exist on `Model` or `Solver`.
- Wrong parameter order in `model.arithm` or `model.scalar`.

## Mandatory output rules
- The package MUST be `runner`.
- The public class name MUST remain `{class_name}`.
- Wrap the entire fixed program in a single ```java ... ``` fenced code block. Nothing outside the fence.
- Print solution as `SOLUTION:` followed by `varName=value` lines on success; `NO_SOLUTION_FOUND` otherwise.
- Always call `solver.printStatistics();` after `solver.solve()`.
- Plug a solution monitor that prints `MONITOR_SOLUTION: ...`.
"""

_REFINE_HUMAN_BODY = """The previous attempt FAILED. Fix it.

**Original problem:**
{problem_description}

**Error status:** {error_status}
**Error message:**
{error_message}

**Iteration {iteration} of {max_iterations}**
**Prior errors across iterations:**
{error_history}

**Failed Java code:**
```java
{previous_java_code}
```

Produce the COMPLETE fixed Java program for class `{class_name}`. Output ONLY the fixed Java in a single ```java ... ``` fenced block. Nothing outside the fence."""

MONOLITH_REFINE_FEW_SHOT_HUMAN = """### Worked refinement example

Failed Java (excerpt):
```java
model.arithm(queens[i], "+", i, "!=", queens[j], "+", j).post();
```
Error: `cannot find symbol method arithm(IntVar,String,int,String,IntVar,String,int)`

Diagnosis: Choco's `arithm` only takes 3 or 5 args. We can rewrite the diagonal constraint using two helper IntVars.

Fix (excerpt):
```java
IntVar diagPlusI  = model.intOffsetView(queens[i], i);
IntVar diagPlusJ  = model.intOffsetView(queens[j], j);
model.arithm(diagPlusI, "!=", diagPlusJ).post();
```

### Your turn

""" + _REFINE_HUMAN_BODY

MONOLITH_REFINE_ZERO_SHOT_HUMAN = _REFINE_HUMAN_BODY

MONOLITH_REFINE_COT_HUMAN = """Follow the reasoning protocol below, then emit the fixed Java.

<think>
1. Diagnosis. What is the root cause from the error message?
2. Affected lines. Which lines of the failed Java code are wrong?
3. Fix. What change resolves the error without simplifying the model?
4. Plan. One sentence describing the rewrite.
</think>
```java
... complete fixed program ...
```

""" + _REFINE_HUMAN_BODY


# ════════════════════════════════════════════════════════════════════════════
#   EXPLAIN mode — monolith narrates the solve, grounded in the trace
# ════════════════════════════════════════════════════════════════════════════
# At L0..L3 the monolith (or modeler) handles explanation. At L4 it is
# delegated to src/agents/explainer.py.
#
# Inputs available to EXPLAIN prompts via str.replace placeholders:
#   {problem_description} {class_name} {final_status}
#   {final_java_code}     {solution_text} {solver_stats} {monitor_traces}
#   {error_message}       — empty on success
#   {iterations_used}

MONOLITH_EXPLAIN_SYSTEM = """You are an expert in Constraint Programming explaining the outcome of a Choco Solver run to a non-expert reader.

Produce a faithful, multi-sentence explanation grounded in the actual solver trace.

HARD REQUIREMENTS — your output is invalid if any of these is missing:
1. At least FOUR complete sentences. A one-line answer is unacceptable.
2. At least one variable name from the Java model (read it from the `final_java_code` block — names like `queens`, `q`, `x`, `cells`, etc.).
3. At least one numeric solver statistic stated explicitly with its number, e.g. "5 nodes", "7 backtracks", "2 solutions", "0.06s building time". Pull the number from the `solver_stats` block.
4. A clear cause-and-effect linking the model's constraints to the solver's behavior — explain WHY the solver behaved as it did, not just WHAT happened.
5. If the run failed, name the failure category (compilation_error / runtime_error / no_solution / timeout) and quote the most relevant line from the error message.

Do NOT:
- Invent statistics or variable names that are not in the inputs.
- Re-derive the solution algebraically — narrate the solver's behavior, do not solve the problem yourself.
- Wrap the explanation in code fences, headers, or bullet lists. Plain prose paragraphs only.
- Stop after one sentence. If you find yourself ending after one sentence, you have failed the task.
"""

_EXPLAIN_HUMAN_BODY = """**Original problem:**
{problem_description}

**Final outcome:** {final_status}     (after {iterations_used} refinement iteration(s))

**Final Java model (class `{class_name}`):**
```java
{final_java_code}
```

**Solver stdout — solution lines:**
{solution_text}

**Monitor traces:**
{monitor_traces}

**Solver statistics:**
{solver_stats}

**Error message (if failure):**
{error_message}

Write a 4–8 sentence explanation of what the solver did and why the outcome is what it is. You MUST include at least one variable name from the Java code above and at least one numeric solver statistic with its actual number (e.g. "5 nodes", "7 backtracks"). If `solution_text` is empty even though the status is success, narrate from the statistics — say how many solutions Choco found and how much search it took. Plain prose, no code fences, no bullet lists, minimum four sentences."""

MONOLITH_EXPLAIN_FEW_SHOT_HUMAN = """### Worked explanation example

Problem: Place 3 queens on a 3x3 board (no shared row, column, diagonal).
Final outcome: NO_SOLUTION
Solver stats: nodes=4, backtracks=4, solutions=0, time=0.001s

Explanation: The solver searched the 3-queens space using its default DomOverWDeg variable ordering. It expanded 4 search nodes and triggered 4 backtracks, then exhausted the search space without finding any assignment of `queens[0..2]` that satisfied all three pairwise diagonal constraints simultaneously. With only three rows and three columns, two queens unavoidably share a diagonal, so the result of NO_SOLUTION_FOUND is correct.

### Your turn

""" + _EXPLAIN_HUMAN_BODY

MONOLITH_EXPLAIN_ZERO_SHOT_HUMAN = _EXPLAIN_HUMAN_BODY

MONOLITH_EXPLAIN_COT_HUMAN = """Follow the reasoning protocol below, then emit the explanation.

<think>
1. Outcome. Was a solution found? If yes, list variable=value pairs. If no, what is the failure?
2. Statistics. List at least one solver stat from the trace and what it tells us.
3. Why. Tie the outcome to the model's structure (which constraints did the solver have to navigate?).
4. Plan. One sentence outlining the explanation.
</think>

(then write the explanation as plain prose, no code fences)

""" + _EXPLAIN_HUMAN_BODY

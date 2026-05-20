# Final Defence — Presentation Table of Contents

**Author:** Oussama Belhout — M1 Informatique DS4H
**Supervisor:** Pr. Jean-Charles Régin (I3S)
**Defence window:** 18–21 May 2026
**Time budget:** 15 min talk + ~10 min Q&A
**Slide budget:** ~18 content slides (≈ 1 slide / min including a few image-only beats)

---

## Slide budget at a glance

| # | Section | Slides | Time |
|---|---|---|---|
| 1 | Title page | 1 | 0:30 |
| 2 | Outline | 1 | 0:30 |
| 3 | Introduction — context, problem, idea | 4 | 3:30 |
| 4 | Materials and Methods | 5 | 4:30 |
| 5 | Results | 3 | 2:30 |
| 6 | Discussion (folded into the closing arc) | 2 | 2:00 |
| 7 | Retrospective Meta-Analysis | 1 | 1:00 |
| 8 | Conclusion + contributions | 1 | 0:30 |
| 9 | Q&A holder | 1 | — |
| | **Total** | **19** | **~15 min** |

Backup slides (for Q&A only — never shown unless asked): listed at the end.

---

## Per-slide breakdown

Each slide is described with four things:
- **Purpose** — what this slide is for, in one sentence.
- **Visual** — the dominant element (figure, table, diagram, photo, code block).
- **Beats** — 3–5 short spoken points, in delivery order.
- **Takeaway** — the one thing the jury should remember when this slide leaves the screen.

---

### Slide 1 — Title

- **Purpose:** Identification.
- **Visual:** UCA / EUR-DS4H logos; clean title typography.
- **Content:**
  - Title: *Automatic solving of combinatorial problems and their explanations using LLMs and constraint programming*
  - Subtitle: *A Progressive Delegation Ablation*
  - Author, Programme, Supervisor, Host laboratory, Date.
- **Takeaway:** Who I am, what I worked on, who supervised it.

---

### Slide 2 — Outline

- **Purpose:** Navigation contract with the jury.
- **Visual:** Vertical list with section icons (no animations).
- **Beats:**
  1. Why combinatorial problems matter and why automating their resolution is hard.
  2. How we set up the study: three design axes, configuration enumeration, PDA.
  3. What we measured.
  4. What we found, and the named principle that explains it.
  5. What I gained as a researcher.
- **Takeaway:** The talk has a spine, not a list.

---

## §1 — Introduction (4 slides, ~3:30)

### Slide 3 — Where combinatorial problems live

- **Purpose:** Anchor the jury in concrete, recognisable domains before any formalism.
- **Visual:** 2×2 grid of 4 domain icons + a one-line example under each.
  - **Healthcare** — emergency operating-room assignment.
  - **Finance** — portfolio rebalancing under risk constraints.
  - **Logistics & transportation** — vehicle routing for last-mile delivery.
  - **Management / HR** — staff scheduling under skill and shift rules.
- **Beats:**
  1. All four share the same skeleton: choose values for decision variables under rules.
  2. Choice spaces explode fast (twenty employees over seven shifts → > 10^20 assignments).
  3. We will follow one concrete example — Emergency OR Assignment — for the rest of the talk.
- **Takeaway:** Combinatorial problems are everywhere; they are not abstract.

---

### Slide 4 — The CSP, made concrete

- **Purpose:** Show what a CSP *is*, using the OR example, in 60 seconds.
- **Visual:** Left half: the OR example as a table; right half: a tiny backtrack tree (≤ 5 nodes).
- **Content:**
  - **Surgeries:** C (cardiac), N (neuro), T (trauma).
  - **Operating rooms:** OR1 (full), OR2 (cardiac + general), OR3 (general only).
  - **Variables:** x_C, x_N, x_T.
  - **Domains:** x_C ∈ {OR1, OR2}, x_N ∈ {OR1}, x_T ∈ {OR1, OR2, OR3}.
  - **Constraint:** AllDifferent(x_C, x_N, x_T).
  - **Trace:** try x_C = OR1 → x_N blocked → backtrack → x_C = OR2 → propagate → x_T = OR3. **Solution:** C → OR2, N → OR1, T → OR3.
- **Beats:**
  1. The *modelling* step turns the story into variables, domains, constraints.
  2. The *solving* step is done by a specialised program (a solver) that alternates two operations: backtracking and constraint propagation.
  3. The jury sees one full solve in under one minute.
- **Takeaway:** A CSP is just variables + domains + rules; a solver searches the space without listing it.

---

### Slide 5 — The bottleneck: the modeller

- **Purpose:** Set up the economic motivation for automation.
- **Visual:** Stylised "expert" silhouette + speech bubble listing what the modeller controls:
  - choice of model formulation
  - search strategy (DFS, LDS, …)
  - heuristics (first-fail, min-domain, …)
  - data structures for global constraints
- **Beats:**
  1. The hard part is not running the solver — it is *writing the formal model* and *configuring the search*.
  2. This requires PhD-level training in constraint programming and detailed knowledge of one specific solver (here, Choco).
  3. Such experts are scarce and expensive to hire.
- **Takeaway:** High demand for solving × low supply of modellers = unmet need.

---

### Slide 6 — The idea and the research questions

- **Purpose:** Close the introduction by stating what the project investigates.
- **Visual:** Two-arrow diagram: "Natural-language problem → LLM (probabilistic) → formal model → Choco (deterministic) → solution + explanation". Highlight that the LLM only *writes the model*; the solver searches.
- **Content:**
  - **Idea:** replace the human modeller by a Large Language Model.
  - **Research questions:**
    - **RQ1.** Can an LLM produce a formal model that a generic solver accepts?
    - **RQ2.** Which design configuration of the LLM-side produces the highest success rate?
    - **RQ3.** Can the system fix its own errors without human intervention?
- **Takeaway:** The LLM is the modeller; the solver is the source of truth. The study asks how to configure the LLM side.

---

## §2 — Materials and Methods (5 slides, ~4:30)

### Slide 7 — Scope and the five behaviours

- **Purpose:** Define the playground and what must be transferred from the human expert to the LLM.
- **Visual:** Diagram with a fixed "Choco" block on the right and a variable "LLM side" block on the left, with the five behaviours listed inside the LLM block.
- **Content:**
  - **Fixed:** the solver (Choco). It is deterministic and treated as the source of truth.
  - **Variable:** everything on the LLM side.
  - **The five behaviours of the human expert that must be carried over to the LLM:**
    1. **Formalisation** — natural language → variables, domains, constraints.
    2. **Modelling** — formal spec → Java code that calls the Choco API.
    3. **Validation** — sanity-check the model before it is run.
    4. **Refinement** — read the failure trace and fix the model.
    5. **Explanation** — turn the solver's solution back into natural language.
- **Takeaway:** We are not improving the solver; we are turning the LLM into the modeller.

---

### Slide 8 — Three design axes

- **Purpose:** Frame the study spine — what we vary and why.
- **Visual:** The triple c = (π, m, α) drawn as three labelled dials.
- **Beats (the pedagogical sequence — keep this order):**
  1. **Baseline:** one LLM, one short instruction → the literature shows LLMs perform much better with a careful prompt → **Axis 1: prompting technique π**.
  2. **Next attempt:** any model will do? → studies show model choice changes per-call accuracy, context window, code-generation reliability → **Axis 2: the LLM m**.
  3. **Next attempt:** stuff everything into one call? → context explosion, silent semantic errors, no internal check → **Axis 3: the agentic design α** (how many LLM calls and how they are chained).
- **Formula on the slide:** **c = (π, m, α) ∈ Π × M × A** — every configuration is one cell of a 3-D grid.
- **Takeaway:** Three knobs. We measured every combination.

---

### Slide 9 — Values along each axis

- **Purpose:** Tell the jury exactly what was instantiated on each axis.
- **Visual:** Three vertical lanes side by side; PDA ladder figure (L0 → L3) on the right.
- **Content:**
  - **Prompting techniques (Π):** few-shot, Chain-of-Thought, Reflexion-style, structured output (Pydantic). Selected because each addresses a behaviour the agent must perform.
  - **LLMs (M):** Qwen 2.5-Coder-32B (code-tuned baseline), Claude Haiku 4.5 (small, fast, accurate), DeepSeek-R1-Distill-Llama-70B (reasoning-trained). Selected to span three deliberately different profiles.
  - **Agentic designs (A):** four rungs of the **Progressive Delegation Ablation (PDA)** — L0 monolith → L1 refiner split → L2 + validator split → L3 + formaliser split. One behaviour is detached per rung.
- **Takeaway:** 4 levels × 3 LLMs × 10 problems = 120 controlled runs.

---

### Slide 10 — The enumeration procedure

- **Purpose:** Show that this is a rigorous *full factorial design*, not a one-off A/B test.
- **Visual:** Triple-nested loop pseudocode (5 lines) + a small table of the metrics recorded.
- **Pseudocode:**
  ```
  for level in {L0, L1, L2, L3}:
      workflow = build_workflow(level)
      for model in {Qwen, Haiku, DeepSeek}:
          for problem in benchmarks (10 from CSPLib):
              run = workflow.solve(problem, model)
              record_metrics(run)
  ```
- **Metrics recorded:** success rate, first-shot success, refinement iterations, compilation-failure rate, wall time, Choco solver statistics.
- **Takeaway:** Every cell is measured under the same protocol; comparisons are honest.

---

### Slide 11 — Experimentation system

- **Purpose:** Show the implementation in one diagram.
- **Visual:** A horizontal stack diagram:
  `Benchmark suite (CSPLib) → LangGraph workflow → OpenRouter (multi-provider gateway) → LLM → generated Java → Maven compile → Choco run → LangSmith trace`.
- **Beats:**
  1. **OpenRouter** routes calls to Qwen / Haiku / DeepSeek with identical request semantics, removing one source of variability. (Earlier prototypes used Kaggle + ngrok-tunnelled local models; OpenRouter replaced them for reliability.)
  2. **LangGraph** expresses each PDA level as a state machine: one node per LLM call, one edge per conditional transition.
  3. **LangSmith** stores a full trace of every LLM call; one trace per row of the configuration grid.
- **Takeaway:** Every run is reproducible and inspectable from the LangSmith dashboard.

---

## §3 — Results (3 slides, ~2:30)

### Slide 12 — The configuration grid

- **Purpose:** Headline table — the 4×3 success-rate matrix.
- **Visual:** Table with delegation level as rows and LLM as columns, plus a per-row mean. Highlight the L0 row at 100 %.
- **Content (verbatim numbers):**

  |  | Qwen | Haiku | DeepSeek | **Mean** |
  |---|---|---|---|---|
  | L0 | 100 | 100 | 100 | **100.0** |
  | L1 | 100 | 100 | 80  | **93.3** |
  | L2 | 90  | 50  | 100 | **80.0** |
  | L3 | 90  | 60  | 50  | **66.7** |

- **Takeaway:** The shallowest delegation is the strongest configuration, whatever the LLM.

---

### Slide 13 — Success degrades along the delegation axis

- **Purpose:** Plant the surprise — the result is the opposite of what the multi-agent literature predicts.
- **Visual:** The pgfplots success-rate curve (already in the report): four points per LLM + a dashed mean line. The mean line falls 100 → 93.3 → 80 → 66.7.
- **Beats:**
  1. The pre-registered hypothesis was that more agents → higher reliability → higher success.
  2. The data falsifies that hypothesis: mean success decreases at every step.
  3. The entire decline is driven by the four *hard-tier* problems (Sudoku, SEND+MORE=MONEY, scheduling, knapsack). Easy and medium problems stay near 100 % across every cell.
- **Takeaway:** Splitting one LLM call into four did not help — it hurt.

---

### Slide 14 — The cost grew too

- **Purpose:** Show that the deeper levels lose on *both* success and cost.
- **Visual:** Two small bar charts side by side: (a) mean wall time per problem (47 s → 788 s); (b) compilation-failure rate (0 % at L0/L1 → 50 % L2 → 30 % L3 for Haiku).
- **Beats:**
  1. Wall time grows by a factor of 16 between L0 and L3.
  2. Compilation failures *appear* exactly where the validator is introduced (L2), which is a direct signature of the next slide's explanation.
  3. The retry budget (3 attempts) was the same at every level — but one retry at L3 is roughly four LLM calls, not one.
- **Takeaway:** Deeper delegation costs more *and* delivers less.

---

## §4 — Discussion (2 slides, ~2:00)

### Slide 15 — Why it degraded (five mechanisms)

- **Purpose:** Convert the curve into a causal story.
- **Visual:** Five compact cards, one per mechanism, with a single supporting datum next to each.
- **Content:**
  - **M1 — Errors stack up across stages.** p^k decay: 0.95^4 ≈ 0.81. Explains ~19 of the 33 lost percentage points.
  - **M2 — Redundancy with the external checker.** A probabilistic critic above an exact, deterministic solver adds noise without information.
  - **M3 — The critic introduces its own bugs.** Haiku: 0 % compile failures at L0/L1, 50 % at L2. Half of L2's failures are introduced by the validator-refiner loop itself.
  - **M4 — The retry budget is blind to the cost of one retry.** Same budget = wildly different compute across levels.
  - **M5 — LLMs react differently to delegation.** No ranking of the three LLMs is preserved across the four levels.
- **Takeaway:** The decline has a structural cause, not a measurement artefact.

---

### Slide 16 — The verifier-redundancy tax

- **Purpose:** The named principle — the strongest contribution of the work.
- **Visual:** Two-column diagram. Left: "Tasks **without** an external checker" (essay writing, code review without execution, open dialogue) → multi-agent **substitutes** for a missing verifier → **gains**. Right: "Tasks **with** an exact external checker" (CSP solving against Choco) → multi-agent **competes** with the verifier → **costs**.
- **Beats:**
  1. The mechanisms M1–M5 unify under one rule.
  2. **Verifier-redundancy tax:** when an exact deterministic checker is already in the loop, adding LLM agents competes with that checker rather than helps it.
  3. This restricts — does not refute — the AutoGen / MetaGPT claims: their tasks have no exact checker; CSP solving does.
  4. The tax is a CSP-specific instance of the broader **LLM-Modulo** principle (Kambhampati et al., ICML 2024).
- **Takeaway:** The headline finding has a name, a mechanism, and a place in the literature.

---

## §5 — Retrospective Meta-Analysis (1 slide, ~1:00)

### Slide 17 — What this tutorship taught me

- **Purpose:** Tutorship-specific — the jury wants to see growth, not just results.
- **Visual:** A horizontal timeline with three milestones above the line and a short skill list below.
- **Above the line (subject evolution):**
  1. **Start:** "Get an LLM to solve combinatorial problems."
  2. **Mid:** "Find the best LLM-side configuration to solve them."
  3. **End:** "Measure why deeper delegation hurts when an exact checker is present."
- **Below the line (skills gained):**
  - ~2 months of SOTA analysis: prompting families, multi-agent frameworks, neuro-symbolic systems, LLM-Modulo.
  - Hard skills: LangGraph, LangSmith, OpenRouter, Choco, Maven, structured output, Reflexion-style retry loops, pgfplots-based reporting.
  - Soft skills: framing a refuted hypothesis as a positive contribution; writing a reproducible experiment protocol; defending a result the literature did not predict.
- **Takeaway:** The project taught me how to turn a refuted hypothesis into a named principle.

---

## §6 — Conclusion (1 slide, ~0:30)

### Slide 18 — Contributions and selling points

- **Purpose:** Close strong. This slide is the one the jury sees while writing your grade.
- **Visual:** Two columns. Left header: **Technical contributions.** Right header: **Pedagogical / methodological contributions.**
- **Left (technical):**
  1. A controlled full-factorial enumeration of the (π, m, α) configuration space over 120 runs.
  2. A measured monotonic decline along the agentic-design axis (100 % → 66.7 %).
  3. A named principle — **the verifier-redundancy tax** — that organises the decline and connects it to LLM-Modulo.
- **Right (pedagogical / methodological):**
  1. A reusable protocol: pre-registered predictions, refutation table, five-mechanism explanation.
  2. A reproducible experimental stack (LangGraph + OpenRouter + LangSmith + Choco) with one LangSmith trace per cell.
  3. A clear statement of when multi-agent decomposition is expected to help — and when it is not.
- **One-line closer (spoken):** *"More agents are not always better. When an exact verifier is already in the loop, fewer agents is the right answer — and now we have a principled reason why."*

---

### Slide 19 — Thank you / Questions

- **Purpose:** Holder for Q&A.
- **Visual:** Project title at top; supervisor + lab acknowledgement; LangSmith URL or QR code optional.
- **Spoken:** *"I am happy to take your questions."*

---

## Backup slides (for Q&A only — keep ready, do not show by default)

| # | Title | Why you might need it |
|---|---|---|
| B1 | The exact L3 message trace on 8-Queens | If asked "how does L3 actually look in action?" — show the user → formaliser (JSON) → modeller (Java) → validator → Choco → explanation chain. |
| B2 | The DeepSeek 21,318 s outlier | If asked about the wall-time outlier — show that it was a stalled HTTP request, not model reasoning. |
| B3 | Limitations of the regex explanation score | If asked about explanation quality — show that the score returned 0 because the solution dictionary was empty during logging; LLM-as-judge is the planned fix. |
| B4 | Why CSPLib? | If asked why these ten problems — comparability with prior constraint-programming work. |
| B5 | Pre-registered predictions vs. observations | The verdict table (four rows, four refutations). |
| B6 | Related agentic-CP system (CP-Agent, Szeider 2025) | If asked how this compares to other LLM-driven CP work. |
| B7 | Future directions | Six items, mapped one-to-one to the five limitations + one extension. |

---

## Style notes for the slide-generation phase (hand to the Canva LLM)

- **Visual hierarchy:** one big idea per slide; one figure or one short bullet list, never both crowded.
- **Colour palette:** muted blue + green accent (echoing the report's TikZ figures: blue!8 for agents, green!12 for the solver).
- **Typography:** sans-serif; ≥ 20 pt body; titles ≥ 28 pt.
- **Banned on slides:** long paragraphs, full sentences as bullets, abbreviations introduced without expansion, more than 6 lines of text on any slide.
- **Reuse from report:** all figures (4-Queens illustration, PDA ladder, prompt anatomy, success-rate curve, hard-tier bars, Haiku compile-fail bars) already exist as TikZ/pgfplots in `tutorat_report.tex`; they can be rebuilt or exported.
- **Per slide, supply to the slide-generation LLM:**
  1. Slide title (exact text).
  2. Visual element description (one sentence).
  3. The 3–5 bullets or table content.
  4. The takeaway line (used as a footer or speaker note, not on the slide itself).

---

*End of TOC. Next phase: hand this file to the slide-generation LLM with a Canva-tool prompt.*

# Prompt — Generate the defence slide deck in Canva

> Paste everything below into a new Claude conversation that has the **Canva MCP tools enabled**. It will produce a 30-slide deck and export it as a PDF.

---

## 1. Your mission

You are building the slide deck for a 15-minute Master's tutorship defence. Use the **Canva MCP tool suite** to create the design, populate every slide one by one, and export the final result as a PDF. Return both the editable Canva URL and the exported PDF link.

The full slide-by-slide content is given in section 7 below. Follow it slide-for-slide. Do not invent extra slides. Do not skip slides.

---

## 2. Speaker and project identity

- **Speaker:** Oussama Belhout
- **Programme:** M1 Informatique — EUR DS4H, Université Côte d'Azur
- **Supervisor:** Pr. Jean-Charles Régin
- **Host laboratory:** I3S
- **Title of the work:** *Automatic Solving of Combinatorial Problems and their Explanations using LLMs and Constraint Programming*
- **Subtitle:** *A Progressive Delegation Ablation*
- **Defence window:** 18–21 May 2026
- **Talk length:** 15 minutes + ~10 minutes Q&A

---

## 3. Audience (this is the most important section)

The jury is **2–3 people, kind, but mixed in expertise**. At least one member is a **pedagogy / education** specialist — not a technical specialist.

Therefore:

1. **Default reading level: motivated non-specialist.** Anyone with a master's-level scientific background must follow every slide without prior knowledge of constraint programming, prompt engineering, or multi-agent systems.
2. **Define every technical term the first time it appears.** "Constraint Satisfaction Problem", "LLM", "agent", "ablation", "delegation" — all defined inline with one short phrase, not assumed.
3. **Pedagogical flow is non-negotiable.** Every slide must connect to the previous one with a visible logical step. Reuse the same running example (Emergency OR Assignment) across the introduction so the audience never restarts from zero.
4. **Speak at the level of *intuition first*, then formalism.** Show the picture, then name it.

---

## 4. Hard rules on slide content (NEVER violate)

These rules override anything else. The previous draft of the deck violated them; this one must not.

| Rule | Concretely means |
|---|---|
| **One idea per slide** | If you have two ideas, you have two slides. |
| **At most one short phrase OR two short sentences on a slide** | No paragraphs. No long bullets. No nested bullets. |
| **Every slide must carry a visual** | Diagram, icon, chart, table, pictogram, photo, or shape composition. A slide with only text is a failure. |
| **No abbreviations without expansion on first use** | "LLM" → write "Large Language Model (LLM)" once, then "LLM" thereafter. Same for CSP, PDA, RQ, etc. |
| **Speaker notes carry the elaboration; slides carry the punchline** | Every slide must have populated speaker notes. The talk is delivered from notes, not read from slides. |
| **No more than 6 lines of text on any slide, ever** | Includes title + caption + axis labels. |
| **Title length ≤ 8 words** | Titles are a phrase, not a sentence. |

If a slide as specified below cannot fit these rules, **split it into two slides**. Never compress.

---

## 5. Visual style guide

- **Palette:**
  - Primary blue: `#1E5AA8` (used for titles and key shapes)
  - Soft blue fill: `#E8F0FB` (used for agent boxes — echoes the report's `blue!8`)
  - Soft green fill: `#E2F3E0` (used for the solver box — echoes the report's `green!12`)
  - Accent orange: `#E07A00` (used only to highlight the key surprise / contribution)
  - Neutral grey: `#5A5A5A` for secondary text
  - Background: white or a very pale grey (`#FAFAFA`).
- **Typography:**
  - Sans-serif throughout (Canva default: Inter, Open Sans, or Montserrat).
  - Title size: 36–44 pt.
  - Caption / body: 22–28 pt.
  - Never go below 20 pt.
- **Iconography:** Use Canva's built-in flat / line icon set. Avoid 3D, cartoon, or photo-realistic icons. Keep one icon family throughout the deck.
- **Page size:** Standard 16:9 presentation (1920×1080).
- **No animations.** No transition effects beyond the default.
- **Footer (every slide except title + thank-you):** small grey text — "Belhout · DS4H tutorship defence · May 2026" on the left, slide number on the right.

---

## 6. How to use the Canva MCP tools

Follow this sequence:

1. **Create the deck:** call `generate-design-structured` (or `create-design-from-candidate` if a candidate is already available) with the title from section 2 and `design_type = presentation`. Plan for 30 pages.
2. **Open an editing transaction:** call `start-editing-transaction` on the new design ID.
3. **For each slide (1 → 30):**
   - Use `perform-editing-operations` to set the slide's layout (title, caption, visual placeholder).
   - Add the title, the caption (if any), and the visual element described in section 7.
   - Populate the **speaker notes** field with the elaboration text from section 7.
   - Apply the palette and typography rules from section 5.
4. **Commit:** call `commit-editing-transaction`.
5. **Export:** call `export-design` with `format = PDF` to produce a deliverable PDF.
6. **Return** the Canva editable URL and the PDF URL to the user.

If any Canva tool call fails, retry once. If it fails again, report the failure verbatim and stop — do not silently substitute behaviour.

---

## 7. Slide-by-slide content

Below, every slide is given with four fields: **TITLE** (≤ 8 words, appears on the slide), **VISUAL** (the dominant graphic element — describe to Canva what to render or fetch), **CAPTION** (at most one short phrase shown under the visual; may be empty), and **NOTES** (speaker notes — never shown on screen).

> Wherever the visual reuses a figure from the written report (`tutorat_report.tex`), the figure is described in plain terms so Canva can rebuild it natively from shapes and text.

---

### Slide 1 — Title slide

- **TITLE:** Automatic Solving of Combinatorial Problems with LLMs
- **VISUAL:** UCA and EUR-DS4H logos at top; clean centred title block; subtitle below in lighter weight; bottom-left: name, programme, supervisor, lab; bottom-right: defence date.
- **CAPTION:** *A Progressive Delegation Ablation*
- **NOTES:** Greet the jury. State your name and the title in one sentence. Do not read the slide.

---

### Slide 2 — Outline

- **TITLE:** Today's journey
- **VISUAL:** A horizontal row of five circular icons, evenly spaced: a compass (context), a flask (method), a bar chart (results), a lightbulb (insight), a mirror (reflection). One word under each icon.
- **CAPTION:** *Context · Method · Results · Insight · Reflection*
- **NOTES:** Five stops. We start from a real-life problem, build the method, show what we found, name the principle behind it, and close on what the project taught me.

---

## §1 — Introduction (slides 3 to 10)

### Slide 3 — Combinatorial problems are everywhere

- **TITLE:** They are everywhere
- **VISUAL:** A 2×2 grid of four illustrated tiles, each with an icon + a one-line example caption.
  - **Healthcare** — *Assigning emergency surgeries to operating rooms.*
  - **Finance** — *Choosing a portfolio under risk limits.*
  - **Logistics** — *Routing delivery trucks across a city.*
  - **Human resources** — *Scheduling hospital staff across shifts.*
- **CAPTION:** (none)
- **NOTES:** Four domains, one shared skeleton: choose values for decision variables under a list of rules. The choice space grows exponentially — twenty staff over seven shifts already gives more than 10²⁰ possible schedules.

---

### Slide 4 — A real-life case

- **TITLE:** Three emergencies, three rooms
- **VISUAL:** Left column: three person-icons labelled "Cardiac", "Neuro", "Trauma". Right column: three door-icons labelled "OR1 (full equipment)", "OR2 (cardiac + general)", "OR3 (general only)". A big question mark between the two columns.
- **CAPTION:** *Who goes where?*
- **NOTES:** A hospital has three operating rooms. Three emergencies arrive at the same time. Each room is equipped for some surgeries and not others. Each surgery must be assigned to a compatible room, and no two surgeries can use the same room at the same time.

---

### Slide 5 — The same problem, formally

- **TITLE:** The same story, written in math
- **VISUAL:** Three vertical pastel boxes side by side, titled **Variables**, **Domains**, **Constraints**, each holding 1–2 lines of math:
  - **Variables:** x_C, x_N, x_T
  - **Domains:** x_C ∈ {OR1, OR2}; x_N ∈ {OR1}; x_T ∈ {OR1, OR2, OR3}
  - **Constraints:** AllDifferent(x_C, x_N, x_T)
- **CAPTION:** *A Constraint Satisfaction Problem (CSP) = variables + domains + rules.*
- **NOTES:** Three ingredients. Variables are the decisions. Domains are what each decision can be. Constraints are the rules that must hold. Every problem from the previous slide fits this shape.

---

### Slide 6 — How a solver finds the answer

- **TITLE:** Try, fail, backtrack, propagate
- **VISUAL:** A small backtrack tree (4–5 nodes), drawn as labelled circles with arrows. Leftmost path crossed out in red ("x_C = OR1 → no OR for neuro → fail"). Rightmost path highlighted in green ("x_C = OR2 → x_N = OR1 → x_T = OR3").
- **CAPTION:** *The solver explores the space — without listing it.*
- **NOTES:** A constraint solver alternates two moves. Backtracking: undo the last choice when it leads to a dead end. Propagation: remove from the remaining choices anything that cannot still satisfy the rules. The result is an exact, deterministic search.

---

### Slide 7 — Behind every model: an expert

- **TITLE:** Many knobs, one expert
- **VISUAL:** A stylised expert silhouette in the centre, with four dials around them, each labelled: *Model formulation*, *Search strategy*, *Heuristics*, *Data structures*.
- **CAPTION:** *Each knob requires PhD-level training.*
- **NOTES:** Writing the formal model and tuning the search engine takes years of expertise in constraint programming and detailed knowledge of one specific solver. The hard part is not running the solver — it is preparing what to give it.

---

### Slide 8 — The mismatch

- **TITLE:** High demand, low supply
- **VISUAL:** Two opposing bars: a tall green bar labelled "Industries that need it" (with sub-icons: hospital, bank, truck, factory) and a short red bar labelled "Experts available".
- **CAPTION:** *Hiring the expert does not scale.*
- **NOTES:** Demand for combinatorial problem-solving grows every year — healthcare, finance, logistics, manufacturing. The supply of qualified modellers does not. This mismatch is the economic motivation behind automation.

---

### Slide 9 — The idea

- **TITLE:** Let the LLM be the modeller
- **VISUAL:** A horizontal arrow chain with four boxes: "Natural-language description" → soft-blue box "Large Language Model (LLM)" → "Formal model" → soft-green box "Solver (Choco)" → "Solution".
- **CAPTION:** *A probabilistic mind drives a deterministic engine.*
- **NOTES:** A Large Language Model — a neural network trained on enormous amounts of text — reads the problem in everyday language and writes the formal model. The solver, which gives exact guarantees, does the actual search. This combination is called a **neuro-symbolic system**.

---

### Slide 10 — Three research questions

- **TITLE:** Three questions
- **VISUAL:** Three large question marks in a row; under each, one short research question in italics.
  - **RQ1:** *Can an LLM produce a model the solver accepts?*
  - **RQ2:** *Which configuration of the LLM works best?*
  - **RQ3:** *Can the system fix its own mistakes?*
- **CAPTION:** (none)
- **NOTES:** RQ1 is feasibility. RQ2 is optimisation across the design space we will see next. RQ3 is autonomy — can it recover from a bad first attempt without human help.

---

## §2 — Materials and Methods (slides 11 to 22)

### Slide 11 — Where we focus

- **TITLE:** We tune only one side
- **VISUAL:** Two boxes side by side. Left, soft-blue, labelled **LLM side — variable**, with a small dial icon. Right, soft-green, labelled **Solver (Choco) — fixed**, with a padlock icon.
- **CAPTION:** *The solver stays. The LLM side varies.*
- **NOTES:** The solver is the source of truth, treated as a black box. Everything we change happens on the LLM side. This keeps the experiment honest: any change in success rate comes from a change we control.

---

### Slide 12 — What the expert really does

- **TITLE:** Five behaviours to transfer
- **VISUAL:** A horizontal strip of five small cards, each with an icon + a one-word label: **Formalise**, **Model**, **Validate**, **Refine**, **Explain**.
- **CAPTION:** *We carry each behaviour over to the LLM.*
- **NOTES:** The expert reads the problem (formalise), writes Java code (model), checks the code makes sense (validate), reads error traces and fixes them (refine), and explains the solution (explain). The LLM side has to do all five.

---

### Slide 13 — Naïve attempt

- **TITLE:** One LLM, one order
- **VISUAL:** A single LLM bubble with an arrow to a solver box. No surrounding context.
- **CAPTION:** *Sometimes works. Often fails.*
- **NOTES:** The most direct attempt — give the LLM the problem and ask for Java code. This works on the easy cases. It fails silently on harder ones: the code compiles but encodes a wrong constraint. We need controls.

---

### Slide 14 — Better with a better prompt

- **TITLE:** Axis 1 — prompting
- **VISUAL:** A vertically-stacked prompt anatomy: three rounded blocks labelled **System instruction**, **Worked example**, **Actual request**. Small annotations on the right.
- **CAPTION:** *How we phrase the request matters.*
- **NOTES:** A prompt is the template we use to phrase the LLM's task. Adding a worked example, asking for step-by-step reasoning, or attaching the previous failure trace are well-known techniques. This is the first axis of the study — we call it π.

---

### Slide 15 — Better with a better model

- **TITLE:** Axis 2 — model selection
- **VISUAL:** Three LLM "badges" side by side. Each shows the model name and a one-line distinguisher.
  - **Qwen 2.5-Coder-32B** — *open, code-tuned baseline*
  - **Claude Haiku 4.5** — *small, fast, accurate*
  - **DeepSeek-R1 70B** — *trained to reason step by step*
- **CAPTION:** *Three deliberately different profiles.*
- **NOTES:** Different LLMs differ in size, training data, and reliability when generating code. We pick three with very different profiles to see whether the conclusions hold beyond one specific model. This is the second axis — we call it m.

---

### Slide 16 — Better with several agents?

- **TITLE:** Axis 3 — agentic design
- **VISUAL:** Two side-by-side diagrams. Left: one LLM bubble with all five behaviour-labels stacked inside it. Right: a chain of four bubbles, each labelled with one behaviour.
- **CAPTION:** *One generalist, or four specialists?*
- **NOTES:** An "agent" is one LLM call configured for one specific task. We can put all five behaviours in one agent — or split them across many specialised agents that pass messages to each other. This is the third axis — we call it α.

---

### Slide 17 — One configuration, one cell

- **TITLE:** Every system is one cell of a grid
- **VISUAL:** A 3-D cube wireframe with the three axes labelled π (prompts), m (models), α (agentic designs). One small marker inside the cube highlighted.
- **CAPTION:** *c = (π, m, α)*
- **NOTES:** Any system we can build is one combination of a prompt, a model, and an agentic design. Each combination is one cell of a three-dimensional grid. The study enumerates the cells.

---

### Slide 18 — Prompts chosen

- **TITLE:** One prompt per behaviour
- **VISUAL:** Four small cards in a 2×2 grid, each labelled with the technique and the behaviour it serves.
  - **Few-shot** — *for general modelling*
  - **Chain-of-Thought** — *for validation*
  - **Reflexion** — *for refinement*
  - **Structured output** — *for formalisation*
- **CAPTION:** (none)
- **NOTES:** Each prompting technique was chosen because it matches the kind of work the agent does. Few-shot prompting shows worked examples; Chain-of-Thought asks the LLM to think step by step; Reflexion shows the previous failure and asks the LLM to revise; structured output forces a strict JSON shape.

---

### Slide 19 — Models chosen

- **TITLE:** Three deliberately different LLMs
- **VISUAL:** Same three model badges as slide 15, larger, with a tagline under each.
- **CAPTION:** *Open · Fast · Reasoning-trained.*
- **NOTES:** All three models accessed through OpenRouter — a single network gateway that exposes models from different providers behind the same interface. This removes one source of measurement noise.

---

### Slide 20 — The delegation ladder

- **TITLE:** Progressive Delegation Ablation
- **VISUAL:** Four horizontal rows, top to bottom. **L0**: one box "Monolith" → solver. **L1**: monolith → refiner → solver. **L2**: monolith → validator → refiner → solver. **L3**: formaliser → modeller → validator → refiner → solver. Use the blue/green palette consistently.
- **CAPTION:** *At each rung, one behaviour is detached from the monolith.*
- **NOTES:** L0 is a single agent that does everything. At each rung, one of the five behaviours is taken out and given to a dedicated specialised agent. L3 has four agents in a chain, with the solver at the end. The expected effect — based on the multi-agent literature — was that deeper rungs would perform better.

---

### Slide 21 — The enumeration procedure

- **TITLE:** Test every combination
- **VISUAL:** A code-styled block (monospaced, light background) showing the triple-nested loop:
  ```
  for level in {L0, L1, L2, L3}:
      for model in {Qwen, Haiku, DeepSeek}:
          for problem in benchmark_suite:
              run(level, model, problem)
              record_metrics()
  ```
- **CAPTION:** *4 × 3 × 10 = 120 controlled runs.*
- **NOTES:** Every cell of the grid is measured under identical conditions. The benchmark suite is ten problems from CSPLib, the standard library used by the constraint-programming community.

---

### Slide 22 — Reproducible by design

- **TITLE:** The experimentation stack
- **VISUAL:** A horizontal stack diagram, left to right, with each box labelled:
  - **CSPLib** (the 10 problems) → **LangGraph** (the agent workflow) → **OpenRouter** (the LLM gateway) → **LLM call** → **Generated Java** → **Choco solver** → **LangSmith** (trace storage)
- **CAPTION:** *One run = one trace.*
- **NOTES:** LangGraph builds each agentic design as a state machine. LangSmith stores a full trace of every LLM call. Any cell of the grid can be inspected after the fact, replayed, or compared.

---

## §3 — Results (slides 23 to 25)

### Slide 23 — Success rate per cell

- **TITLE:** The configuration grid
- **VISUAL:** A 4×3 table with rows L0–L3 and columns Qwen / Haiku / DeepSeek. Cells coloured on a heatmap scale (dark green = 100 %, dark red = 50 %). Values inside each cell:
  - L0: 100 · 100 · 100
  - L1: 100 · 100 · 80
  - L2: 90 · 50 · 100
  - L3: 90 · 60 · 50
- **CAPTION:** *The shallowest row is uniformly green.*
- **NOTES:** L0 is at 100% across all three LLMs. The success rate worsens as we go down the table — which is the opposite of what the multi-agent literature predicts.

---

### Slide 24 — More agents, less success

- **TITLE:** A monotonic decline
- **VISUAL:** A line plot. X-axis: L0, L1, L2, L3. Y-axis: success rate (40 %–110 %). Three coloured lines (Qwen, Haiku, DeepSeek) and a thicker dashed black line for the mean. Mean values: 100 → 93.3 → 80 → 66.7.
- **CAPTION:** *Mean success falls 33 percentage points across the ladder.*
- **NOTES:** Each step of the ladder loses points. The drop comes entirely from four hard-tier problems — the easy and medium tiers stay near 100 %. The hypothesis the multi-agent literature would have predicted is refuted by the data.

---

### Slide 25 — More agents, more cost

- **TITLE:** And it costs more
- **VISUAL:** Two small bar charts side by side. Left: wall time per problem — 47 s (L0), 120 s (L1), 320 s (L2), 788 s (L3). Right: Claude Haiku compilation-failure rate — 0 %, 0 %, 50 %, 30 %.
- **CAPTION:** *16× wall time. 50 % compile failures.*
- **NOTES:** Wall time grows sixteen-fold. Haiku produced no compile failures at L0 and L1 — then half its runs failed to compile once the validator was added at L2. This is a direct fingerprint of one of the mechanisms we will see next.

---

## §4 — Discussion (slides 26 to 28)

### Slide 26 — Errors stack up

- **TITLE:** Errors stack up across stages
- **VISUAL:** Four small boxes in a chain. Each box labelled "p = 0.95". Joint probability under the chain: 0.95⁴ ≈ 0.81. Show the multiplication visually.
- **CAPTION:** *Four 95-% steps give only 81 %.*
- **NOTES:** When a task passes through more agents, each one has to be right. With four perfect-looking stages at 95 % each, the joint success drops by 19 percentage points just from arithmetic. This explains most — but not all — of what we saw.

---

### Slide 27 — The critic competes with the solver

- **TITLE:** The critic competes with the solver
- **VISUAL:** A magnifying-glass icon hovering over a green check mark, with a red arrow saying "wrongly flags as broken". Below: a small replica of the Haiku 0/0/50/30 bar chart from slide 25.
- **CAPTION:** *A probabilistic critic adds noise to an exact answer.*
- **NOTES:** Choco is an exact verifier. Putting an LLM critic above it is redundant at best. In practice, the critic frequently flags correct code as broken; the refiner then "fixes" code that did not need fixing — and introduces real bugs. Haiku's L2 compile failures show this directly.

---

### Slide 28 — The verifier-redundancy tax

- **TITLE:** The verifier-redundancy tax
- **VISUAL:** A two-column comparison. Left column header (green): *Tasks without an exact judge — essays, design, debate.* Diagram: agents supplying their own judgement. Right column header (red): *Tasks with an exact judge — CSP, theorem proving.* Diagram: agents competing with the judge.
- **CAPTION (in accent orange):** *More agents help when there is no exact judge — and hurt when there is one.*
- **NOTES:** This is the contribution of the work. The same multi-agent decomposition that improves essay writing or open-ended dialogue degrades performance when the underlying task already has an exact deterministic checker. We name the loss the *verifier-redundancy tax*. It is a CSP-specific instance of the broader LLM-Modulo principle from the literature.

---

## §5 — Retrospective (slide 29)

### Slide 29 — What this tutorship gave me

- **TITLE:** What this project gave me
- **VISUAL:** A horizontal timeline with three milestones — *Start: "make an LLM solve a CSP"* → *Mid: "find the best LLM configuration"* → *End: "explain why deeper delegation hurts"*. Below the line, four icons with one-word skill labels: **Research**, **Engineering**, **Writing**, **Argument**.
- **CAPTION:** *From a tool question to a measurable principle.*
- **NOTES:** Two months on state-of-the-art analysis. Hard skills: LangGraph, LangSmith, OpenRouter, Choco, structured output, reflexion loops. Soft skills: framing a refuted hypothesis as a positive contribution, writing a reproducible protocol, defending a non-obvious result.

---

## §6 — Conclusion (slide 30)

### Slide 30 — Contributions

- **TITLE:** What I bring to the table
- **VISUAL:** Two columns. Left header: **Technical** (with a wrench icon). Right header: **Methodological** (with a compass icon). Three short phrases per column.
  - **Technical:**
    - *120-run full-factorial study*
    - *Monotonic decline: 100 % → 66.7 %*
    - *The verifier-redundancy tax*
  - **Methodological:**
    - *Pre-registered predictions & refutation*
    - *Reproducible LangGraph + LangSmith stack*
    - *Clear scope for when multi-agent helps*
- **CAPTION (in accent orange, bottom):** *More agents are not always better.*
- **NOTES:** Close on the headline. Thank the supervisor and the laboratory. Invite questions.

---

### Slide 31 — Thank you

- **TITLE:** Thank you
- **VISUAL:** Centred project title; under it, name and supervisor. Optional small QR code linking to the LangSmith dashboard or the GitHub repository if available.
- **CAPTION:** *Questions?*
- **NOTES:** Pause. Look at the jury. Wait for the first question.

---

## 8. Deliverable

When all 31 slides are populated and the editing transaction is committed, **export the design as PDF** and return:

1. The Canva editable URL.
2. The exported PDF URL.
3. A short status report: number of slides created, any tool errors encountered, any slides that needed adaptation.

Do not return partial results. If you cannot complete the deck, stop and report which step failed.

---

*End of prompt.*

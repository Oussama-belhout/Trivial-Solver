# Bibliography for *Automatic Solving of Combinatorial Problems and their Explanations using LLMs and Constraint Programming*

**Author of report:** Oussama Belhout (M1 Informatique, DS4H, Université Côte d'Azur)
**Supervisor:** Pr. Jean-Charles Régin (I3S)
**Submission:** 12 May 2026

This document is meant to be handed off to an LLM (or human editor) for completing the report's missing bibliography. It contains two parts:

- **Part 1** — the reference list (34 entries, grouped by theme, with arXiv IDs / DOIs / publisher).
- **Part 2** — a citation usage map: for every place in the report where a reference is needed, the section number, the anchor phrase, and the rationale.

---

## Part 1 — Reference list

### A. Constraint Programming foundations

**[1]** F. Rossi, P. van Beek, T. Walsh (Eds.). *Handbook of Constraint Programming*. Foundations of Artificial Intelligence vol. 2. Elsevier, 2006.

**[2]** S. Russell, P. Norvig. *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson, 2021. — Chapter on CSPs (backtracking, AC-3, constraint propagation).

**[3]** E. C. Freuder. "In Pursuit of the Holy Grail." *Constraints* 2(1):57–61, 1997. DOI: 10.1023/A:1009749006768. — The originating "user states the problem, computer solves it" vision.

**[4]** C. Prud'homme, J.-G. Fages. "Choco-solver: A Java library for constraint programming." *Journal of Open Source Software* 7(78):4708, 2022. DOI: 10.21105/joss.04708.

**[5]** I. P. Gent, T. Walsh. "CSPLib: A benchmark library for constraints." In *Principles and Practice of Constraint Programming (CP'99)*, LNCS 1713, pp. 480–481, Springer, 1999. — www.csplib.org

### B. LLM foundations and limitations

**[6]** A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, I. Polosukhin. "Attention Is All You Need." In *NeurIPS*, 2017. — The Transformer.

**[7]** T. B. Brown, B. Mann, N. Ryder et al. "Language Models are Few-Shot Learners." In *NeurIPS*, 2020. arXiv:2005.14165. — GPT-3; canonical reference for few-shot / in-context learning.

**[8]** Z. Ji, N. Lee, R. Frieske, T. Yu, D. Su, Y. Xu, E. Ishii, Y. J. Bang, A. Madotto, P. Fung. "Survey of Hallucination in Natural Language Generation." *ACM Computing Surveys* 55(12):248, 2023. DOI: 10.1145/3571730.

**[9]** M. Sclar, Y. Choi, Y. Tsvetkov, A. Suhr. "Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design or: How I Learned to Start Worrying about Prompt Formatting." *ICLR*, 2024. arXiv:2310.11324.

### C. Prompting techniques

**[10]** J. Wei, X. Wang, D. Schuurmans, M. Bosma, B. Ichter, F. Xia, E. Chi, Q. Le, D. Zhou. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." In *NeurIPS*, 2022. arXiv:2201.11903.

**[11]** N. Shinn, F. Cassano, A. Gopinath, K. Narasimhan, S. Yao. "Reflexion: Language Agents with Verbal Reinforcement Learning." In *NeurIPS*, 2023. arXiv:2303.11366.

**[12]** A. Madaan, N. Tandon, P. Gupta et al. "Self-Refine: Iterative Refinement with Self-Feedback." In *NeurIPS*, 2023. arXiv:2303.17651.

### D. Multi-agent LLM frameworks

**[13]** Q. Wu, G. Bansal, J. Zhang, Y. Wu, B. Li, E. Zhu, L. Jiang, X. Zhang, S. Zhang, J. Liu, A. H. Awadallah, R. W. White, D. Burger, C. Wang. "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation." arXiv:2308.08155, 2023.

**[14]** S. Hong, X. Zheng, J. Chen et al. "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework." *ICLR*, 2024. arXiv:2308.00352.

**[15]** C. Qian, W. Liu, H. Liu et al. "ChatDev: Communicative Agents for Software Development." *ACL*, 2024. arXiv:2307.07924.

### E. Specific LLMs used in the experiment

**[16]** B. Hui, J. Yang, Z. Cui et al. (Qwen Team). "Qwen2.5-Coder Technical Report." arXiv:2409.12186, 2024.

**[17]** DeepSeek-AI, D. Guo, D. Yang, H. Zhang et al. "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning." *Nature* 645:633–638, 2025. arXiv:2501.12948. DOI: 10.1038/s41586-025-09422-z.

**[18]** Anthropic. "Claude 4 Model Family." Model card / system card. Anthropic, 2025. — For Claude Haiku 4.5.

### F. Neuro-symbolic AI

**[19]** A. d'Avila Garcez, L. C. Lamb. "Neurosymbolic AI: The 3rd Wave." *Artificial Intelligence Review* 56:12387–12406, 2023. DOI: 10.1007/s10462-023-10448-w.

**[20]** H. Kautz. "The Third AI Summer: AAAI Robert S. Engelmore Memorial Lecture." *AI Magazine* 43(1):105–125, 2022. DOI: 10.1609/aimag.v43i1.19122.

**[21]** S. Kambhampati, K. Valmeekam, L. Guan, M. Verma, K. Stechly, S. Bhambri, L. Saldyt, A. Murthy. "LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks." *ICML*, 2024. arXiv:2402.01817. — Structurally parallel argument to the verifier-redundancy tax.

### G. LLM + Constraint Programming (directly related work)

**[22]** D. C. Tsouros, H. Verhaeghe, S. Kadıoğlu, T. Guns. "Holy Grail 2.0: From Natural Language to Constraint Models." Workshop *Progress Toward the Holy Grail*, CP 2023. arXiv:2308.01589.

**[23]** F. Régin, E. De Maria, A. Bonlarron. "Combining Constraint Programming Reasoning with Large Language Model Predictions." In *Principles and Practice of Constraint Programming (CP 2024)*, LIPIcs vol. 307, art. 25. DOI: 10.4230/LIPIcs.CP.2024.25. arXiv:2407.13490. — **Supervisor's research group (I3S).**

**[24]** A. Bonlarron, E. De Maria, F. Régin, J.-C. Régin. "Large Language Model Meets Constraint Propagation." *IJCAI*, 2025. arXiv:2505.24012. — **Supervisor's research group (I3S).**

**[25]** J. Michailidis, T. Guns, S. Kadıoğlu. "MCP-Solver: Integrating Language Models with Constraint Programming Systems." arXiv:2501.00539, 2025.

**[26]** S. Szeider. "CP-Agent: Agentic Constraint Programming." arXiv:2508.07468, 2025. — **Direct competitor / closest comparable** for the agentic-design axis.

**[27]** R. Ramamonjison, T. T. L. Yu, R. Li, H. Li, G. Carenini, B. Ghaddar, S. He, M. Mostajabdaveh, A. Banitalebi-Dehkordi, Z. Zhou, Y. Zhang. "Augmenting Operations Research with Auto-Formulation of Optimization Models from Problem Descriptions." In *EMNLP (industry track)*, 2023. arXiv:2209.15565. — NL4OPT challenge.

**[28]** A. Pellegrino, J. Mauro. "When Words Change the Model: Sensitivity of LLMs for Constraint Programming Modelling." arXiv:2511.14334, 2025.

### H. Evaluation methodology

**[29]** L. Zheng, W.-L. Chiang, Y. Sheng, S. Zhuang, Z. Wu, Y. Zhuang, Z. Lin, Z. Li, D. Li, E. P. Xing, H. Zhang, J. E. Gonzalez, I. Stoica. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." *NeurIPS Datasets and Benchmarks Track*, 2023. arXiv:2306.05685.

### I. Software, infrastructure, tooling

**[30]** LangChain Inc. "LangGraph: Stateful, Multi-Actor Applications with LLMs." Documentation, 2024–2025. https://langchain-ai.github.io/langgraph/

**[31]** LangChain Inc. "LangSmith: Trace, Evaluate, and Monitor LLM Applications." https://www.langchain.com/langsmith

**[32]** OpenRouter, Inc. "OpenRouter: A Unified Interface for LLMs." https://openrouter.ai/

**[33]** S. Colvin et al. "Pydantic." https://docs.pydantic.dev/

**[34]** Apache Software Foundation. "Apache Maven." https://maven.apache.org/

---

## Part 2 — Citation usage map

The page numbers below refer to the typeset PDF (page 1 = cover, page 2 = abstract).
"Anchor phrase" is a short excerpt that lets a downstream LLM locate the exact insertion point.

### §1 — Introduction (p. 3)

| # | § | Anchor phrase (where to insert `[N]`) | Refs | Rationale |
|---|---|--------------------------------------|------|-----------|
| 1 | 1.1 | "Special-purpose programs called solvers can search such choice spaces..." | [1], [4] | Generic citation for CP solvers + the specific solver used (Choco). |
| 2 | 1.2 | "A Large Language Model (LLM) is a neural network trained on very large amounts of text." | [6], [7] | Transformer architecture and the seminal large-scale LLM paper. |
| 3 | 1.2 | "...because LLM outputs are probabilistic and offer no guarantee of correctness." | [8] | Hallucination survey. |
| 4 | 1.2 | "...the defining feature of neuro-symbolic systems, described in Section 2.5." | [19], [20] | Garcez & Lamb; Kautz. |
| 5 | 1.5 | "...a common assumption in the multi-agent-LLM literature." | [13], [14], [15] | AutoGen, MetaGPT, ChatDev. |
| 6 | 1.5 | "...mean success rate decreases monotonically from 100% at L0 to 66.7% at L3..." | — (no cite needed; original finding) | — |

### §2 — Background

**§2.1 Constraint Satisfaction Problems (p. 4–5).**

| # | § | Anchor phrase | Refs | Rationale |
|---|---|---------------|------|-----------|
| 7 | 2.1 | "A Constraint Satisfaction Problem (CSP) is described by three components..." | [1], [2] | Formal CSP definition. |
| 8 | 2.1 | "A small example is the 4-Queens problem, illustrated in Figure 1." | [5] | CSPLib problem 054. |
| 9 | 2.1 | "A solver such as Choco searches the space of assignments..." | [4] | Choco JOSS paper. |
| 10 | 2.1 | "The solver alternates two techniques. The first technique is backtracking... The second technique is constraint propagation..." | [1], [2] | CP Handbook / Russell-Norvig for backtracking and AC. |

**§2.2 Large Language Models (p. 5).**

| # | § | Anchor phrase | Refs | Rationale |
|---|---|---------------|------|-----------|
| 11 | 2.2 | "A Large Language Model is a neural network trained on very large amounts of text." | [6], [7] | Transformer; GPT-3. |
| 12 | 2.2 | "...a property usually called in-context learning." | [7] | Canonical reference for in-context learning. |
| 13 | 2.2 | "...the LLM can be constrained to produce structured output, for example a JSON object..." | [33] | Pydantic. |
| 14 | 2.2 | "This kind of error is called a silent semantic error..." | [8] | Hallucination survey. |
| 15 | 2.2 | "...small changes in the prompt can produce noticeably different outputs." | [9] | Prompt-sensitivity paper. |

**§2.3 The three design axes in detail (p. 5–6).**

| # | § | Anchor phrase | Refs | Rationale |
|---|---|---------------|------|-----------|
| 16 | 2.3 | "The first family is few-shot prompting..." | [7] | GPT-3 introduced few-shot ICL. |
| 17 | 2.3 | "The second family is Chain-of-Thought prompting..." | [10] | Wei et al. CoT. |
| 18 | 2.3 | "The third family is Reflexion-style prompting..." | [11] | Shinn et al. Reflexion. |

**§2.4 Self-correcting systems (p. 6).**

| # | § | Anchor phrase | Refs | Rationale |
|---|---|---------------|------|-----------|
| 19 | 2.4 | "A self-correcting system contains a loop that reads its own failure signals and tries again." | [11], [12] | Reflexion + Self-Refine — the two canonical references for LLM self-correction. |

**§2.5 Neuro-symbolic perspective (p. 6–7).**

| # | § | Anchor phrase | Refs | Rationale |
|---|---|---------------|------|-----------|
| 20 | 2.5 | "The system studied here is an instance of a wider class called neuro-symbolic." | [19], [20] | Garcez–Lamb; Kautz. |
| 21 | 2.5 | "...how should the probabilistic part and the exact part be coupled so that the exact part remains the source of truth?" | [21] | Kambhampati LLM-Modulo — same engineering question, formalised. |

**§2.6 Related work on multi-agent LLM systems (p. 7).**

| # | § | Anchor phrase | Refs | Rationale |
|---|---|---------------|------|-----------|
| 22 | 2.6 | "AutoGen provides a generic conversational scaffold." | [13] | — |
| 23 | 2.6 | "MetaGPT simulates a software-engineering team..." | [14] | — |
| 24 | 2.6 | "ChatDev uses a similar role split..." | [15] | — |
| 25 | 2.6 | "None of them includes an automatic, exact external checker that decides correctness without ambiguity." | [21] | Kambhampati makes exactly this distinction (verifier-vs-no-verifier task taxonomy). |

### §3 — Materials and Methods

**§3.3 The prompting axis (p. 8).**

| # | § | Anchor phrase | Refs | Rationale |
|---|---|---------------|------|-----------|
| 26 | 3.3 | "The monolith uses few-shot prompting with two worked examples..." | [7] | — |
| 27 | 3.3 | "The refiner uses a Reflexion-style prompt..." | [11] | — |
| 28 | 3.3 | "The validator uses adversarial Chain-of-Thought prompting..." | [10] | Base CoT; you may also want to cite an adversarial CoT variant if you can find one in your notes. |
| 29 | 3.3 | "The formaliser uses structured output through a Pydantic schema..." | [33] | — |

**§3.4 The model axis (p. 8–9).**

| # | § | Anchor phrase | Refs | Rationale |
|---|---|---------------|------|-----------|
| 30 | 3.4 | "Qwen 2.5-Coder-32B was chosen because it is an open model fine-tuned on code..." | [16] | Qwen2.5-Coder technical report. |
| 31 | 3.4 | "Claude Haiku 4.5 was chosen because it is a small commercial model..." | [18] | Anthropic model card. |
| 32 | 3.4 | "DeepSeek-R1-Distill-Llama-70B was chosen because it has been trained with explicit reasoning traces..." | [17] | DeepSeek-R1 paper (the distilled models are described in §3 of that paper). |
| 33 | 3.4 | "All three models were accessed through OpenRouter..." | [32] | — |

**§3.7 Benchmark suite (p. 9).**

| # | § | Anchor phrase | Refs | Rationale |
|---|---|---------------|------|-----------|
| 34 | 3.7 | "Ten CSP instances were drawn from CSPLib, the standard benchmark library..." | [5] | — |
| 35 | 3.7 | "Reusing CSPLib problems rather than designing new ones was chosen because CSPLib makes the present results directly comparable with prior constraint-programming work." | [5] | — |

**§3.9 Tools and reproducibility (p. 10).**

| # | § | Anchor phrase | Refs | Rationale |
|---|---|---------------|------|-----------|
| 36 | 3.9 | "The symbolic component is Choco Solver, a Java constraint-programming library." | [4] | — |
| 37 | 3.9 | "Generated Java models were compiled by Apache Maven..." | [34] | — |
| 38 | 3.9 | "The agent graphs were implemented in LangGraph..." | [30] | — |
| 39 | 3.9 | "LLM calls were routed through OpenRouter..." | [32] | — |
| 40 | 3.9 | "LangSmith was used to trace and store every LLM call." | [31] | — |

### §5 — Discussion

**§5.3 The verifier-redundancy tax (p. 13).**

| # | § | Anchor phrase | Refs | Rationale |
|---|---|---------------|------|-----------|
| 41 | 5.3 | "Multi-agent decomposition is harmful when it competes with an external checker that is already exact and deterministic..." | [21] | Cite LLM-Modulo here — your tax is a CSP-specific instantiation of their general principle. Optional but strongly recommended; it strengthens the discussion. |

**§5.4 Relation to prior literature (p. 13).**

| # | § | Anchor phrase | Refs | Rationale |
|---|---|---------------|------|-----------|
| 42 | 5.4 | "AutoGen, MetaGPT, and ChatDev evaluate decomposition on tasks for which no automatic external checker exists." | [13], [14], [15] | Re-cite. |
| 43 | 5.4 | *(new sentence to add)* "Closer to the present setting, several systems use LLMs to produce CP models from natural language: the Holy Grail 2.0 blueprint [22], integration of LLMs with MiniZinc solvers (MCP-Solver) [25], and most recently the agentic system CP-Agent [26]." | [22], [25], [26] | These three are the closest prior art on LLM-to-CP and **must** be cited; CP-Agent is the closest comparable because it also uses an agentic decomposition. |
| 44 | 5.4 | *(new sentence)* "The supervisor's group has also explored the converse direction — embedding LLMs inside CP search rather than using CP to verify LLM output [23, 24]." | [23], [24] | Cites Régin/Bonlarron/De Maria — politically and intellectually important. |
| 45 | 5.4 | *(new sentence)* "Earlier work on natural-language formulation of optimisation problems (NL4OPT) [27] and recent stress tests of LLM brittleness on CSPLib instances [28] frame the broader landscape into which the present empirical result fits." | [27], [28] | Round out related-work coverage. |

**§5.5 Limitations (p. 14).**

| # | § | Anchor phrase | Refs | Rationale |
|---|---|---------------|------|-----------|
| 46 | 5.5 | "A different scoring protocol (for example, an LLM-as-judge protocol) would be required to evaluate explanation quality." | [29] | Cite Zheng et al. — the standard LLM-as-judge reference. |

### §6 — Conclusion

No new citations needed; restated claims. Optionally re-cite [21], [22], [26] at §6.1 when summarising the verifier-redundancy tax and the prior multi-agent baseline.

---

## Part 3 — Editorial notes for the downstream LLM

1. **House style.** The report uses no inline citations currently; pick one consistent format. Suggested: numerical brackets `[23]` matching the bibliography ordering above. If the supervisor prefers author–year, all entries have full author lists.

2. **Where coverage is thinnest.** §1.1 (motivation) and §6 (conclusion) can be left mostly uncited — these are framing sections. §2 (background) and §5.4 (related work) need the densest citation work. Hit those two sections first.

3. **Must-cite list (do not omit these).** [4] Choco; [5] CSPLib; [7] Brown 2020; [10] Wei 2022; [11] Shinn 2023; [13]–[15] AutoGen / MetaGPT / ChatDev; [16]–[18] the three LLMs; [22] Holy Grail 2.0; [23], [24] Régin group; [26] CP-Agent.

4. **References [23], [24] are politically important** — the supervisor's own group's papers. Their absence in a tutorship report supervised by Pr. Régin would be conspicuous.

5. **Reference [26] (Szeider, CP-Agent, 2025) is the single most direct comparable** to your PDA. The discussion section is materially stronger if you position your monotonic-decline finding explicitly against CP-Agent's design.

6. **Reference [21] (Kambhampati LLM-Modulo) supplies the upstream principle** for your verifier-redundancy tax. The discussion gains theoretical anchoring by citing it.

7. **Optional additions not listed but worth considering** if space permits: Lewkowycz et al. "Solving Quantitative Reasoning Problems with Language Models" (Minerva, 2022) for LLM math reasoning baseline; Yao et al. "ReAct" (ICLR 2023) for the reasoning-and-acting paradigm; Bonlarron, Calabrèse, Kornprobst, Régin "Constraints first" (IJCAI 2023) as a third supervisor-group reference if author-year style.

8. **One small textual fix to consider while inserting refs.** The phrase in §3.2.2 "expected to raise per-agent reliability. The aggregate effect should be a higher end-to-end success rate (on benchmark suite, and solver statistics like time-wall...ect) at L3 than at L0." contains a typo ("...ect") and an unusual parenthetical. Worth cleaning during the bibliography pass.

---

*End of bibliography deliverable.*

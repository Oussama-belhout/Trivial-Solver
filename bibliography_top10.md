# Top-10 Bibliography and Usage Map

**For:** *Automatic Solving of Combinatorial Problems and their Explanations using LLMs and Constraint Programming* — O. Belhout, tutorship final report, M1 Informatique DS4H, Université Côte d'Azur, submission 12 May 2026.

**Built by:** merging the three LLM-generated drafts (LLM1 = detailed 34-entry list, LLM2 = Elicit CSV, LLM3 = Perplexity-style list) into a single 10-entry list optimised for value-per-reference on **this specific report**.

This document has three parts:
1. **Part 1** — the 10 references with full bibliographic info.
2. **Part 2** — citation usage map: section + anchor phrase + which references go where.
3. **Part 3** — what was deliberately cut, and how to recover from the cuts if the page budget allows more later.

---

## Part 1 — The 10 references

### A. Constraint Programming backend

**[R1]** C. Prud'homme, J.-G. Fages. *Choco-solver: A Java library for constraint programming.* Journal of Open Source Software 7(78):4708, 2022. DOI: 10.21105/joss.04708.

**[R2]** I. P. Gent, T. Walsh. *CSPLib: A benchmark library for constraints.* In *Principles and Practice of Constraint Programming (CP'99)*, LNCS 1713, pp. 480–481, Springer, 1999. — www.csplib.org

### B. Prompting techniques actually used in the experiment

**[R3]** J. Wei, X. Wang, D. Schuurmans, M. Bosma, B. Ichter, F. Xia, E. Chi, Q. Le, D. Zhou. *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models.* NeurIPS, 2022. arXiv:2201.11903. — Also serves as the canonical few-shot prompting reference (the CoT paper is built on few-shot examples).

**[R4]** N. Shinn, F. Cassano, A. Gopinath, K. Narasimhan, S. Yao. *Reflexion: Language Agents with Verbal Reinforcement Learning.* NeurIPS, 2023. arXiv:2303.11366.

### C. Multi-agent LLM frameworks (the comparison baseline)

**[R5]** Q. Wu, G. Bansal, J. Zhang, Y. Wu, B. Li, E. Zhu, L. Jiang, X. Zhang, S. Zhang, J. Liu, A. H. Awadallah, R. W. White, D. Burger, C. Wang. *AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation.* arXiv:2308.08155, 2023.

**[R6]** S. Hong, X. Zheng, J. Chen, Y. Cheng, C. Zhang, Z. Wang, S. K. S. Yau, Z. Lin, L. Zhou, C. Ran, L. Xiao, C. Wu. *MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework.* ICLR, 2024. arXiv:2308.00352.

### D. Neuro-symbolic framing

**[R7]** Z. Wan, C.-K. Liu, H. Yang, C. Li, H. You, Y. Fu, C. Wan, T. Krishna, Y. Lin, A. Raychowdhury. *Towards Cognitive AI Systems: a Survey and Prospective on Neuro-Symbolic AI.* arXiv:2401.01040, 2024.

### E. The theoretical anchor for the *verifier-redundancy tax*

**[R8]** S. Kambhampati, K. Valmeekam, L. Guan, M. Verma, K. Stechly, S. Bhambri, L. Saldyt, A. Murthy. *LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks.* ICML, 2024. arXiv:2402.01817.

> Why this is in the top 10: your central original contribution (Section 5.3) is a CSP-specific instantiation of Kambhampati's LLM-Modulo principle. Citing it upgrades §5.3 from "interesting observation" to "empirical confirmation of a known structural principle in a new domain."

### F. Direct prior art on LLM + CP

**[R9]** F. Régin, E. De Maria, A. Bonlarron. *Combining Constraint Programming Reasoning with Large Language Model Predictions.* In *Principles and Practice of Constraint Programming (CP 2024)*, LIPIcs vol. 307, art. 25. DOI: 10.4230/LIPIcs.CP.2024.25. arXiv:2407.13490.

> Why this is in the top 10: this is the supervisor's group's flagship paper on the exact LLM ↔ CP integration question your report addresses. Absence in a tutorship report supervised by Pr. Régin would be conspicuous. Politically *and* intellectually mandatory.

**[R10]** S. Szeider. *CP-Agent: Agentic Constraint Programming.* arXiv:2508.07468, 2025.

> Why this is in the top 10: this is the **single most direct comparable** to your Progressive Delegation Ablation. CP-Agent uses an agentic decomposition for CP modelling; your finding (decomposition *hurts* performance once an exact verifier is present) directly engages with theirs. §5.4 is materially stronger with this contrast.

---

## Part 2 — Citation usage map

Section numbers and page numbers are those of the typeset PDF (page 1 = cover). "Anchor phrase" is a short excerpt that uniquely locates the insertion point.

### §1 — Introduction (p. 3)

| § | Anchor phrase | Refs |
|---|---|---|
| 1.1 | "Special-purpose programs called solvers can search such choice spaces without listing every candidate." | [R1] |
| 1.2 | "An LLM is therefore a plausible candidate to translate a natural-language problem statement into the formal model that a solver requires." | [R3] |
| 1.2 | "The task dispatch between a probabilistic component (the LLM) and a deterministic component (the solver) is the defining feature of neuro-symbolic systems…" | [R7] |
| 1.5 | "A measured finding that contradicts a common assumption in the multi-agent-LLM literature." | [R5], [R6] |

### §2 — Background

#### §2.1 Constraint Satisfaction Problems (p. 4–5)

| § | Anchor phrase | Refs |
|---|---|---|
| 2.1 | "A solver such as Choco searches the space of assignments without listing every candidate." | [R1] |
| 2.1 | "The solver alternates two techniques. The first technique is backtracking… The second technique is constraint propagation…" | [R1] |
| 2.1 | "A small example is the 4-Queens problem, illustrated in Figure 1." | [R2] (CSPLib problem 054) |

#### §2.2 Large Language Models (p. 5)

| § | Anchor phrase | Refs |
|---|---|---|
| 2.2 | "…a property usually called in-context learning." | [R3] (CoT paper relies on and formalises few-shot ICL) |

> *No hallucination-survey reference made the top 10. The report's discussion of "silent semantic errors" is self-contained; if you later expand the page budget, add Ji et al. ACM Computing Surveys 2023.*

#### §2.3 The three design axes in detail (p. 5–6)

| § | Anchor phrase | Refs |
|---|---|---|
| 2.3 | "The first family is few-shot prompting…" | [R3] |
| 2.3 | "The second family is Chain-of-Thought prompting…" | [R3] |
| 2.3 | "The third family is Reflexion-style prompting…" | [R4] |

#### §2.4 Self-correcting systems (p. 6)

| § | Anchor phrase | Refs |
|---|---|---|
| 2.4 | "A self-correcting system contains a loop that reads its own failure signals and tries again." | [R4] |

#### §2.5 Neuro-symbolic perspective (p. 6–7)

| § | Anchor phrase | Refs |
|---|---|---|
| 2.5 | "The system studied here is an instance of a wider class called neuro-symbolic." | [R7] |
| 2.5 | "…how should the probabilistic part and the exact part be coupled so that the exact part remains the source of truth?" | [R8] |

#### §2.6 Related work on multi-agent LLM systems (p. 7)

| § | Anchor phrase | Refs |
|---|---|---|
| 2.6 | "AutoGen provides a generic conversational scaffold." | [R5] |
| 2.6 | "MetaGPT simulates a software-engineering team with explicit role specialisation. ChatDev uses a similar role split for end-to-end software development." | [R6] |
| 2.6 | "None of them includes an automatic, exact external checker that decides correctness without ambiguity." | [R8] |

> **Editorial note on §2.6:** because ChatDev was dropped from the top 10, fold its mention into the MetaGPT citation, e.g. *"MetaGPT [R6] and similar role-specialisation frameworks (ChatDev, …) report…"* — keeps the ChatDev name but spares the bibliography entry.

### §3 — Materials and Methods

| § | Anchor phrase | Refs |
|---|---|---|
| 3.2 | "This hypothesis is the operational form of the assumption that underlies multi-agent frameworks such as AutoGen and MetaGPT." | [R5], [R6] |
| 3.3 | "The monolith uses few-shot prompting with two worked examples…" | [R3] |
| 3.3 | "The refiner uses a Reflexion-style prompt…" | [R4] |
| 3.3 | "The validator uses adversarial Chain-of-Thought prompting…" | [R3] |
| 3.7 | "Ten CSP instances were drawn from CSPLib, the standard benchmark library used in the constraint-programming community." | [R2] |
| 3.7 | "Reusing CSPLib problems… makes the present results directly comparable with prior constraint-programming work." | [R2] |
| 3.9 | "The symbolic component is Choco Solver, a Java constraint-programming library." | [R1] |

> *Model-axis citations (Qwen, Haiku, DeepSeek) and infrastructure citations (LangGraph, LangSmith, OpenRouter, Pydantic, Maven) did not make the top 10. If the page budget allows, add them later as web references; they don't substantively support any claim in the report, only document the stack.*

### §5 — Discussion

#### §5.3 The verifier-redundancy tax (p. 13) — **the strongest payoff zone for the new references**

| § | Anchor phrase | Refs |
|---|---|---|
| 5.3 | "Multi-agent decomposition is harmful when it competes with an external checker that is already exact and deterministic, as in CSP solving against a complete solver." | [R8] |
| 5.3 | "This work names that loss the verifier-redundancy tax." | [R8] (cite to position your tax as the CSP-specific instance of LLM-Modulo) |

#### §5.4 Relation to prior literature (p. 13)

| § | Anchor phrase | Refs |
|---|---|---|
| 5.4 | "AutoGen, MetaGPT, and ChatDev evaluate decomposition on tasks for which no automatic external checker exists." | [R5], [R6] |
| 5.4 | *(add a new sentence)* "Closer to the present setting, the supervisor's group has explored embedding LLMs inside CP search rather than the reverse direction [R9], and a recent agentic CP system, CP-Agent [R10], adopts a decomposition similar to L3 on a different benchmark suite." | [R9], [R10] |
| 5.4 | *(continue)* "The present work supplies the missing controlled comparison: the same five behaviours, the same benchmark suite, the same exact checker, varied only along the agentic depth." | — |

### §6 — Conclusion

No new citations required. Optionally re-cite [R8], [R9], [R10] at §6.1 when summarising the verifier-redundancy tax and positioning the contribution.

---

## Part 3 — Editorial notes for the downstream LLM

### What was deliberately cut, and why

| Reference candidate | Why cut | Recovery path |
|---|---|---|
| ChatDev (Qian et al. 2024) | Named in §2.6 but functionally near-identical to MetaGPT for the report's argument. | Fold mention into [R6] citation; add to bibliography if budget grows. |
| Brown et al. *GPT-3 / Language Models are Few-Shot Learners* (2020) | [R3] (CoT, Wei 2022) is itself a few-shot paper and covers in-context learning. | Add if §2.2 needs a dedicated ICL anchor. |
| Self-Refine (Madaan et al. 2023) | [R4] (Reflexion) covers self-correction with a stronger trace-based fit to your refiner loop. | Add as a paired citation in §2.4 if budget grows. |
| CP Handbook (Rossi, van Beek, Walsh 2006) | [R1] (Choco paper) and [R2] (CSPLib paper) jointly cover the §2.1 CSP definition, backtracking, and propagation. | Add if §2.1 needs a textbook anchor. |
| Hallucination survey (Ji et al. 2023) | The report's "silent semantic errors" passage is self-contained. | Add if you expand §2.2 limitations. |
| Holy Grail 2.0 (Tsouros et al. 2023) | [R10] (CP-Agent) is a stronger, more recent, more directly comparable LLM-to-CP system. | Add as a third related-work citation in §5.4 if budget grows. |
| Russell & Norvig AIMA, Freuder "Holy Grail" 1997 | Textbook / vision-statement; not load-bearing for any specific claim. | Skip. |
| LangGraph / LangSmith / OpenRouter / Pydantic / Maven docs | Infrastructure documentation; not citations to scholarly claims. | Add as URL footnotes in §3.9 if the supervisor prefers explicit stack documentation. |
| Qwen / DeepSeek-R1 / Claude model cards | Model documentation; useful but not load-bearing. | Add as URL footnotes in §3.4 if needed. |

### House style suggestion

Use numerical citations `[R3]` matching the bibliography order in Part 1, or convert to author–year (Wei et al., 2022) if the supervisor prefers. All 10 entries have full author lists ready for either style.

### Densest-citation zones (work on these first)

1. **§2.3** — three prompting families, three citations ([R3], [R3], [R4]).
2. **§2.6** — three multi-agent systems, two citations ([R5], [R6]) plus the verifier-vs-no-verifier observation ([R8]).
3. **§5.3** — the verifier-redundancy tax paragraph, one critical citation ([R8]).
4. **§5.4** — related-work paragraph, four citations ([R5], [R6], [R9], [R10]).

If you only have time for one section, do **§5.4**: that paragraph turns from a generic acknowledgement into a positioned scholarly contribution.

### One textual fix to consider while inserting refs

§3.2.2 contains: *"expected to raise per-agent reliability. The aggregate effect should be a higher end-to-end success rate (on benchmark suite, and solver statistics like time-wall...ect) at L3 than at L0."* — the parenthetical is malformed ("...ect" → "etc.") and the meaning is unclear. Worth cleaning during the bibliography pass.

---

*End of deliverable. Hand this file to the next LLM with the instruction:*

> *"Insert citations into the attached PDF/LaTeX source using the anchor-phrase map in Part 2. Use numerical brackets `[Rn]` matching the bibliography in Part 1. Generate a References section at the end of the document from Part 1. Optionally suggest BibTeX entries from the DOIs and arXiv IDs listed."*

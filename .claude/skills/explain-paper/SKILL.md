---
name: explain-paper
description: Turn a research paper PDF in papers_pdf/ into a beginner-friendly explainer markdown in papers_and_articles/, matching the house style of reflexion.md and generative_agents.md (tables, GitHub callouts, "In plain English" analogies, ASCII diagrams, Context-Engineering mapping, cross-paper Connections). Use when you've dropped a new paper PDF in papers_pdf/ and want the .md study version.
disable-model-invocation: true
---

The user wants a research-paper PDF turned into a study-style explainer markdown. Arguments: $ARGUMENTS

## Purpose

`papers_pdf/` holds raw research-paper PDFs. `papers_and_articles/` holds the digested, beginner-friendly `.md` versions used for actual study. This skill produces one `.md` from one PDF, in the exact house style established by `reflexion.md` and `generative_agents.md`, plus a few agreed enhancements (frontmatter, At-a-Glance, glossary, Business Problem stub, From-Paper-to-Practice stub, project-module links).

The companion skill `/paper-to-build` later fills in the Business Problem + From-Paper-to-Practice sections and scaffolds a runnable notebook. This skill writes those two sections as **stubs** so the handoff is clean.

## Instructions

### 1. Locate the PDF

Parse `$ARGUMENTS`. Accept a full filename, a path, or a fuzzy fragment of the title. Match it against files in `papers_pdf/` (use Glob). If empty or ambiguous, list the PDFs in `papers_pdf/` and ask which one. Derive a **slug** from the paper's short title in snake_case (e.g. "Graph RAG-Tool Fusion" → `graph_rag_tool_fusion`). The output path is `papers_and_articles/<slug>.md`. If that file already exists, confirm before overwriting.

### 2. Read the source material — both layers

- **Study the template first.** Read `papers_and_articles/reflexion.md` AND `papers_and_articles/generative_agents.md` in full. These are the ground truth for tone, section order, table density, callout usage, and the "🗣️ In plain English" analogy blocks. Match them — do not invent a new style.
- **Read the PDF.** Use the Read tool with the `pages` parameter. For papers over 10 pages, read in batches (≤20 pages/request). Extract: the core idea, the problem it solves, the architecture/method, every benchmark/ablation table, limitations, and the references (find the arXiv id / DOI).

### 3. Write the .md — exact house structure

Reproduce this section order. Every section is heavy on **markdown tables**, uses **GitHub callouts** (`> [!IMPORTANT]`, `[!NOTE]`, `[!TIP]`, `[!WARNING]`, `[!CAUTION]`), and includes **🗣️ In plain English:** analogy blocks after each hard concept. Use fenced ASCII diagrams for loops/flows (as reflexion.md does).

1. **Frontmatter metadata** *(enhancement A)* — a fenced metadata block immediately under the H1 title:
   ```
   > **Paper:** <full title> · **Authors:** <first author et al.> · **Year:** <year>
   > **Link:** [arXiv:XXXX.XXXXX](url) · **Difficulty:** ★★★☆☆ · **Reading time:** ~N min
   > **Roadmap phase:** Phase 1 — Agent Foundations · **Module link:** <relevant module or —>
   ```
2. **H1 title** — catchy + descriptive, in the style of "Reflexion: Teaching LLM Agents to Learn from Their Mistakes — Using Words, Not Gradients".
3. **At a Glance** *(enhancement B)* — a `> [!NOTE]` callout or short bullet list, 3–4 bullets, that lets a reader grok the paper in 30 seconds.
4. `## The Core Idea` — a defining table + a one-paragraph plain summary. Add a `> 🖼️ *Suggested figure:* <one-line description>` placeholder where an architecture diagram belongs (see §4 on images).
5. `## Key Terms` *(enhancement C)* — a glossary table (`Term | Plain-English meaning`) covering the paper's jargon, placed before the deep mechanics.
6. `## Why Does This Matter?` — a problem table, an `[!IMPORTANT]` callout with the key insight, and a **🗣️ In plain English:** analogy.
7. `## How Does It Work?` (and sub-sections) — the method/architecture, broken into components with tables, ASCII diagrams, callouts, and analogies. One sub-section per major component.
8. `## The Evidence` — benchmark result tables and the ablation study, framed as "what actually matters". Keep the paper's real numbers.
9. Advantages / Limitations — two tables (what's great, what breaks).
10. `## The Business Problem` *(enhancement D — STUB)* — insert exactly this placeholder so `/paper-to-build` can fill it:
    ```
    > [!TIP]
    > **Scaffolded by `/paper-to-build <slug>`.** A short trading-platform / wealth-management
    > problem statement (synthetic data only) will be written here, paired with the notebook below.
    ```
11. `## From Paper to Practice` *(enhancement E — STUB)* — insert this placeholder:
    ```
    > [!TIP]
    > **Scaffolded by `/paper-to-build <slug>`.** A minimal LangGraph / LangChain build that
    > exercises *every* core aspect of this paper lands here, linked to `builds/<slug>.ipynb`.
    ```
12. `## Connection to Context Engineering` — map the paper onto the four strategies (✍️ Write, 🎯 Select, 🗜️ Compress, 🧱 Isolate) in a table, exactly like reflexion.md / generative_agents.md. Add an `[!NOTE]` on which context failure mode (poisoning, distraction, confusion, clash) it addresses.
13. `## Connection to <other papers>` — one comparison table per closely related paper already in `papers_and_articles/` (reflexion, generative_agents, think_tool, context_engineering). Only include genuinely related ones.
14. `## Connection to This Project's Modules` *(enhancement F)* — a short table mapping the paper's ideas to the repo's learning modules (e.g. `scratchpad/`, `context_isolation/`, `subagent_delegation/`). Check which module dirs actually exist (Glob the repo root) before linking.
15. A bold **The takeaway:** closing paragraph (one dense paragraph, like the examples).
16. `## References` — the arXiv/DOI link(s), formatted like the examples.

### 4. Images

The example files reference real PNGs in `../images/`. New papers have none, and this skill does not generate images. So:
- **Do not** reference image files that don't exist.
- Instead, render flows/loops/architectures as **fenced ASCII diagrams** (reflexion.md already does this for its loop), and drop `> 🖼️ *Suggested figure: ...*` placeholders where a real diagram would later help.
- Image paths, if any are ever added, are relative from `papers_and_articles/` so use `../images/<name>.png`.

### 5. Quality bar

Before finishing, self-check against the examples:
- [ ] Section order matches §3.
- [ ] At least one table in most sections; at least three "🗣️ In plain English:" analogies.
- [ ] Real numbers from the paper in the Evidence tables (no invented stats).
- [ ] The four-strategy Context Engineering mapping is present.
- [ ] Business Problem + From Paper to Practice are STUBS (not filled — that's `/paper-to-build`'s job).
- [ ] No broken image references.
- [ ] arXiv/DOI link is correct.

### 6. Report

State the created file path, the slug, and remind the user they can now run `/paper-to-build <slug>` to scaffold the trading/wealth-management build that fills in the two stubbed sections.

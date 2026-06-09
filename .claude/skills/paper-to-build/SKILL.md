---
name: paper-to-build
description: Scaffold a small, runnable LangGraph/LangChain build that turns a research paper into a hands-on comprehension check. Writes a SHORT trading-platform / wealth-management problem statement (synthetic data only) and a companion notebook whose sections map to EVERY core aspect of the paper, then fills the Business Problem and From-Paper-to-Practice sections of the paper's .md. Use after /explain-paper, when you want to implement a paper to validate your understanding.
disable-model-invocation: true
---

The user wants to scaffold a hands-on build for a research paper. Arguments: $ARGUMENTS

## Purpose

Reading a paper is passive; implementing it is the real comprehension test. This skill produces a **scaffold** (not a finished solution — the user builds that) consisting of:

1. A **short** problem statement from a **trading-platform / wealth-management** context (2–4 sentences max, synthetic/public data only).
2. A **coverage map** — every core aspect/mechanism of the paper mapped to a notebook section, so that completing the build forces the user to touch *all* of the paper's ideas. This is the comprehension check.
3. A companion **Jupyter notebook** scaffold (`builds/<slug>.ipynb`) with one section per aspect: a markdown cell explaining the aspect + how it maps to the problem, then a skeleton code cell with a precise `# TODO:` describing what to implement.
4. The now-filled **Business Problem** and **From Paper to Practice** sections in `papers_and_articles/<slug>.md`.

> ⚠️ **Compliance (from CLAUDE.md):** use ONLY synthetic or public data. No real client data, MNPI, or production systems. Trading/wealth examples are decision-support only.

## Instructions

### 1. Locate the paper

Parse `$ARGUMENTS` for a slug, title fragment, or path. The explainer `.md` must already exist at `papers_and_articles/<slug>.md` (produced by `/explain-paper`). If it doesn't, tell the user to run `/explain-paper` first (offer to do it). Also locate the source PDF in `papers_pdf/` for any detail the `.md` omits.

### 2. Extract the aspect inventory

Read `papers_and_articles/<slug>.md` (and the PDF if needed). List **every core aspect/mechanism** of the paper — the things a faithful implementation must contain. Be exhaustive but atomic. Examples of what "aspect" means:
- Reflexion → Actor, Evaluator, Self-Reflection model, short-term memory, long-term (episodic) memory, the trial loop, bounded-memory compression, stop condition.
- A RAG-Tool-Fusion paper → tool knowledge base, retrieval/index, query→tool matching, fusion/re-ranking, tool execution, fallback.

This inventory is the contract: the notebook must have a section for each item.

### 3. Frame the business problem — SHORT, trading / wealth management

Write a **2–4 sentence** problem statement set in a trading platform or wealth-management context that the paper's technique naturally solves. Keep it small and quick to build — the goal is comprehension, not a product. Use synthetic data only. Examples of the *shape* (adapt to the paper):
- "A wealth-management copilot must pick the right analytics tool from 40+ (rebalancing, tax-loss harvesting, risk attribution…) for each advisor query. Naïve prompting mis-selects as the toolset grows."
- "A trading-desk research agent keeps repeating the same flawed reasoning when a backtest fails. It should learn from each failed run within a session."

Do **not** make it lengthy. One tight paragraph.

### 4. Build the coverage map

Produce a table: `Paper aspect | Role in the build | Notebook section`. Every aspect from §2 must appear. This table goes into both the `.md` (From Paper to Practice section) and the notebook (a "Coverage Map" cell). It is the user's checklist that the implementation covers the whole paper.

### 5. Scaffold the notebook

Create `papers_and_articles/builds/<slug>.ipynb` (Write will create the `builds/` dir). Structure:

1. **Title markdown cell** — `# <Paper title> — Hands-on Build`, plus: date, a link back to `../<slug>.md`, and the short problem statement from §3.
2. **Imports code cell** — reuse the project's standard header (mirror `.claude/skills/new-module/SKILL.md`): `os`, `time`, typing, `dotenv.load_dotenv()`, langchain_core messages/prompts/tools, model providers (`ChatOpenAI`, `ChatAnthropic`, `ChatMistralAI`), langgraph (`StateGraph`, `START`, `END`, `add_messages`, `ToolNode`, `MemorySaver`, `Send`), and the `assert os.getenv(...)` key checks.
3. **LLM instances code cell** — reuse the new-module LLM block (OpenAI / Anthropic / Mistral instances).
4. **Synthetic data cell** — a small markdown note + code cell generating the synthetic trading/WM data the build uses (a handful of holdings, a toy tool catalog, etc.). Keep it tiny.
5. **Coverage Map markdown cell** — the table from §4, framed as "complete every section below to cover the whole paper."
6. **One section per aspect** (from §2), each = two cells:
   - a markdown cell: aspect name, 1–2 sentences on what it is, and how it maps to the trading/WM problem;
   - a code cell: a skeleton with a precise `# TODO:` naming exactly what to implement (function signature or graph node stub where helpful), left for the user to complete.
7. **Wire-up cell** — a skeleton that assembles the pieces into a LangGraph `StateGraph` (TypedDict state, nodes, edges) with `# TODO`s, so the user connects the aspects into one runnable agent.
8. **Validation markdown cell** — an end-to-end run instruction + a checklist with one box per aspect ("☐ Actor produces an action", "☐ Reflection is stored and reused", …). Completing the checklist == understanding confirmed.

Follow the repo's notebook JSON shape (nbformat 4, nbformat_minor 5; kernelspec python3) exactly as in `new-module`. Code cells: `"execution_count": null`, `"outputs": []`.

### 6. Fill the .md stubs

Edit `papers_and_articles/<slug>.md`:
- Replace the **`## The Business Problem`** stub with the §3 problem statement (and a one-line synthetic-data/compliance note).
- Replace the **`## From Paper to Practice`** stub with: a one-paragraph intro, the §4 coverage-map table, and a link to `builds/<slug>.ipynb`. Optionally include a tiny condensed code snippet (the state TypedDict or the core node) — but the runnable code lives in the notebook.

### 7. Report

State: the notebook path, the number of aspects covered (so the user sees the full paper is represented), the filled `.md` sections, and a reminder that the build uses synthetic data only and is the comprehension check — they implement the `# TODO`s, then tick the validation checklist.

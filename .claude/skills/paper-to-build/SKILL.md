---
name: paper-to-build
description: Scaffold a small, runnable LangGraph/LangChain build that turns a research paper into a hands-on comprehension check. Writes a SHORT trading-platform / wealth-management problem statement (synthetic data only) and a companion notebook whose sections map to EVERY core aspect of the paper — each section is library-first (no rebuilding primitives from scratch), agent-concept-focused, and carries an explicit Input → Output contract plus a "why this matters" line. Then fills the Business Problem and From-Paper-to-Practice sections of the paper's .md. Use after /explain-paper, when you want to implement a paper to validate your understanding.
disable-model-invocation: true
---

The user wants to scaffold a hands-on build for a research paper. Arguments: $ARGUMENTS

## Purpose

Reading a paper is passive; implementing it is the real comprehension test. This skill produces a **scaffold** (not a finished solution — the user builds that) consisting of:

1. A **short** problem statement from a **trading-platform / wealth-management** context (2–4 sentences max, synthetic/public data only).
2. A **coverage map** — every core aspect/mechanism of the paper mapped to a notebook section, so that completing the build forces the user to touch *all* of the paper's ideas. This is the comprehension check.
3. A companion **Jupyter notebook** scaffold (`builds/<slug>.ipynb`) with one section per aspect, each carrying a clear **Input → Output contract**, a one-line **bigger-picture** note, the **library to lean on**, and a skeleton code cell whose `# TODO:` is *glue-level wiring*, not a from-scratch reimplementation.
4. The now-filled **Business Problem** and **From Paper to Practice** sections in `papers_and_articles/<slug>.md`.

> ⚠️ **Compliance (from CLAUDE.md):** use ONLY synthetic or public data. No real client data, MNPI, or production systems. Trading/wealth examples are decision-support only.

## Design principles — read before scaffolding

These exist because the earlier version produced vague, time-consuming notebooks that demanded micro-level reimplementation of things a library already does. Don't repeat that.

1. **Don't start from zero — library-first.** For any mechanical primitive (embeddings, vector search, BM25, similarity, ranking metrics, re-rankers, tokenization, the agent loop), the TODO must **call an existing library**, not reimplement it. Reserve hand-written code for the *agent-level concept* the paper is actually about. A TODO like "implement the BM25 formula" or "build an L2-normalized matrix and compute cosine by hand" is **banned** — use `langchain_community`'s `BM25Retriever`, `InMemoryVectorStore`/`FAISS`, `sklearn.metrics.ndcg_score`, a `sentence-transformers` CrossEncoder, etc. See the cheat-sheet in §0.

2. **Stay at the agent / concept altitude.** Decompose the paper into **agent-relevant concepts** (the ideas worth understanding), not low-level numerics. The user's job is to wire concepts together into an agent, not to re-derive primitives. If an aspect is purely mechanical, hand it to a library and spend the section's words on *why it matters to the agent*.

3. **Every section is a contract, not a riddle.** Each section states, explicitly and concretely: **Input** (type + a tiny example), **Output** (type + a tiny example), and the **library/function** to use. No vague "implement X" — the user must always know what goes in, what comes out, and what tool does the heavy lifting.

4. **Always show the bigger picture.** Each section gets a one-line **"Why this matters"** tying it to the end-to-end agent (what breaks without it). The notebook must read top-to-bottom as a story: *raw inputs → … → an agent that does the thing*, so the user never loses the plot while filling TODOs.

5. **Small and fast to finish.** Prefer fewer, meatier sections over many micro-steps. A section the user can complete in a few lines of library glue is the target. If a section would take an hour of from-scratch code, it's mis-scoped — shrink it or library-ize it.

## Instructions

### 0. Library cheat-sheet (prefer these over hand-rolled code)

When an aspect needs one of these primitives, the TODO must point at the library, not ask for a reimplementation:

| Need | Use (don't hand-roll) |
|---|---|
| Embeddings | `OpenAIEmbeddings` (already in the project header) |
| Vector store + cosine top-k | `InMemoryVectorStore` / `FAISS` (`langchain_community`) `.as_retriever()` |
| Sparse / lexical retrieval (BM25) | `langchain_community.retrievers.BM25Retriever` or `rank_bm25` |
| Hybrid retrieval | `EnsembleRetriever` |
| Ranking metrics (nDCG/Recall/Precision) | `sklearn.metrics` (`ndcg_score`, etc.) |
| Cross-encoder re-rank | `sentence-transformers` `CrossEncoder`, or an LLM judge via the project's `llm*` instances |
| Agent / tool-calling loop | `langchain`'s `create_agent`, or `langgraph` `ToolNode` + `StateGraph` — not a manual while-loop unless the loop *is* the concept |
| Memory / checkpointing | `langgraph.checkpoint.memory.MemorySaver` |
| Text similarity / fuzzy overlap | `difflib`, `rapidfuzz`, or `sklearn` — not a hand-written LCS |

The carve-out: if the paper's actual contribution *is* one of these mechanisms (e.g. a paper whose novelty is a new ranking metric), then implementing that one piece is the point — keep it, and library-ize everything around it.

### 1. Locate the paper

Parse `$ARGUMENTS` for a slug, title fragment, or path. The explainer `.md` must already exist at `papers_and_articles/<slug>.md` (produced by `/explain-paper`). If it doesn't, tell the user to run `/explain-paper` first (offer to do it). Also locate the source PDF in `papers_pdf/` for any detail the `.md` omits.

### 2. Extract the aspect inventory — at the agent/concept altitude

Read `papers_and_articles/<slug>.md` (and the PDF if needed). List the paper's core aspects as **agent-relevant concepts** — the ideas a reader must understand, not the numerics underneath them. Each aspect should be completable as **library glue around one clear idea**. Examples:
- Reflexion → Actor, Evaluator, Self-Reflection step, episodic memory, the trial loop, stop condition. (The "memory" is a list + a `MemorySaver`, not a hand-built store.)
- A tool-retrieval paper → tool catalog, dense retrieval (vector store), lexical baseline (BM25 library), instruction augmentation, ranking metrics (`sklearn`), the retrieval→agent handoff, the pass-rate gap.

For each aspect, note **which library** (from §0) carries its mechanics, so the section can be glue-level. If two aspects are both trivial library calls, consider merging them. This inventory is the contract: the notebook has a section per item.

### 3. Frame the business problem — SHORT, trading / wealth management

Write a **2–4 sentence** problem statement set in a trading platform or wealth-management context that the paper's technique naturally solves. Keep it small and quick to build — the goal is comprehension, not a product. Use synthetic data only. Examples of the *shape* (adapt to the paper):
- "A wealth-management copilot must pick the right analytics tool from 40+ (rebalancing, tax-loss harvesting, risk attribution…) for each advisor query. Naïve prompting mis-selects as the toolset grows."
- "A trading-desk research agent keeps repeating the same flawed reasoning when a backtest fails. It should learn from each failed run within a session."

Do **not** make it lengthy. One tight paragraph.

### 4. Build the coverage map

Produce a table: `Paper aspect | Agent-level role in the build | Library leaned on | Notebook section`. Every aspect from §2 must appear. This table goes into both the `.md` (From Paper to Practice section) and the notebook (a "Coverage Map" cell). It is the user's checklist that the implementation covers the whole paper *and* a glance at how little from-scratch work remains (the Library column should rarely say "from scratch").

### 5. Scaffold the notebook

Create `papers_and_articles/builds/<slug>.ipynb` (Write will create the `builds/` dir). Structure:

1. **Title markdown cell** — `# <Paper title> — Hands-on Build`, plus: date, a link back to `../<slug>.md`, and the short problem statement from §3.
2. **Imports code cell** — reuse the project's standard header (mirror `.claude/skills/new-module/SKILL.md`): `os`, `time`, typing, `dotenv.load_dotenv()`, langchain_core messages/prompts/tools, model providers (`ChatOpenAI`, `ChatAnthropic`, `ChatMistralAI`), `OpenAIEmbeddings`, langgraph (`StateGraph`, `START`, `END`, `add_messages`, `ToolNode`, `MemorySaver`, `Send`), and the `assert os.getenv(...)` key checks. Add the specific helper libraries this build leans on (from §0, e.g. `from sklearn.metrics import ndcg_score`).
3. **LLM instances code cell** — reuse the new-module LLM block (OpenAI / Anthropic / Mistral instances).
4. **"Bigger picture" markdown cell** — 3–4 sentences (or a tiny flow diagram in text: `data → retrieve → rerank → agent → score`) stating what the finished notebook does end-to-end and what each stage contributes. This is the narrative spine the sections hang off.
5. **Synthetic data cell** — a small markdown note + code cell generating the synthetic trading/WM data the build uses (a handful of holdings, a toy tool catalog, etc.). Keep it tiny.
6. **Coverage Map markdown cell** — the table from §4, framed as "complete every section below to cover the whole paper."
7. **One section per aspect** (from §2), each = two cells:
   - a **markdown cell** using this exact template so no section is vague:
     ```markdown
     ### S<n> . <Aspect name>

     **Concept:** <1–2 sentences — what this is in the paper, at the agent/concept level.>
     **Why it matters:** <one line — what the end-to-end agent loses if this is missing.>
     **Input:** <type + tiny concrete example, e.g. `query: str` — "Trim my tech exposure">
     **Output:** <type + tiny concrete example, e.g. `List[str]` of tool IDs — `['T01','T02']`>
     **Use:** <the library/function from §0 that does the mechanics, e.g. `InMemoryVectorStore.as_retriever()`>
     ```
   - a **code cell**: a skeleton whose `# TODO:` is **glue-level** and restates the I/O contract inline. The TODO must name the library call to make, not a primitive to reimplement. Shape:
     ```python
     def <fn>(<typed args>) -> <typed return>:
         # TODO (glue, not from scratch): use <library> to <do the one thing>.
         # Input:  <contract>
         # Output: <contract>
         ...
     ```
     Provide a real function signature / graph-node stub with concrete types so the contract is unambiguous.
8. **Wire-up cell** — a skeleton that assembles the pieces into a LangGraph `StateGraph` (TypedDict state, nodes, edges) with `# TODO`s, so the user connects the aspects into one runnable agent. Prefer `create_agent`/`ToolNode` over a manual loop unless the loop is the paper's concept.
9. **Validation markdown cell** — an end-to-end run instruction + a checklist with one box per aspect ("☐ Dense retriever returns tool IDs", "☐ Reflection is stored and reused", …), each phrased as an observable input→output behavior. Completing the checklist == understanding confirmed.

Follow the repo's notebook JSON shape (nbformat 4, nbformat_minor 5; kernelspec python3) exactly as in `new-module`. Code cells: `"execution_count": null`, `"outputs": []`.

### 6. Fill the .md stubs

Edit `papers_and_articles/<slug>.md`:
- Replace the **`## The Business Problem`** stub with the §3 problem statement (and a one-line synthetic-data/compliance note).
- Replace the **`## From Paper to Practice`** stub with: a one-paragraph intro (the end-to-end "bigger picture" story), the §4 coverage-map table (with the Library column), and a link to `builds/<slug>.ipynb`. Optionally include a tiny condensed code snippet (the state TypedDict or the core node) — but the runnable code lives in the notebook.

### 7. Report

State: the notebook path, the number of aspects covered (so the user sees the full paper is represented), how many sections are pure library-glue vs. genuinely from-scratch (should be mostly glue), the filled `.md` sections, and a reminder that the build uses synthetic data only and is the comprehension check — they implement the glue `# TODO`s, then tick the validation checklist.

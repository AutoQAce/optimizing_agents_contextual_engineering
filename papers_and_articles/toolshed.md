# Toolshed: Giving an Agent a 4,000-Tool Library Without Drowning It — Treating Tool Selection as a RAG Problem

> **Paper:** Toolshed: Scale Tool-Equipped Agents with Advanced RAG-Tool Fusion and Tool Knowledge Bases · **Authors:** Elias Lumer et al. (PwC Innovation Hub) · **Year:** 2024
> **Link:** [arXiv:2410.14594](https://arxiv.org/abs/2410.14594) · **Difficulty:** ★★★☆☆ · **Reading time:** ~14 min
> **Roadmap phase:** Phase 1 — Agent Foundations · **Module link:** `context_isolation/` *(planned)* — the 🎯 Select strategy for tools

---

## At a Glance

> [!NOTE]
> - **The problem:** model providers cap an agent at ~128 tool definitions per API call (OpenAI recommends ≤20 for accuracy). But real systems may have *thousands* of tools. How do you give a single agent a 4,000-tool library without stuffing them all into the prompt?
> - **The insight:** picking the right tool from thousands is the *same* "needle-in-a-haystack" problem as retrieval-augmented generation (RAG). So borrow the entire advanced-RAG toolkit and apply it to **tools** instead of documents.
> - **The method:** two pieces — a **Toolshed Knowledge Base** (a vector DB of *enriched* tool descriptions) plus **Advanced RAG-Tool Fusion** (an ensemble of RAG tricks across pre-, intra-, and post-retrieval). **No fine-tuning.**
> - **The payoff:** +46% / +56% / +47% absolute Recall@5 over a BM25 baseline on three tool benchmarks — while letting you dial down `top-k` to save tokens and latency.

---

## The Core Idea

| Concept | What It Means |
|---|---|
| **The constraint** | An LLM agent can only be handed ~128 tool definitions per request — and accuracy degrades well before that. Thousands of tools simply won't fit. |
| **The reframe** | "Which tool do I use?" is the same retrieval problem as "which document answers this question?" — a needle in a haystack. |
| **Toolshed Knowledge Base** | A vector database where each tool is stored not as a bare name+description, but as an **enriched document** (name, description, argument schema, synthetic questions, key topics). |
| **Advanced RAG-Tool Fusion (ARTF)** | An **ensemble** of advanced-RAG techniques applied to tool selection across three phases: **pre-retrieval** (enrich + index), **intra-retrieval** (rewrite, decompose, expand the query), **post-retrieval** (rerank, dedupe, self-reflect). |
| **The two knobs** | `tool-M` = how many tools exist in total; `top-k` = how many you actually retrieve and hand to the agent. Tuning `top-k` trades off accuracy vs. token cost. |

In one paragraph: instead of fine-tuning a model to memorize tools (expensive, brittle) or cramming every tool into the prompt (impossible at scale), Toolshed stores tools in a vector database as *rich* documents and retrieves only the handful relevant to each query — using a stack of proven RAG techniques. The agent never sees 4,000 tools; it sees the 5 that matter.

> 🖼️ *Suggested figure:* the ARTF pipeline — a user query flowing left-to-right through **Pre-retrieval** (enriched tool docs indexed into the Toolshed KB) → **Intra-retrieval** (query rewrite → decompose → multi-query expand) → **Toolshed KB lookup** → **Post-retrieval** (rerank → dedupe → self-reflect) → a final `top-k` toolset handed to the agent. (Paper Fig. 1 & Fig. 2.)

---

## Key Terms

| Term | Plain-English meaning |
|---|---|
| **Tool / function calling** | The agent emits a structured JSON request ("call `get_price(ticker="AAPL")`") instead of free text; the runtime executes the function and feeds the result back. |
| **Tool selection / retrieval** | Choosing *which* tools to even show the agent for a given request — the focus of this paper (not the actual calling). |
| **`tool-M`** | The total number of tools available in the knowledge base (can be thousands). |
| **`top-k`** | The number of tools retrieved from the KB and equipped to the agent for one request (must be ≤128). |
| **Recall@k** | Of the truly-correct tools for a query, what fraction appear in the top-k retrieved? The paper's headline metric. |
| **BM25** | A classic keyword/term-matching retrieval algorithm — the lexical baseline ARTF beats. |
| **DPR (Dense Passage Retrieval)** | Neural embedding-based retrieval; the Seal-Tools benchmark's own retriever, used as a strong baseline. |
| **HyDE / reverse-HyDE** | RAG tricks: generate a *hypothetical answer* to embed (HyDE), or attach *hypothetical questions* to a document so queries match it better (reverse-HyDE). |
| **Query decomposition** | Splitting a complex request into independent sub-steps, each needing its own tool. |
| **Multi-query expansion** | Rewriting one sub-query into several phrasings to catch the many ways a tool could be described. |
| **Reranking** | Re-ordering retrieved candidates by true relevance (via cross-encoder embeddings or an LLM) before handing them on. |
| **Self-RAG / Corrective RAG** | Letting the agent judge whether retrieval was sufficient and, if not, fetch more — self-reflection on the retrieval itself. |
| **Simple / Base Agent** | An agent given M static tools directly in the API call, with no retrieval layer — the thing ARTF replaces at scale. |

---

## Why Does This Matter?

Tool-equipped agents are everywhere now — querying databases, pushing code, answering domain Q&A. But scaling the *number* of tools hits a hard wall:

| Problem | Impact |
|---|---|
| **128-tool API ceiling** | OpenAI/Anthropic/Gemini cap function definitions at ~128 per request — and OpenAI advises ≤20 for complex tasks. A 1,000-tool agent is impossible this way. |
| **Multi-agent doesn't fix it** | Splitting tools across sub-agents (AutoGen, LangGraph, CrewAI) helps, but *each* sub-agent still hits the same 128 ceiling. |
| **Fine-tuning is expensive & brittle** | Tuning-based approaches (ToolLLM, Gorilla) bake tools into weights — costly, and stale the moment your tool catalog changes. |
| **Naive tool retrieval is weak** | Prior retrievers embed only 1–2 fields (tool name + description). That's a thin signal — easy to miss the right tool. |
| **Nobody studied the cost knob** | There was little research on how `tool-M` and `top-k` actually trade off against accuracy, token cost, and latency. |

> [!IMPORTANT]
> The key insight: **tool selection is just RAG wearing a different hat.** The advanced-RAG community already solved "find the right needle in a 10,000-document haystack." Toolshed's contribution is recognizing that a tool catalog *is* that haystack, and porting the whole RAG playbook — enrichment, query decomposition, reranking, self-reflection — onto tools, with **no model fine-tuning** required.

**🗣️ In plain English:**

Imagine a workshop with 4,000 labeled tools hanging on the walls. A naive approach hands the apprentice all 4,000 and says "pick the right one" — they're overwhelmed and grab the wrong wrench. Fine-tuning is like making the apprentice memorize all 4,000 over months of training (and re-training every time you buy a new tool). Toolshed instead hires a sharp **tool-room clerk**: you describe the job, the clerk fetches the 5 most likely tools from a well-organized cabinet, and the apprentice picks from those 5. The clerk doesn't need to be a genius — they just need a good catalog and a good search system.

---

## How Does It Work?

Toolshed has two halves: the **Toolshed Knowledge Base** (where tools live) and **Advanced RAG-Tool Fusion** (the three-phase retrieval pipeline that feeds the agent).

```
                    ┌─────────────────────────────────────────────┐
   4,000 raw tools  │           TOOLSHED KNOWLEDGE BASE            │
   ───────────────► │   each tool = enriched document, embedded   │
   (PRE-RETRIEVAL)  └─────────────────────────────────────────────┘
                                       ▲   │
                                       │   │ retrieve top-k
                          query the KB │   ▼
   user query ──► [INTRA-RETRIEVAL] ──►│  candidate tools ──► [POST-RETRIEVAL] ──► final top-k ──► AGENT
                   rewrite                                      rerank
                   decompose                                    dedupe
                   multi-query expand                           self-reflect
                   step-back
```

### 1. Pre-retrieval — building a *rich* tool document

The assumption ARTF rejects: that storing just a tool's name + description is enough. Instead, each tool becomes a 5-component document before it's embedded and indexed:

| Component | What it adds | Why it helps retrieval |
|---|---|---|
| **1. Tool name** | e.g. `GetRecord` → embedded as "Get Record" (spaces added) | Cleaner tokens sit better in vector space |
| **2. Description** | Long, high-quality, says *when to use and when not to* | The richest semantic signal |
| **3. Argument schema** | Parameter names + descriptions, no abbreviations | Lets parameter-laden queries match |
| **4. Synthetic questions** | LLM-generated *hypothetical questions this tool answers* | Reverse-HyDE — moves the tool closer to real user queries in vector space |
| **5. Key topics / intents** | LLM-generated themes for the tool | Broadens the match surface |

A crucial detail: each tool document carries a **metadata dictionary** mapping the embedded display name back to the *true* code name (`"get_record"` → the actual Python function). Retrieval finds the document; the dictionary resolves it to a callable.

> [!TIP]
> If a tool's description is short, vague, or overlaps another tool, the paper recommends having an LLM **re-write it** into something longer and unique before indexing. Garbage descriptions in → garbage retrieval out.

**🗣️ In plain English:** Instead of filing each tool under just its name, you write it a little dating profile — what it does, what questions it answers, what topics it covers, what arguments it takes. A richer profile gets matched to far more relevant queries.

### 2. Intra-retrieval — transforming the query before you search

The assumption: users phrase things sloppily and pack multiple needs into one sentence. Querying the KB with the raw user text retrieves poorly. So ARTF transforms the query first:

```
"What's a neural network, and find me the AAPL closing price for last Friday?"
        │
        ├─ (a) Query rewrite      → fix typos, pronouns, use chat history
        │
        ├─ (b) Decompose          → Step 1: "explain neural network"
        │                            Step 2: "get AAPL closing price, last Friday"
        │
        ├─ (c) Multi-query expand → Step 1 variants: {research tool? web search?
        │      (per sub-step)        course tool? tutor tool? NN-specific tool?}
        │
        └─ (d) Step-back (optional) → abstract the question before reasoning
                            │
                            ▼
                  query Toolshed KB for each variant → top-k tools each
```

| Technique | Borrowed from RAG as | "Must-have"? |
|---|---|---|
| Query rewriting | Ma et al. query rewrite | If users use shorthand/pronouns |
| **Query decomposition / planning** | IRCoT, ReWOO, REAPER | **Yes** — the key differentiator on Seal-Tools |
| Multi-query expansion / variation | Query2doc, RAG-Fusion | If multiple non-identical tools could fit |
| Step-back prompting | Step-back prompting | Optional, for abstract questions |

> [!NOTE]
> The expansion module has **no awareness of what tools exist** in the KB. That's deliberate — it blindly generates diverse phrasings of intent, casting a wide net so that *whatever* the right tool is, some phrasing lands near it.

**🗣️ In plain English:** Before you search the tool cabinet, you clean up the request ("you mean *it* = the AAPL stock, right?"), break it into separate errands, and for each errand you brainstorm several ways to describe it — because the perfect tool might be filed under a word you didn't think of.

### 3. Post-retrieval — finalizing the toolset

Intra-retrieval over-fetches: each query variant pulls its own top-k, so you end up with a big, duplicate-ridden candidate pile. Post-retrieval condenses it:

| Step | What happens |
|---|---|
| **Rerank** | An LLM-based reranker (or a cross-encoder) re-orders candidates by true relevance, condensing N sets down to the final `top-k`. |
| **Discard & dedupe** | Irrelevant tools that snuck through on surface similarity are dropped; duplicates across sub-queries are removed (a *must*). |
| **Self-reflect (optional Self-RAG)** | If the agent judges it still lacks a needed tool, it can autonomously re-query the Toolshed KB for more. |

The final, condensed `top-k` toolset is handed to the agent — which then does the actual tool *calling*. (The paper scopes itself to *retrieval*, not the calling/solving step.)

> [!TIP]
> An LLM reranker can be swapped for a cheaper embedding cross-encoder — but the LLM brings extra reasoning (discarding irrelevant tools, collapsing near-duplicates) that a pure embedder can't. Classic accuracy-vs-cost trade-off.

### 4. The `tool-M` × `top-k` equation — the cost dial

This is the paper's quietly practical contribution. Two separable questions:

| Question | Measured by | Finding (Seal-Tools) |
|---|---|---|
| Can a *Simple Agent* even call correctly when handed M tools? | Toolshed Eval Framework (name + param keys + param values) | **97–100%** accuracy for *any* M from 1–128 (on this non-overlapping dataset) |
| Does *retrieval* find the right tools as the catalog grows? | Recall@k | ARTF holds **95–100%** across tool-M/top-k; only dips to 80–100% once tool-M > 500 *and* top-k < 6 |

Because an ARTF agent only ever holds `top-k` tools, its overall performance ≈ **(retrieval accuracy) × (Simple-Agent accuracy where tool-M = top-k)**. So if a dataset is hard for the agent's reasoning, you set `top-k` *lower* — fewer tools to reason over (and fewer tokens) — and lean on high retrieval accuracy to make sure the right ones are still in that small set.

**🗣️ In plain English:** It's like deciding how many job candidates to bring in for a final interview. Bring too many (high `top-k`) and the hiring manager gets overwhelmed and the process is expensive. Bring too few and you might've filtered out the best person. Toolshed says: if your screening (retrieval) is excellent, you can confidently interview just a handful — saving everyone's time and money.

---

## The Evidence

### Retrieval accuracy vs. baselines (Recall@5, absolute improvement)

| Benchmark | Tools | Beats BM25 by | Beats prior SOTA by |
|---|---|---|---|
| **ToolE — single-tool** | ~200 | **+46%** | +5% over Re-Invoke |
| **ToolE — multi-tool** | ~200 | **+56%** | +9% over Re-Invoke |
| **Seal-Tools** (single + multi) | ~4,000 | **+47%** | +41% over Seal-Tools DPR |

> The headline: across all three datasets, ARTF beats the BM25 lexical baseline by ~46% absolute Recall@5, and beats every prior state-of-the-art retriever it was compared against — **without fine-tuning any model.**

### Scaling behavior (tool-M from 1 → 4,000)

| Setup | Result |
|---|---|
| Seal-Tools **DPR** baseline | As tool-M grows, retrieval accuracy **drops significantly**; high top-k needed to compensate |
| **Advanced RAG-Tool Fusion** | Retrieval stays **95–100%** for essentially any tool-M / top-k; degrades only past tool-M > 500 with top-k < 6 |
| **Simple Agent** tool-calling (Seal-Tools) | **97–100%** for any 1–128 tools — so on a clean, non-overlapping dataset the *bottleneck is retrieval, not calling* |

> [!NOTE]
> The key differentiator varied by dataset: on **Seal-Tools** it was the **query-decomposition/planner** module; on **ToolE** it was the **pre-retrieval enrichment + multi-query expansion + rewriting + reranking** combo. This is why ARTF is an *ensemble* — no single trick wins everywhere.

### What's great vs. what breaks

| ✅ Advantages | Why it matters |
|---|---|
| **No fine-tuning** | Plug-and-play with any off-the-shelf embedder/LLM; adapts instantly to new tools |
| **Scales to thousands of tools** | Breaks the 128-tool ceiling without multi-agent gymnastics |
| **Modular ensemble** | Turn individual RAG modules on/off per dataset |
| **Explicit cost dial** | `top-k` lets you trade accuracy for token cost / latency, with data to guide it |
| **Plain vector DB** | No hierarchical tool-category tree required; metadata filtering optional |

| ⚠️ Limitations | Impact |
|---|---|
| **Planner is tool-agnostic** | Decomposition has no knowledge of what tools exist — adding that context (or clarifying questions) could push accuracy toward 100% but breaks zero-shot |
| **Fixed `top-k` per sub-intent** | A flat budget (e.g. 24 = 3 sub-intents × 8) hurts when one sub-intent is harder; dynamic thresholds are future work |
| **Multi-turn chat unexplored** | On a follow-up ("what if the cost were $500 more?"), should you reuse the prior toolset, the single last tool, or re-run the whole pipeline? Open question |
| **Easy benchmark caveat** | Seal-Tools tools barely overlap and need only single-turn calls — real multi-turn, HITL, stateful tool datasets (τ-bench, ToolSandbox) will be harder |
| **Latency/cost of the pipeline** | Rewrite + decompose + multi-expand + rerank is several extra LLM calls per query |

---

## The Business Problem

A wealth-management research copilot has a catalog of **60+ analytics tools** (rebalancing, tax-loss harvesting, risk attribution, NPV, factor exposure, options Greeks, FX conversion, …). Stuffing all 60 into every prompt blows past the model's reliable tool limit and causes mis-selection. We need a **Toolshed retrieval layer** that, for each advisor query, enriches and indexes the catalog, decomposes and expands the query, retrieves and reranks down to a small `top-k`, and hands only those tools to the agent — while measuring **Recall@k** as we vary catalog size (`tool-M`) and selection threshold (`top-k`).

> [!WARNING]
> **Synthetic / public data only** (per `CLAUDE.md`). A toy 12-tool catalog and hand-written golden query→tool pairings — decision-support, not advice. No real client data or MNPI.

---

## From Paper to Practice

The companion notebook — [`builds/toolshed.ipynb`](builds/toolshed.ipynb) — is a scaffold that forces you to reconstruct **every** mechanism of the paper against the wealth-management problem above. Each section is a markdown explainer plus a skeleton code cell with a precise `# TODO`; you implement the TODOs, wire the phases into one LangGraph, then tick the validation checklist. The coverage map below is the contract — finishing it means you've touched the whole paper.

| # | Paper aspect | Role in the build | Notebook section |
|---|---|---|---|
| 1 | Toolshed Knowledge Base (vector store + metadata dict) | Store enriched tool docs; map display name → real callable | §1 |
| 2 | Pre-retrieval enrichment (name, description, arg schema, synthetic Qs, key topics) | Turn each catalog tool into a rich, embeddable document | §2 |
| 3 | Indexing / embedding | Embed enriched docs into the KB | §2 |
| 4 | Intra-retrieval: query rewrite | Fix pronouns/typos, use chat history | §3 |
| 5 | Intra-retrieval: query decomposition / planning | Split a multi-part advisor query into sub-steps | §4 |
| 6 | Intra-retrieval: multi-query expansion | Generate diverse phrasings per sub-step | §5 |
| 7 | Retrieval | Query the KB per variant → top-k candidates each | §6 |
| 8 | Post-retrieval: rerank + dedupe | Condense the candidate pile to a final top-k | §7 |
| 9 | Post-retrieval: self-reflection (Self-RAG) | Agent judges sufficiency; re-query if a tool is missing | §8 |
| 10 | `tool-M` × `top-k` trade-off + Recall@k | Measure recall vs catalog size and threshold | §9 |
| 11 | Final agent tool-calling | Equip only the top-k tools; let the agent answer | §10 |
| 12 | Wire-up into one graph | Assemble all phases into a runnable LangGraph | §11 |

The core state the graph threads through every phase:

```python
class ToolshedState(TypedDict):
    query: str
    rewritten: str
    sub_steps: List[str]      # query decomposition (intra-retrieval)
    variants: List[str]       # multi-query expansion
    candidates: List[str]     # retrieved per-variant tool names
    final_tools: List[str]    # after rerank + dedupe + self-reflection
    messages: Annotated[List[BaseMessage], add_messages]
```

---

## Connection to Context Engineering

Toolshed is fundamentally a **🎯 Select** paper — it's the discipline of *selecting* the right context (here, tools) before it ever reaches the model. But it touches all four strategies:

| Strategy | How Toolshed applies |
|---|---|
| 🎯 **Select** | The whole point. Out of thousands of tools, retrieve only the `top-k` relevant ones into the prompt — the purest possible Select mechanism. |
| ✍️ **Write** | Pre-retrieval *writes* enriched tool documents (synthetic questions, key topics, argument schemas) into the Toolshed KB — externalized, reusable context authored ahead of time. |
| 🗜️ **Compress** | Post-retrieval reranking + dedupe *compresses* an over-fetched candidate pile down to a tight, non-redundant `top-k`. Lowering `top-k` is literal context compression. |
| 🧱 **Isolate** | The agent's prompt is *isolated* from the full 4,000-tool catalog — it never sees tools it doesn't need, keeping the working context lean. |

> [!NOTE]
> Toolshed is a direct defense against **context confusion** and **context distraction** — the failure modes where too many (or irrelevant) tools in the prompt make the model pick wrong or lose focus. OpenAI's own ≤20-tool guidance *is* the confusion failure mode admitted in a footnote. By retrieving a small, high-precision `top-k`, Toolshed keeps the tool context clean enough for the agent to reason well.

---

## Connection to Other Papers in This Folder

### vs. Context Engineering (the four-strategy framework)

| Dimension | Context Engineering | Toolshed |
|---|---|---|
| **Scope** | General framework for curating *all* context | A concrete, deep instance of one strategy (🎯 Select) applied to *tools* |
| **Contribution** | Names the strategies & failure modes | Operationalizes Select for large tool catalogs with measured trade-offs |
| **Takeaway** | "Curate what enters the window" | "Here's exactly how to curate *tools* at scale" |

### vs. Reflexion

| Dimension | Reflexion | Toolshed |
|---|---|---|
| **What it reflects on** | *Why did my task attempt fail?* | *Did retrieval get me all the tools I need?* (optional Self-RAG step) |
| **Loop** | Across task retries | Within a single retrieval pass |
| **Shared DNA** | Self-reflection as a corrective signal | Post-retrieval self-reflection is the same idea, scoped to tool sufficiency |

### vs. Think Tool

| Dimension | Think Tool | Toolshed |
|---|---|---|
| **Concern** | *Should I act now, or pause and reason?* mid-task | *Which tools should I even have access to?* before acting |
| **When** | During tool-use chains | Before the agent is handed any tools |
| **Together** | Think Tool decides *whether/how* to use a tool; Toolshed decides *which tools are on the bench* | Complementary layers of the same tool-use stack |

---

## Connection to This Project's Modules

| Paper idea | Repo module | Link |
|---|---|---|
| Retrieve only the `top-k` relevant tools; isolate the agent from the full catalog | `context_isolation/` *(planned)* | The Select/Isolate strategy, made concrete for tools |
| Delegate scoped tool subsets so each agent's context stays lean | `subagent_delegation/` *(planned)* | Toolshed is the within-agent alternative to splitting tools across sub-agents |
| Enriched, externalized tool documents as reusable written context | `scratchpad/` *(planned)* | Same "write rich context once, reuse at inference" instinct |
| Vector-DB-backed retrieval of stored representations | `long_term_memory/` | Mechanically identical infra: embed → store → retrieve top-k |

> [!NOTE]
> The technique modules (`scratchpad/`, `context_isolation/`, `subagent_delegation/`) are scaffolded as you progress through the article; `long_term_memory/` already exists and shares Toolshed's embed-store-retrieve backbone.

---

**The takeaway:** Toolshed's big move is a reframe — **scaling an agent's tools is the same needle-in-a-haystack problem as RAG**, so steal RAG's entire advanced playbook. Store each tool as a richly enriched document (name, description, arg schema, synthetic questions, key topics) in a vector "Toolshed Knowledge Base," then run an ensemble pipeline — pre-retrieval enrichment, intra-retrieval query rewriting/decomposition/expansion, and post-retrieval reranking/dedupe/self-reflection — to surface only the handful of tools each request actually needs. The result is +46–56% absolute Recall@5 over BM25 and stable 95–100% retrieval across catalogs up to 4,000 tools, **with zero fine-tuning**. And by exposing the `tool-M` × `top-k` trade-off explicitly, it hands practitioners a concrete dial: tighten `top-k` to cut tokens and sharpen agent reasoning, and trust high-precision retrieval to keep the right tools in that small set. It's context engineering's 🎯 *Select* strategy, fully industrialized for tools.

---

## References

- [Toolshed: Scale Tool-Equipped Agents with Advanced RAG-Tool Fusion and Tool Knowledge Bases — Lumer, Subbiah, Burke, Honaganahalli Basavaraju, Huber, 2024 (arXiv:2410.14594)](https://arxiv.org/abs/2410.14594)
- Author code walkthrough: [EliasLumer/Toolshed-... (GitHub)](https://github.com/EliasLumer/Toolshed-Scale-Tool-Equipped-Agents-with-Advanced-RAG-Tool-Fusion-and-Tool-Knowledge-Bases)
- Follow-up work: [Graph RAG-Tool Fusion — Lumer et al., 2025 (arXiv:2502.07223)](https://arxiv.org/abs/2502.07223)

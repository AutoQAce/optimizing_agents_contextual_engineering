# Graph RAG-Tool Fusion: Teaching an Agent to Retrieve a Tool *and* Everything That Tool Needs

> **Paper:** Graph RAG-Tool Fusion · **Authors:** Elias Lumer, Pradeep Honaganahalli Basavaraju, Myles Mason, James A. Burke, Vamse Kumar Subbiah (PwC AI & EmTech Teams) · **Year:** 2025
> **Link:** [arXiv:2502.07223](https://arxiv.org/abs/2502.07223) · **Difficulty:** ★★★☆☆ · **Reading time:** ~14 min
> **Roadmap phase:** Phase 1 — Agent Foundations · **Module link:** context-isolation / tool-selection (Select strategy)

---

> [!NOTE]
> **At a Glance**
> - **The problem:** When an agent has access to *hundreds or thousands* of tools, you can't fit them all in the context window — you must *retrieve* the relevant few. Plain vector RAG finds tools that *sound like* the query but **misses each tool's hidden dependencies** (the "get stock price" tool silently needs "get stock ticker", which needs internet connectivity).
> - **The idea:** Store tools in a **knowledge graph** where edges encode dependencies. Retrieve the top-k tools by vector search, then **traverse the graph** to pull in every dependency. Vector search for *relevance*, graph traversal for *completeness*.
> - **The payoff:** **+71.7%** (ToolLinkOS) and **+22.1%** (ToolSandbox) absolute improvement in retrieval accuracy (mAP@10) over naïve RAG — no model fine-tuning, fully plug-and-play.
> - **The bonus:** A new benchmark, **ToolLinkOS** (573 fictional tools across 15+ industries, avg 6.3 dependencies each) — the first tool-retrieval dataset with a predefined dependency knowledge graph.

---

## The Core Idea

| Naïve RAG Tool Retrieval | Graph RAG-Tool Fusion |
|---|---|
| Tools stored as vectors in a vector DB | Tools stored as **nodes in a knowledge graph** (plus vectors) |
| Retrieve top-k tools by **semantic similarity** to the query | Retrieve top-k by similarity, **then traverse edges** to gather dependencies |
| A tool's dependencies are invisible — they're often *semantically unrelated* to the query | Dependencies are **explicit edges** — retrieved structurally, not semantically |
| "Get stock price" retrieved alone → agent fails (no ticker) | "Get stock price" → "get stock ticker" → "internet connectivity" all retrieved together |
| Accuracy collapses as tool count + dependency depth grows | Accuracy holds because structure is traversed, not guessed |

Graph RAG-Tool Fusion is a **plug-and-play** retrieval method (no fine-tuning) that fixes a blind spot in tool retrieval: a tool is rarely useful by itself. It usually needs *other* tools to supply its parameters or to operate at all. Vector search is great at finding the *main* tool you asked for, but terrible at finding that tool's prerequisites — because a prerequisite like `set_wifi_on` has nothing semantically in common with "make me a dinner reservation." The fix is to **combine two retrieval mechanisms**: vector search for semantic relevance, and graph traversal for structural completeness.

> 🖼️ *Suggested figure: the two-stage pipeline — vector search retrieves nodes A/B/C, then DFS traversal walks each node's dependency edges to gather the full tool set, concatenated into one ordered list and truncated to top-K.*

---

## Key Terms

| Term | Plain-English meaning |
|---|---|
| **Tool retrieval / tool selection** | Picking the small subset of relevant tools (out of thousands) to actually hand to the agent at inference time |
| **Tool knowledge base** | The full corpus of M tools the agent *could* use |
| **Knowledge graph (KG)** | Tools stored as **nodes**, dependencies between them stored as **edges** |
| **Core tool** | A reusable utility other tools depend on (e.g. `get_current_date`, `set_wifi_status`). 50 of ToolLinkOS's 573 tools |
| **Regular tool** | A normal, non-utility tool/API/agent the user actually wants (e.g. `restaurant_reservation`). 523 of 573 |
| **Dependency (edge)** | A directed link saying "tool X needs / benefits from tool Y" |
| **Vector search** | First-pass retrieval by embedding similarity between the query and each tool's description |
| **Graph traversal (DFS)** | Walking the dependency edges out from each retrieved tool to collect its prerequisites |
| **Reranking (RR)** | An LLM re-orders the initial vector hits so the *most* relevant tool is ranked #1 before traversal |
| **k / d / K** | `k` = how many tools vector search returns; `d` = dependency limit per tool; `K` = final cut-off (total tools handed to the agent) |
| **mAP@10** | Mean Average Precision at 10 — the headline retrieval-quality metric (higher = better) |

---

## Why Does This Matter?

Modern agents are expected to call from **hundreds to thousands** of tools, APIs, and even other agents-as-tools. You physically cannot stuff every tool definition into the context window — so you retrieve a relevant subset per query. That retrieval step is now a core bottleneck, and plain RAG breaks on it:

| Problem | What Happens |
|---|---|
| **Dependencies are semantically unrelated** | "Restaurant reservation" needs the *current date* and *Wi-Fi on*, but those tools don't *sound* like the query, so vector search never retrieves them |
| **The agent gets a half-equipped toolbox** | It retrieves the main tool, calls it, and fails because a required parameter-supplying tool was never loaded |
| **Existing benchmarks ignore this** | ToolBench, ToolE, Seal-Tools have lots of tools but **no dependency structure** — so the field couldn't even *measure* the problem |
| **It gets worse with scale** | More tools + deeper dependency chains = vector search misses more prerequisites |

> [!IMPORTANT]
> The key insight: **a tool's relevance and a tool's prerequisites are two different things, and they require two different retrieval mechanisms.** Semantic similarity (vectors) finds what you asked for. Structural traversal (graph) finds what that thing *needs*. Naïve RAG only has the first; it's structurally blind.

**🗣️ In plain English:**

Imagine you ask a hardware-store clerk for "a shelf bracket." A bad clerk hands you just the bracket. You get home and discover you also needed wall anchors, the right screws, and a drill bit — none of which you knew to ask for, and none of which *look* like "shelf bracket." A great clerk knows the **dependency chain**: bracket → screws → anchors → drill bit, and hands you the whole kit. Naïve RAG is the bad clerk (matches words). Graph RAG-Tool Fusion is the great clerk (knows what depends on what).

---

## How Does It Work?

There are two phases: a one-time **indexing** phase that builds the tool knowledge graph, and a per-query **retrieval** phase that does vector search + graph traversal.

### 1. Graph Indexing — Modeling Tools as a Graph

Every one of the M tools is transformed into a schema object with a **node type** and a list of **dependency edges**.

#### Two node types

| Node Type | What It Is | Examples |
|---|---|---|
| **Core tool** | A reusable utility that *other* tools depend on; usually called before regular tools | `get_current_date`, `set_wifi_status`, `set_cellular_status`, `unit_converter` |
| **Regular tool** | A normal task tool/API/agent the user actually wants | `restaurant_reservation`, `get_current_stock_price` |

Core tools can themselves depend on other core or regular tools — dependencies nest arbitrarily deep.

#### Four edge (dependency) types

| Edge Type | Meaning | Example |
|---|---|---|
| **Tool directly depends on** | Tool *requires* another to operate at all | `get_stock_price` requires internet connectivity to be on |
| **Tool indirectly depends on** | Tool *benefits from* another but works without it | `restaurant_reservation` benefits from `get_weather` |
| **Parameter directly depends on** | A parameter *must* be supplied by another tool first | `product_info` needs `product_id`, supplied by `get_product_id` |
| **Parameter indirectly depends on** | A parameter depends on context *only if the user input requires it* | "tomorrow" needs `get_current_date`; but "12/25/2025" does not |

Each edge also carries `reason` (why the dependency exists) and `parameter_name` (which parameter, if any) labels.

**🗣️ In plain English:**

Think of recipes in a cookbook. A "regular tool" is a finished dish (lasagna). A "core tool" is a building block lots of dishes reuse (tomato sauce, fresh pasta). The edges are the "you'll need…" notes: *directly depends on* = "you cannot make lasagna without pasta"; *indirectly depends on* = "garlic bread goes nicely but isn't required"; *parameter directly depends on* = "the sauce recipe needs the quantity from the serving-size calculator." The graph just writes all those "you'll need…" notes down once, so nobody has to rediscover them per order.

---

### 2. Tool Retrieval — Vector Search, Then Traverse

At query time, the algorithm runs this pipeline (Algorithm 1 in the paper):

```
Input: user query q, vector DB, knowledge graph KG
       params: top_k, rerank_top_k, final_top_K, d_limit

1.  (optional) q ← QueryTransform(q)        # rewrite / decompose / transform
2.  initial ← VectorSearch(q, VDB, top_k)   # first-pass: top-k by similarity
3.  (optional) initial ← Rerank(initial, rerank_top_k)   # LLM puts best tool #1
4.  graph_list ← []
5.  for each tool t in initial:
6.      add t to graph_list (if new)
7.      for each dependency dep in DFS(t, KG) up to d_limit:
8.          add dep to graph_list (if new)   # walk the edges
9.  final ← truncate graph_list to final_top_K
10. return final                            # equip these tools to the agent
```

The ordering matters: the list starts with the **top vector tool, then its dependencies**, then the next vector tool and *its* dependencies, and so on — then it's **truncated to the final top-K**. So the most-relevant tool's full dependency chain is preserved first.

> [!NOTE]
> Graph RAG-Tool Fusion is **plug-and-play**: it sits *on top of* whatever vector retriever you already have. You can bolt on any advanced-RAG trick — query rewriting, decomposition, reranking, corrective RAG — at the vector-search step. The graph traversal is an *addition*, not a replacement.

> [!TIP]
> Because dependencies are read by **graph traversal**, not embedding similarity, they're retrieved with near-perfect recall *regardless of how semantically unrelated they are to the query.* That's the whole trick: stop asking vectors to find prerequisites they were never going to find.

**🗣️ In plain English:**

It's a two-pass librarian. First pass (vector search): "Here are the 3 books most related to your question." Second pass (graph traversal): "And here are the prerequisite texts each of those 3 books cites that you'll need to actually understand them." You walk out with a complete, ordered reading list instead of 3 books that each reference things you don't have.

---

### 3. The Retrieval Accuracy Equation

The paper models expected retrieval accuracy as the baseline vector accuracy **plus** the extra accuracy from graph-traversed dependencies, scaled by how many of the discovered tools actually fit under the final top-K cut-off:

```
E[GRTF(k, d, K)] = E[Retrieval_vector(k)]  +  E[KG_dep(k, d)] × min(1, K/N)
```

where `k` = initial vector tools, `d` = dependency limit per tool, `K` = final top-K cut-off, `N` = total tools discovered including all dependencies.

> [!WARNING]
> Notice the `min(1, K/N)` term. If a query's tools have **so many dependencies that N > K**, truncation kicks in and you start *losing* correctly-discovered tools at the final cut-off. This is exactly where the paper's biggest error source lives (see Evidence → Error Analysis). Set `K` generously when dependency chains are deep.

---

## The Evidence

Setup: embeddings = `text-embedding-ada-002`; LLM (for reranking/generation) = `gpt-4o-2024-08-06`; vector + lexical search via Azure AI Search (HNSW + BM25); knowledge graph in **Neo4j**. Metric = **mAP@10/20/30** over 1,569 (ToolLinkOS) and 1,032 (ToolSandbox) instances.

### Headline results (mAP@10)

| Dataset | Lexical (BM25) | Naïve RAG | Hybrid RAG | **GRTF (no rerank)** | **GRTF (w/ rerank)** |
|---|---|---|---|---|---|
| **ToolLinkOS** (573 tools, 6.3 deps avg) | 0.185 | 0.210 | 0.202 | **0.856** | **0.927** |
| **ToolSandbox** (33 tools, 1.6 deps avg) | 0.215 | 0.440 | 0.431 | **0.521** | **0.661** |

- On **ToolLinkOS**, GRTF goes from naïve RAG's 0.210 to **0.927** with reranking — a **+71.7% absolute** improvement.
- On **ToolSandbox**, naïve RAG's 0.440 → **0.661** — a **+22.1% absolute** improvement.

> [!IMPORTANT]
> The gap is *much* larger on ToolLinkOS (6.3 deps/tool) than ToolSandbox (1.6 deps/tool). **The more dependency-rich your toolset, the more Graph RAG-Tool Fusion wins.** When tools barely depend on each other, naïve RAG is nearly fine; when they form deep chains, naïve RAG falls off a cliff and graph traversal is essential.

**🗣️ In plain English:**

The benefit scales with how "tangled" your tools are. If your tools are mostly standalone (like a small ToolSandbox), the smart librarian only helps a bit. If your tools form a dense web of "this needs that needs the other" (like the 573-tool ToolLinkOS), the smart librarian is the difference between a working agent and a broken one.

---

### Reranking matters

Applying an LLM reranker to the initial top-k *before* traversal:

| Dataset | Lift from reranking (mAP@10) |
|---|---|
| ToolLinkOS | **+7% absolute** |
| ToolSandbox | **+14% absolute** |

Reranking also **reduced truncation errors by 52%** on ToolLinkOS — because putting the right tool at rank #1 means its dependency chain is expanded first and survives the top-K cut.

---

### Error Analysis — what actually goes wrong

The paper decomposes every retrieval failure into three buckets:

| Error | Cause | Frequency |
|---|---|---|
| **1. Not retrieved by vector search** | The correct *primary* tool wasn't even in the initial top-k (k=3) | 8.1% (hits reranked & non-reranked equally) |
| **2. In top-k but not top-1, then truncated** | Right tool was retrieved but ranked low; its deps got pushed out at the top-K cut | 91.6% of GRTF-no-RR errors; 43.6% of GRTF-RR errors |
| **3. Top-1 but excluded by dependency truncation** | Even the #1 tool's full dependency set overflowed top-K | <0.01% (no RR); 30% (RR) |

> [!CAUTION]
> Error #2 dominates without reranking (91.6%). The lesson: **most failures aren't "we couldn't find the tool" — they're "we found it but ranked it wrong and truncation killed its dependencies."** That's why reranking (which fixes ranking) helps so much, and why it shifts the error profile toward truncation (#3 rises to 30%). The bottleneck is the *quality of the first-pass vector retrieval*, not the graph.

---

### Advantages

| Advantage | Why It Matters |
|---|---|
| **Plug-and-play, no fine-tuning** | Wrap it around any existing vector retriever |
| **Retrieves unrelated dependencies reliably** | Graph traversal doesn't care about semantic similarity |
| **Scales with tool count and dependency depth** | The harder the case, the bigger the win |
| **Composable with advanced RAG** | Query rewriting, reranking, corrective RAG all stack on the vector step |
| **Interpretable** | The dependency graph is human-readable and auditable |

### Limitations

| Limitation | Impact |
|---|---|
| **Bottlenecked by the vector retriever** | If first-pass vector search misses the primary tool, the graph can't save it (error #1) |
| **Requires a tool knowledge graph** | Someone must build the schema/edges — in this paper, **manually** |
| **No edge-type prioritization** | Retrieval treats "directly depends" and "indirectly depends" the same; deep graphs may need to prioritize direct edges |
| **Truncation loss on deep chains** | If N (discovered tools) ≫ K (cut-off), correct dependencies get dropped |
| **Benchmarks are non-runnable/fictional** | ToolLinkOS tools don't actually execute — it's a *retrieval* benchmark, not an end-to-end one |

---

## The Business Problem

A **wealth-management copilot** on a trading platform exposes a catalog of analytics & execution tools (risk attribution, rebalancing, tax-loss harvesting, price lookup, account context). Many silently **depend on others**: `compute_portfolio_risk` needs `get_current_positions`, which needs `resolve_account_id`; `place_rebalance_order` needs `get_live_price`, which needs `resolve_ticker`. Naïve vector retrieval fetches the headline tool an advisor asks for but **drops its prerequisite tools**, so the agent stalls mid-task. Build Graph RAG-Tool Fusion over a synthetic tool knowledge graph so each advisor query retrieves the right tool *and* its full dependency chain.

> ⚠️ **Synthetic data only. Decision-support, not live trading.** No real client data or MNPI.

---

## From Paper to Practice

A minimal LangGraph / LangChain build that exercises **every** core mechanism of the paper, on the wealth-management problem above. The notebook is a scaffold: a complete synthetic 12-tool catalog (3 core, 9 regular, all four edge types) is provided, and each section is a `# TODO` you implement — completing them all reproduces Algorithm 1 end-to-end. Runnable build: [`builds/graph_rag_tool_fusion.ipynb`](builds/graph_rag_tool_fusion.ipynb).

### Coverage map — the comprehension contract

| # | Paper aspect | Role in the build | Notebook section |
|---|---|---|---|
| 1 | Tool schema: core vs regular **nodes** | Validate & type the catalog | S1 |
| 2 | Four **dependency edge types** | Encode / validate edges | S1 |
| 3 | **Graph indexing** | Build the KG adjacency map | S2 |
| 4 | **Embeddings + vector index** | Embed tool descriptions | S3 |
| 5 | **Vector search (top-k)** | First-pass semantic retrieval (= naïve-RAG baseline) | S4 |
| 6 | (Optional) **Query transform** | Rewrite query before embedding | S5 |
| 7 | (Optional) **Reranking** | LLM puts the best tool at #1 | S6 |
| 8 | **Graph traversal (DFS, `d_limit`)** | Pull each tool's dependencies | S7 |
| 9 | **Ordered concat + dedup + top-K** (`k`/`d`/`K`, `min(1,K/N)`) | Assemble the final tool list | S8 |
| 10 | **Equip to agent + execute** | Run a multi-step query with retrieved tools | S9 |
| 11 | **Evaluation (mAP@K)** vs naïve RAG | Quantify the lift | S10 |
| 12 | **LangGraph wire-up** | Assemble the pipeline as a `StateGraph` | S11 |

The notebook ends with a **validation checklist** (one box per mechanism) — ticking all of it is the comprehension check.

---

## Connection to Context Engineering

Graph RAG-Tool Fusion is almost entirely a refinement of the **🎯 Select** strategy — but it touches all four:

| Strategy | How Graph RAG-Tool Fusion Applies |
|---|---|
| 🎯 **Select** | This is the heart of it. Instead of selecting tools by similarity alone, it selects by **similarity + structural dependency** — a strictly better selection function for tool-rich agents |
| 🗜️ **Compress** | By retrieving only the top-K relevant tools (and their deps) instead of all M tool definitions, it keeps the context window small — dependency-aware compression of the toolset |
| 🧱 **Isolate** | Each query gets its own scoped tool subgraph; the other ~570 tools never enter the context, isolating the agent from irrelevant tool definitions |
| ✍️ **Write** | The knowledge graph itself is *written* context — pre-authored structured knowledge (the dependency edges) that the system reads at retrieval time rather than re-deriving |

> [!NOTE]
> This directly combats **Context Confusion** and **Context Distraction**. Dumping all 573 tool definitions into the prompt would distract the model (too many irrelevant options) and confuse tool selection. By retrieving a tight, *complete* subgraph, the agent sees only the tools it needs — and crucially, *all* of the tools it needs, so it never stalls mid-task on a missing dependency.

---

## Connection to the Toolshed Paper

This paper is the direct successor to the same authors' **Toolshed: Scale Tool-Equipped Agents with Advanced RAG-Tool Fusion** (also in `papers_pdf/`). The lineage:

| Dimension | Toolshed (RAG-Tool Fusion) | Graph RAG-Tool Fusion |
|---|---|---|
| **Core mechanism** | Advanced RAG over a flat tool vector store | Advanced RAG **+ knowledge-graph traversal** |
| **Handles tool dependencies?** | Not structurally | **Yes — explicit graph edges** |
| **Data structure** | Vector DB | Vector DB **+ Neo4j knowledge graph** |
| **New contribution** | Tool knowledge bases + RAG-Tool Fusion | The graph layer + the **ToolLinkOS** dependency benchmark |

If you read both, read Toolshed first: it establishes "retrieve tools with RAG," and this paper adds "…and traverse their dependencies."

## Connection to Reflexion & Generative Agents

| Dimension | Reflexion / Generative Agents | Graph RAG-Tool Fusion |
|---|---|---|
| **What's retrieved** | Past *memories* / reflections | *Tools* and their dependencies |
| **Retrieval signal** | Recency × importance × relevance (semantic) | Semantic similarity **+ graph structure** |
| **Shared idea** | You can't fit everything in context — you must *select* what enters | Same — but for the toolset, with structure added |

All three are answers to the same underlying constraint — **the context window is finite, so retrieval quality is everything** — applied to different payloads (memories vs. tools).

---

## Connection to This Project's Modules

| Paper idea | Maps to this project's work |
|---|---|
| Retrieve only the relevant tool subset, isolate the rest | The article's **context isolation** theme — keeping each task's context scoped and lean |
| Pre-authored dependency graph read at retrieval time | The **long-term memory** module (`long_term_memory/`) — externalized, structured knowledge an agent reads back later |
| Hand a scoped, complete toolset to a sub-agent | The article's **sub-agent delegation** theme — give a scoped helper exactly the tools it needs, nothing more |
| Cost/latency/quality trade-off of how much you feed the agent | The article's central thesis — Graph RAG-Tool Fusion is a concrete lever on that trade-off |

---

**The takeaway:** Graph RAG-Tool Fusion fixes a specific, expensive blind spot in scalable tool-using agents: vector search retrieves the tool you *asked for* but silently drops the tools that tool *depends on*, because dependencies are usually semantically unrelated to the query. The fix is to model tools as a **knowledge graph** (nodes = tools, edges = four kinds of dependency), retrieve the top-k by vector similarity, then **traverse the graph with DFS** to gather every prerequisite, concatenate into one ordered list, and truncate to the final top-K. It's plug-and-play (no fine-tuning), it stacks on top of any advanced-RAG retriever, and it delivers **+71.7%** and **+22.1%** absolute mAP@10 gains over naïve RAG — with the advantage growing the more dependency-rich your toolset is. The remaining bottleneck isn't the graph; it's the *first-pass vector retrieval* (most errors are "found the tool but ranked it wrong and truncated its deps"), which is why an LLM reranker adds another +7–14%. The lesson for agent builders: **relevance and prerequisites are different problems — use vectors for one and graph structure for the other.**

---

## References

- [Graph RAG-Tool Fusion — Lumer, Honaganahalli Basavaraju, Mason, Burke, Subbiah, 2025 (arXiv:2502.07223)](https://arxiv.org/abs/2502.07223)
- [ToolLinkOS dataset (MIT License) — GitHub](https://github.com/EliasLumer/Graph-RAG-Tool-Fusion-ToolLinkOS)
- [Toolshed: Scale Tool-Equipped Agents with Advanced RAG-Tool Fusion — Lumer et al., 2024 (arXiv:2410.14594)](https://arxiv.org/abs/2410.14594)

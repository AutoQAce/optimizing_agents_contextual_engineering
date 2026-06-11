# Retrieval Models Aren't Tool-Savvy: Why Your Agent Can't Find the Right Tool — and a Benchmark That Proves It

> **Paper:** Retrieval Models Aren't Tool-Savvy: Benchmarking Tool Retrieval for Large Language Models · **Authors:** Zhengliang Shi et al. (Shandong University · Baidu · Leiden) · **Year:** 2025
> **Link:** [arXiv:2503.01763](https://arxiv.org/abs/2503.01763) · **Difficulty:** ★★★☆☆ · **Reading time:** ~14 min
> **Roadmap phase:** Phase 1 — Agent Foundations · **Module link:** `context_isolation/` *(planned)* — the 🎯 Select strategy for tools, and the evaluation half of [[toolshed]] / [[graph_rag_tool_fusion]]

---

## At a Glance

> [!NOTE]
> - **The problem:** Almost every tool-use benchmark cheats. It hands the agent a pre-curated shortlist of ~10–20 "obviously relevant" tools per task. Real systems have *thousands* (RapidAPI ≈ 52k; PyPI ≈ 600k packages), so something has to *retrieve* the right few first — and nobody had measured how well retrievers actually do that.
> - **The benchmark:** **TOOLRET** — 7.6k retrieval tasks over a corpus of **43k tools**, aggregated from 30+ existing datasets and reformatted into a clean IR benchmark (like MTEB/BEIR), split into **Web API / Code Function / Customized App**.
> - **The shocking result:** retrievers that *dominate* normal IR benchmarks fall apart here. The best model (NV-Embed-v1, 7B) scores only **33.83 nDCG@10**. Every retriever lands **under 52% Recall@10** and **under 35% Completeness@10**. ColBERT even loses to plain BM25.
> - **The downstream cost:** swap an agent's oracle toolset for retrieved tools and the end-to-end **task pass rate drops ~10–11 points**. Bad retrieval = bad agent.
> - **The fix:** **TOOLRET-train**, a 200k-instance instruction-tuned training set. Models trained on it improve retrieval *and* lift tool-use LLM pass rates by **10–20%**.

---

## The Core Idea

| Concept | What It Means |
|---|---|
| **Tool retrieval** | The *first* step of tool use: out of a giant toolset, pick the handful of tools to even show the agent. Get this wrong and nothing downstream can recover. |
| **The convenient lie** | Most tool-use benchmarks skip retrieval — they pre-annotate ~10 relevant tools per task. Great for measuring *calling*; useless for measuring *finding*. |
| **TOOLRET** | The first large-scale, heterogeneous benchmark built *specifically* to measure tool retrieval — 7.6k tasks, 43k tools, MTEB-style format, with an optional per-query **instruction**. |
| **The finding** | Tool retrieval is genuinely *harder* than document retrieval. State-of-the-art IR models, untouched, are bad at it — and that badness propagates into agent failure. |
| **TOOLRET-train** | A 200k-instance instructional training set that teaches retrievers to be "tool-savvy," closing much of the gap. |

In one paragraph: the field had been quietly grading tool-use agents on an easy version of the test — handing them the answer key (a tiny pre-filtered toolset) before the exam. TOOLRET removes the answer key, makes models retrieve from 43k real tools, and shows that even the best retrievers stumble badly. Then it provides the training data to fix them.

> 🖼️ *Suggested figure:* the headline correlation plot (paper Fig. 1) — x-axis Recall@10 of various IR models, y-axis end-to-end pass rate of GPT-3.5; a dashed line marks the **oracle** pass rate (64.2) and the gap down to retrieval-fed agents (only ~27.3 Recall@10, pass rate −10.1).

---

## Key Terms

| Term | Plain-English meaning |
|---|---|
| **Tool learning** | Equipping an LLM with external tools (web APIs, Python functions, apps) so it can *do* things, not just talk. |
| **IR model (retriever)** | An information-retrieval model that, given a query, ranks a big corpus and returns the top matches. Here the "documents" are tool descriptions. |
| **Toolset / corpus** | The full collection of tools the agent *could* use (43k in TOOLRET). |
| **Oracle toolset** | The hand-annotated "correct" small set of tools for a task — the cheat the paper is calling out. |
| **Instruction (instructional IR)** | An extra sentence paired with the query that spells out the *relevance criteria* ("retrieve tools that transcribe audio to text…"), guiding the retriever beyond the bare query. |
| **Dense / sparse retrieval** | Sparse = lexical word-overlap matching (BM25). Dense = neural embeddings compared by cosine similarity. |
| **Cross-encoder re-ranker** | A heavier model that re-scores an initial shortlist by reading query + candidate *together* (more accurate, slower). |
| **nDCG@K / Recall@K / Precision@K** | Standard ranking metrics — ranking quality / fraction of targets found / accuracy of the top-K, respectively. |
| **Completeness@K (C@K)** | TOOLRET's key metric: **1 only if *all* target tools** for a task appear in the top-K, else 0. Brutal, because tasks need *several* tools. |
| **Term / lexical overlap (ROUGE-L)** | How many words the query and the correct tool's docs literally share. Low overlap ⇒ the retriever must *understand*, not pattern-match. |
| **Pass rate** | End-to-end metric: did the agent actually call the right tools and solve the task? |

---

## Why Does This Matter?

Tool retrieval is the silent bottleneck of agentic AI. Two structural realities make it unavoidable — and most research had been ignoring both:

| Problem | Why it bites |
|---|---|
| **Toolsets are massive** | RapidAPI hosts 52k+ tools; PyPI 600k+ packages. You cannot stuff them all into a limited context window. |
| **Tools update constantly** | Re-training an LLM to "memorize" tools is expensive and goes stale immediately. Retrieval is the cheap, plug-and-play alternative. |
| **Benchmarks pre-annotate the answer** | ToolACE and ToolBench give ~10 relevant tools per task. That measures tool *calling*, not tool *finding* — and hides the retrieval problem entirely. |
| **Existing retrievers are trained for the wrong job** | They're optimized on document/passage retrieval (MS-MARCO, NQ), not on matching a vague user request to the right API among thousands. |

> [!IMPORTANT]
> The key insight: **tool retrieval is not just "document retrieval with tools as documents."** It is measurably harder along two axes — (1) the query and the correct tool barely share words (ROUGE-L overlap of **0.06** vs. 0.31 for Natural Questions), forcing deep semantic understanding; and (2) most tasks need **multiple tools at once** (avg 2.17 targets), so partial retrieval = failure. Models tuned for ordinary IR are not tuned for *this*.

**🗣️ In plain English:**

Imagine a hardware store with 43,000 items and a customer who walks in and says *"I want to hang a picture."* The easy benchmark is like a store where a clerk has already laid 10 likely items on the counter and you just pick the hammer. The *real* job is finding — among 43,000 SKUs — the hammer **and** the nails **and** the wall anchors **and** the level, when the customer never said any of those words. A clerk who's brilliant at "find me the item literally named X" is suddenly useless, because the customer's words ("hang a picture") share almost no vocabulary with the products they actually need. That mismatch is exactly what TOOLRET exposes.

---

## How Does It Work?

TOOLRET is built in three stages — collect, sample, instruct — then evaluated under a careful protocol. Below, one sub-section per moving part.

### 1. Building the Benchmark (Collect → Sample → Instruct)

```
COLLECT  ── 30+ datasets (Aug 2023–Dec 2024) from ACL/NeurIPS tool-use benchmarks,
            CIKM/EMNLP resource tracks, and HuggingFace community releases
            → dedup + normalize → reformat to MTEB/BEIR style (query → target tools)

SAMPLE   ── Task sampling: embed every task (NV-Embed-v1), K-means cluster,
            take 1 task per cluster (clusters = min(#queries, #tools)) → 7.6k tasks
         ── Toolset sampling: manually merge duplicate/overlapping toolsets across
            34 datasets, assign unique IDs → 43k-tool corpus

INSTRUCT ── 3 NLP/IR experts handcraft 100 seed instructions (relevance criteria)
            → GPT-4o generates an instruction per task via in-context learning
            → 5 experts quality-review (Kappa 0.743); revise the ~10.8% that mismatch
```

Every task ends up as: **a query + a generated instruction + the target tool(s) (labels)**, drawn from a shared 43k corpus. The corpus splits naturally into three documentation formats:

| Subset | # Tasks | # Tools | What the tool doc looks like |
|---|---|---|---|
| **Web API** | 4,916 | 36,978 | Structured JSON, OpenAPI-style |
| **Code Function** | 950 | 3,794 | A function-level code snippet |
| **Customized App** | 1,749 | 2,443 | Free-form natural-language description |
| **Total** | **7,615** | **43,215** | avg query 46.9 tok · avg tool doc 174.6 tok |

> [!NOTE]
> The format-based split (Web/Code/App) isn't cosmetic — it lets you see *where* a retriever breaks. A model great at matching natural-language app descriptions may choke on terse JSON API schemas.

**🗣️ In plain English:**

They didn't invent tasks from scratch — they went around to 30+ existing "can your agent use tools?" datasets, threw away the part where the answer was pre-filled, kept the messy real questions, merged all the tools into one giant 43k shared library, and relabeled everything in a single clean format so any retriever can be plugged in and graded fairly. Then they used GPT-4o to write a one-line "here's what a good answer looks like" hint for each task — and had humans check those hints.

### 2. Why It's Harder Than Normal Retrieval (the two killers)

| Difficulty axis | TOOLRET | Normal IR benchmarks |
|---|---|---|
| **Avg # targets per query** | **2.17** | NQ 1.00 · MS-MARCO 1.00 · HotpotQA 2.00 · MTEB 2.57 |
| **ROUGE-L overlap (query ↔ target)** | **0.06** | NQ 0.31 · MS-MARCO 0.34 · HotpotQA 0.11 · MTEB 0.27 |

Two forces compound: you must retrieve **several** correct tools (and Completeness@K demands *all* of them), and you must do it with **almost no shared vocabulary** to lean on. That's why lexical tricks fail and even strong semantic models struggle.

> [!WARNING]
> The 0.06 ROUGE-L number is the whole story in one statistic. A user says "plan my trip to Tokyo"; the correct tool is documented as `flight_search(origin, dest, date)`. Zero word overlap. A retriever that quietly relies on term matching — even a neural one — has nothing to grab onto.

### 3. The Evaluation Protocol

- **Metrics:** nDCG@K (ranking quality), Recall@K (fraction of targets found), Precision@K, and **Completeness@K** (all-or-nothing: did we get *every* target tool?).
- **Two input settings:** **w/o inst.** (query only) vs. **w/ inst.** (query + generated instruction concatenated) — isolating how much the instruction helps.
- **Six model families evaluated:**

| Family | Examples | Idea |
|---|---|---|
| **Sparse** | BM25s | Lexical overlap |
| **Single-task dense** | GTR, Contriever, ColBERTv2, COLT | Dual-encoder trained on MS-MARCO (COLT on ad-hoc tool data) |
| **Multi-task embedding** | all-MiniLM, GTE, BGE, E5 | Encoders trained across many IR datasets |
| **Instruction-tuned embedding** ♠ | NV-Embed-v1, e5-mistral-7b, GritLM-7B, gte-Qwen2 | Embeddings that natively follow instructions |
| **Cross-encoder re-rankers** | MonoT5, mxbai, jina-reranker-v2, bge-reranker | Re-score an initial shortlist |
| **LLM agents (RankGPT)** | GPT-3.5, Mixtral-8x22B | Zero-shot LLM re-ranking |

---

## The Evidence

### Existing retrievers struggle — badly

Across the board (w/o instruction), **every** retriever scores under **52% Recall@10** and under **35% Completeness@10**. Selected average scores:

| Model | Type | Avg nDCG@10 | Avg C@10 |
|---|---|---|---|
| **NV-Embed-v1** (7B) ♠ | Instruction-tuned embed | **33.83** | 32.12 |
| GritLM-7B ♠ | Instruction-tuned embed | 30.02 | 29.44 |
| gte-Qwen2-1.5B ♠ | Instruction-tuned embed | 28.96 | 26.04 |
| **bge-reranker-v2-gemma** | Cross-encoder re-ranker | **35.51** | 34.14 |
| jina-reranker-v2-base | Cross-encoder re-ranker | 33.60 | 32.11 |
| BM25s | Sparse (lexical) | 22.32 | 22.19 |
| ColBERT | Single-task dense | **19.46** | 18.69 |
| COLT (ad-hoc tool-trained) | Single-task dense | 19.25 | 20.32 |

> [!CAUTION]
> Two humbling facts: **ColBERT (19.46) loses to plain BM25 (22.32)** — a strong neural retriever beaten by 2009-era lexical matching. And **COLT**, a model *specifically trained on tool data*, lands near the bottom (19.25). Being good at normal IR, or being trained ad-hoc on tools, does not transfer to robust tool retrieval.

The authors trace the gap to two causes: **(1) low lexical overlap** (needs real semantic reasoning) and **(2) domain/task shift** — models trained on document retrieval aren't optimized for matching intent to tools.

### Re-ranking barely helps — sometimes it hurts

| Action | nDCG@10 |
|---|---|
| NV-Embed-v1 alone | 33.83 |
| NV-Embed-v1 → **re-ranked by MonoT5** | **28.92** ⬇ |

Re-ranking the candidates *lowered* the score. bge-reranker-v2-gemma managed only a ~4.7% Completeness gain. The classic "retrieve then re-rank" upgrade doesn't reliably pay off here.

### Instructions give a real, reliable boost

Adding the per-query instruction (w/ inst.) lifts **every** model — and most of all the instruction-tuned embedders:

| Model | w/o inst. (nDCG@10) | w/ inst. (nDCG@10) |
|---|---|---|
| NV-Embed-v1 ♠ | 33.83 | **42.71** |
| e5-mistral-7b ♠ | 26.06 | **38.97** |
| gte-Qwen2-1.5B ♠ | 28.96 | **45.96** |

> [!TIP]
> The instruction is doing **context engineering at the query level**: it injects the missing relevance criteria the bare query never stated, partly bridging that 0.06 lexical gap. Models *built* to follow instructions cash in the most.

### It correlates with normal IR — but is strictly harder

Performance on TOOLRET vs. MTEB: **Pearson 0.790** (same general ordering of models) but **Spearman only 0.441**, and every score is *lower*. Translation: good IR models tend to be better here too, but the ranking reshuffles and the absolute difficulty is much higher — TOOLRET is not redundant with MTEB.

### Bad retrieval wrecks the actual agent

The payoff experiment: on **ToolBench (G1/G2/G3)**, replace the oracle toolset with retrieved tools and measure GPT-3.5 / ToolLlama pass rate.

| Setting (ToolBench-G1, GPT-3.5) | Pass Rate |
|---|---|
| Oracle (pre-annotated) toolset | **62.00** |
| Tools retrieved by bge-large | **50.60** (▼ 11.40) |

> [!IMPORTANT]
> This is the thesis in one row: retrieval quality is **not** an academic IR metric — it's the ceiling on how well your agent can possibly perform. An 11-point pass-rate drop comes purely from feeding the same agent a worse-retrieved toolset.

### The fix: TOOLRET-train

| Ingredient | Detail |
|---|---|
| **Scale** | 200k+ training instances from ToolACE + APIGen + ToolBench training splits |
| **Each example** | query + generated instruction + target tools + **10 hard negatives** (mined by NV-Embed-v1) |
| **Objective** | Contrastive loss maximizing similarity of `instruction ⊕ query` to target tools over negatives (K=10, lr 5e-5) |
| **Result** | IR models trained on it improve nDCG@10 substantially **and** lift GPT-3.5 / ToolLlama pass rates by **10–20%** |

An ablation removing the instruction from the loss still helps over the untrained baseline, but underperforms the full instruction-tuned version — confirming **instructional training data** is the active ingredient.

**🗣️ In plain English:**

Once they proved the disease (retrievers can't find tools) and its damage (agents fail), they shipped the cure: a huge pile of practice problems where each question comes with the right tools, a hint, and ten *plausible-but-wrong* tools to learn to reject. Retrievers that drill on this stop being fooled — and the agents they feed get noticeably better at finishing tasks.

---

## What's Great / What Breaks

| ✅ Strengths | Why it matters |
|---|---|
| First systematic, large-scale tool-retrieval benchmark | Turns an ignored step into something you can *measure* |
| Heterogeneous & realistic (43k tools, 3 formats, 30+ sources) | Mirrors real toolsets, not a curated toy set |
| Ties retrieval metrics to **downstream pass rate** | Proves retrieval quality is the agent's performance ceiling |
| Ships a 200k instructional **training set**, not just a test | Plug-and-play improvement without re-training the LLM |
| Completeness@K metric | Honestly captures "you need *all* the tools, not most" |

| ⚠️ Limitations | Impact |
|---|---|
| **English & text only** | No multilingual or multimodal tool retrieval (flagged as future work) |
| **Retrieve-then-call only** | Doesn't test *interleaved* retrieve-and-call as the agent reasons step by step |
| **One-to-many label noise** | Merging datasets means a valid tool from dataset B may be marked "wrong" because only dataset A's annotation counts as ground truth |
| **Prompt sensitivity unstudied** | LLM-generated instructions vary with wording; not systematically probed |
| **Instructions are LLM-generated** | ~10.8% needed human revision; quality hinges on GPT-4o + review |

---

## The Business Problem

A wealth-management copilot must pick the right analytics tools from a **heterogeneous catalog** — Web-API quote feeds, Python risk functions, and in-house app actions — for each advisor query. But advisor questions ("trim my overweight tech") share almost no vocabulary with the tools they actually need (`sector_allocation` + `rebalance_portfolio`), and most tasks need **several** tools at once. Naïve embedding retrieval mis-selects as the catalog grows, and every mis-pick caps how well the agent can possibly perform. We build a miniature **TOOLRET** to measure exactly how bad that retrieval is — and how much an instruction layer fixes it.

> [!NOTE]
> **Synthetic / public data only.** Decision-support, not advice — no real client data or MNPI. The tool catalog, queries, and labels are all fabricated.

---

## From Paper to Practice

The companion build reconstructs TOOLRET in miniature over the wealth-management catalog: assemble a heterogeneous corpus + multi-target tasks, retrieve **with and without** an LLM-generated instruction, score **Completeness@k / nDCG@k**, prove that retrieved-vs-oracle toolsets cost real **pass-rate**, then close the gap with hard-negative mining + instruction augmentation. Completing every section forces you to touch **all 11 core aspects** of the paper. Notebook: [`builds/toolret.ipynb`](builds/toolret.ipynb).

| # | Paper aspect | Role in the build | Notebook section |
|---|---|---|---|
| 1 | Heterogeneous tool corpus (Web API / Code / Customized App) | A mixed-format catalog with a unified embeddable text view | S1 |
| 2 | Retrieval tasks (query → multi-target tools, MTEB-style) | The `GOLDEN` tasks: several correct tools per query | S2 |
| 3 | Lexical overlap analysis (ROUGE-L query↔target) | Show overlap ≈ 0 → semantic retrieval is mandatory | S3 |
| 4 | Target-aware instruction construction | LLM writes a relevance-criteria instruction per query from seeds | S4 |
| 5 | Dense retriever (embed → cosine → top-k) | The core 🎯 Select step under test | S5 |
| 6 | Sparse BM25 baseline | Reproduce "strong dense models can lose to lexical BM25" | S6 |
| 7 | Two settings: w/o inst. vs w/ inst. | Retrieve on query alone vs query⊕instruction | S7 |
| 8 | Metrics: nDCG@k, Recall@k, Precision@k, **Completeness@k** | Score retrieval; Completeness@k is all-or-nothing | S8 |
| 9 | Re-ranking (cross-encoder / LLM rerank) | Re-score the shortlist; observe it may *not* help | S9 |
| 10 | Downstream pass-rate vs oracle | Feed retrieved vs oracle tools to an agent; measure the drop | S10 |
| 11 | TOOLRET-train (hard-negative mining + instruction tuning) | Build (q, I, T⁺, T⁻) contrastive examples; show the w/ inst. lift | S11 |
| 12 | Wire-up into one graph | Assemble retrieve → rerank → agent → pass-rate as a LangGraph | S12 |

The signature metric to implement carefully is **Completeness@k** — the all-or-nothing measure that captures "you need *all* the tools, not most":

```python
def completeness_at_k(retrieved: list[str], targets: set[str], k: int) -> float:
    return 1.0 if targets.issubset(set(retrieved[:k])) else 0.0
```

---

## Connection to Context Engineering

TOOLRET is, at heart, a rigorous study of the **🎯 Select** strategy — and a warning about what happens when Select is done naively.

| Strategy | How TOOLRET applies |
|---|---|
| 🎯 **Select** | This *is* the paper. Tool retrieval = selecting which tools enter the context. TOOLRET proves naive selection (off-the-shelf retrievers) is far worse than assumed, and instruction-tuning makes selection sharper. |
| 🧱 **Isolate** | Retrieval is *why* you can isolate: you hand the agent only the top-k relevant tools, keeping its context lean instead of dumping 43k definitions in. |
| 🗜️ **Compress** | A 43k-tool corpus is compressed to a handful per query. Completeness@K measures whether that compression dropped a tool you actually needed. |
| ✍️ **Write** | The generated **instruction** is written context injected at the query boundary — engineered relevance criteria that bridge the 0.06 lexical gap. |

> [!NOTE]
> **Failure mode addressed: Context Confusion (and its cousin, Distraction).** If the retriever returns wrong or incomplete tools, the agent's context fills with irrelevant or insufficient options — it then calls the wrong tool or can't complete the task (the 11-point pass-rate drop). Good tool retrieval is the front-line defense against tool-confusion in large-toolset agents.

---

## Connection to Toolshed & Graph RAG-Tool Fusion

TOOLRET is the **evaluation/diagnosis** paper; [[toolshed]] and [[graph_rag_tool_fusion]] are the **treatment** papers. They form a natural trio.

| Dimension | TOOLRET (this paper) | Toolshed | Graph RAG-Tool Fusion |
|---|---|---|---|
| **Role** | Benchmark + training data | Method (RAG-Tool Fusion) | Method (graph traversal) |
| **Core claim** | Retrievers are *bad* at tool retrieval — here's proof + a fix | Enrich tool docs + ensemble RAG tricks to retrieve better | Add a dependency graph so you also fetch a tool's prerequisites |
| **Key artifact** | 43k-tool corpus, 7.6k tasks, 200k train set | Toolshed Knowledge Base + ARTF pipeline | Tool knowledge graph + ToolLinkOS benchmark |
| **Headline number** | Best model 33.83 nDCG@10; −11 pass rate from bad retrieval | +46–56% Recall@5 over BM25 | +71.7% / +22.1% mAP@10 over naive RAG |
| **Fine-tuning?** | TOOLRET-train *does* tune retrievers | No (RAG techniques only) | No (graph traversal only) |

> [!NOTE]
> Read together: TOOLRET tells you *how bad the problem is and gives you training data*; Toolshed and Graph RAG-Tool Fusion give you *training-free architectural fixes*. The strongest real system likely combines them — instruction-tuned retrievers (TOOLRET-train) **inside** an enriched, dependency-aware retrieval pipeline (Toolshed + Graph RAG).

---

## Connection to Reflexion & Generative Agents

The link is looser but instructive — all four are about **getting the right context into the window**, just at different layers.

| Paper | What it selects/writes into context | Relationship to TOOLRET |
|---|---|---|
| **TOOLRET** | The right *tools* (from 43k) | Select, at the tool layer |
| [[reflexion]] | The right *lessons* (from past failures) | Both compress a huge space into the few items that matter; Reflexion writes them, TOOLRET retrieves them |
| [[generative_agents]] | The right *memories* (recency × importance × relevance) | Generative Agents' retrieval scorer is the *memory* analogue of TOOLRET's *tool* retriever — same needle-in-haystack selection problem |

---

## Connection to This Project's Modules

| Repo module | Link to TOOLRET |
|---|---|
| `context_isolation/` *(planned)* | Tool retrieval is *how* you isolate context — show the agent the top-k tools, not all 43k. TOOLRET measures whether that top-k is any good. |
| `subagent_delegation/` *(planned)* | A sub-agent scoped to a task needs only *its* tools retrieved; poor retrieval poisons the sub-agent's context just as it does the main one. |
| [`long_term_memory/`](../long_term_memory/) | Tool retrieval and memory retrieval are the **same algorithm** on different corpora — both rank a large store against a query and inject the top-k. Lessons (and failure modes) transfer directly. |

---

**The takeaway:** TOOLRET pulls back the curtain on a step the whole tool-use field had been quietly skipping. By forcing retrievers to find the right tools among 43,000 — instead of grading agents on a pre-filtered shortlist — it shows that even state-of-the-art IR models are *not tool-savvy*: the best scores barely 33.83 nDCG@10, ColBERT loses to BM25, and re-ranking can make things worse. The reason is structural — tool queries and tool docs share almost no vocabulary (ROUGE-L 0.06) and tasks need several tools at once — so ordinary IR skill doesn't transfer. And it matters: feeding an agent retrieved instead of oracle tools costs ~11 points of pass rate. The cure is the same shape as the diagnosis — a 200k-instance instructional training set (TOOLRET-train) that makes retrievers tool-savvy and lifts downstream pass rates by 10–20%. For agent builders, the lesson is blunt: **your agent is only as good as its tool retriever, so measure it, instruction-tune it, and stop grading yourself on the answer key.**

---

## References

- [Retrieval Models Aren't Tool-Savvy: Benchmarking Tool Retrieval for Large Language Models — Shi, Wang, Yan, Ren, Wang, Yin, Ren, 2025 (arXiv:2503.01763)](https://arxiv.org/abs/2503.01763)
- Resources: [Tool-Retrieval-Benchmark on HuggingFace and project website](https://arxiv.org/abs/2503.01763) (see paper for live links)

# Context Engineering: Managing What LLMs Pay Attention To

---

## The Core Analogy

| Traditional OS | LLM System |
|---|---|
| CPU | The LLM itself |
| RAM (short-term memory) | The context window |
| OS memory manager | **Context engineering** |

Just as an operating system decides what goes into RAM, **context engineering** is the discipline of deciding what an LLM should hold in its context window — and what it should not.

---

## What Goes Into Context?

Context is everything the model can "see" when generating a response. It falls into three buckets:

![What goes into the Context Window](images/context_window_tree.png)

---

## Why Does This Matter Now?

Agents — systems that use LLMs and tools together over long, multi-step tasks — are surging in popularity because models have gotten better at reasoning and tool use.

But long tasks accumulate context fast: tool results, intermediate reasoning, gathered documents, conversation history. This creates a growing set of problems:

| Problem | Impact |
|---|---|
| Context window overflow | Task can't continue |
| Rising token costs & latency | Slower, more expensive runs |
| **Degraded performance** | The agent gets *worse* as context grows |

That last point is the crux of context engineering. **More context ≠ better performance.** In fact, mismanaged context actively harms agents in four distinct ways.

---

## The Four Failure Modes

### 1. Context Poisoning 🧪

> **When a mistake or hallucination enters the context and gets repeatedly referenced.**

Once an error is embedded in the context — a wrong fact, a hallucinated observation — the model treats it as ground truth. Every subsequent step builds on the mistake, compounding it.

**Real-world evidence:** Google DeepMind's Gemini 2.5 agent, while playing Pokémon, would occasionally hallucinate game states. When these hallucinations made it into the agent's "goals" section, it developed nonsensical strategies and repeated impossible behaviors — sometimes for a very long time before recovering.

> [!IMPORTANT]
> Poisoned context is self-reinforcing. The model references its own errors, which makes them harder to undo over time.

**🗣️ In plain English:**

Imagine you're following a recipe, and someone sneaks in a wrong instruction — "add 10 cups of salt instead of 1 teaspoon." You don't notice the mistake and follow it. Now every step after that builds on the salty disaster. You taste the soup, think "hmm, needs more sugar to balance the salt," and keep making adjustments based on the original error. The dish gets worse and worse, and you can't figure out why — because you trust the recipe.

That's context poisoning. One bad piece of information enters the model's memory, and everything that follows is built on that rotten foundation.

---

### 2. Context Distraction 🌫️

> **When context grows so large that the model over-focuses on it, neglecting what it learned during training.**

As an agent works, its context history balloons with past actions and observations. Eventually, the model starts *repeating past actions from its history* rather than synthesizing new strategies from its training.

**Real-world evidence:**
- The Pokémon-playing Gemini agent showed degraded reasoning beyond **~100k tokens**, favoring repetition of historical actions over novel planning.
- A Databricks study found model correctness began to drop around **~32k tokens** for Llama 3.1 405B, and even earlier for smaller models.

> [!WARNING]
> Models misbehave long before their context windows are full. Super-large context windows are useful for **summarization** and **fact retrieval** — but not for open-ended, multi-step reasoning.

**🗣️ In plain English:**

Imagine you're studying for an exam, and instead of reading the textbook, you read through *every single note you've ever taken* — 10 years' worth. At some point, you stop actually thinking about the questions and just start copying answers you wrote before, even if they were for a completely different subject. You have so much past material in front of you that you forget how to reason from scratch.

That's context distraction. The model has so much history piled up that it stops thinking creatively and just parrots what it did before.

---

### 3. Context Confusion 🔀

> **When irrelevant or unnecessary content in the context influences the model's output.**

If you put something in the context, the model *must* pay attention to it. Irrelevant tool definitions, unnecessary documents, or superfluous details don't get ignored — they actively degrade quality.

**Real-world evidence:**
- The **Berkeley Function-Calling Leaderboard** shows that every model performs worse when given more than one tool. Models will even call irrelevant tools when none of the provided tools are appropriate.
- On the **GeoEngine benchmark** (46 tools), a quantized Llama 3.1 8B failed with all 46 tools in context — but **succeeded with only 19**, even though 46 tools fit within its context window.

> [!TIP]
> Performance degrades proportionally with irrelevant context. Larger models handle it better, but no model is immune.

**🗣️ In plain English:**

Imagine you ask a handyman to fix your leaky faucet, but instead of just giving them a wrench, you dump the entire hardware store in front of them — drills, saws, paint rollers, gardening shears, everything. Now they're standing there thinking, "Maybe I should use the paint roller? The gardening shears look interesting too..." They have the wrench right there, but the sheer volume of irrelevant tools confuses them.

That's context confusion. The model can't ignore what you put in front of it, so irrelevant stuff actively pulls its attention away from what matters.

---

### 4. Context Clash ⚔️

> **When different parts of the context contain conflicting information.**

This is the most destructive variant of confusion: the problematic context isn't just irrelevant — it *directly contradicts* other information the model is supposed to use.

**Real-world evidence:** A Microsoft/Salesforce study took benchmark prompts and "sharded" them across multiple conversational turns (simulating how real users interact). Results:

| Delivery Method | Average Performance |
|---|---|
| All info in one prompt | Baseline |
| Same info across multiple turns | **↓ 39% drop** |

Even OpenAI's o3 dropped from **98.1 → 64.1**. Why? Early turns contained the model's premature (incorrect) attempts at answers. These wrong answers stayed in the context and *conflicted* with later, corrected information — and the model couldn't recover.

> [!CAUTION]
> Agents are especially vulnerable here. They assemble context from diverse sources — documents, tool calls, sub-agent outputs, MCP servers — all of which can disagree with each other.

**🗣️ In plain English:**

Imagine you're assembling IKEA furniture and you have two instruction manuals — one says "attach part A to part B," and the other says "never connect A and B directly." Both are sitting right in front of you. You're stuck. You might follow one, then second-guess yourself and try the other, and end up with a wobbly mess.

That's context clash. The model is given contradictory information in its context and can't decide which to trust, so its output suffers.

---

## The Bottom Line

![Bigger context windows create new failure modes](images/failure_modes_flow.png)

Million-token context windows are powerful — but **more context is not automatically better**. These failures hit agents hardest because agents operate in exactly the scenarios where contexts balloon:

- Gathering info from multiple sources
- Making sequential tool calls
- Engaging in multi-turn reasoning
- Accumulating extensive histories

**Context engineering is not about how much you *can* fit — it's about choosing what *should* go in.**

---

## How Are These Failures Different? A Side-by-Side Comparison

All four failure modes stem from mismanaged context, but they break things in fundamentally different ways. Here's how to tell them apart.

### 🗣️ The Layman's Comparison

| Failure Mode | Everyday Analogy | What Goes Wrong | Why It Happens |
|---|---|---|---|
| **🧪 Poisoning** | A wrong ingredient in a recipe ruins every dish built on it | One bad fact enters memory and the model keeps trusting it | The model generated or received an error and now treats it as truth |
| **🌫️ Distraction** | Reading 10 years of old notes before an exam makes you copy old answers instead of thinking | Too much history makes the model repeat itself instead of reasoning | The sheer volume of accumulated context drowns out the model's own training |
| **🔀 Confusion** | Dumping the entire hardware store in front of a plumber who just needs a wrench | Irrelevant info in the context pulls the model off track | The model *must* attend to everything in context — it can't selectively ignore items |
| **⚔️ Clash** | Two contradictory instruction manuals for the same IKEA shelf | Conflicting facts in the context make the model produce inconsistent output | Different sources (tools, documents, prior turns) provide contradictory information |

### 🔬 The Technical Comparison

| Dimension | 🧪 Poisoning | 🌫️ Distraction | 🔀 Confusion | ⚔️ Clash |
|---|---|---|---|---|
| **What enters context** | Incorrect/hallucinated information | Correct but excessive historical information | Correct but irrelevant information | Correct but mutually contradictory information |
| **Is the bad context factually wrong?** | ✅ Yes — it's an error or hallucination | ❌ No — it's real, just too much | ❌ No — it's real, just not needed | ❌/✅ Each piece may be valid on its own, but they conflict |
| **How does it degrade performance?** | Errors compound — each step builds on the mistake | Model defaults to repeating past actions instead of reasoning | Attention is diluted across irrelevant items, reducing precision | Model can't resolve contradictions, produces inconsistent or wrong outputs |
| **Self-inflicted or external?** | Often self-inflicted (model's own hallucinations) | Self-inflicted (model's own growing history) | External (developer stuffed too much in) | Both (multi-source aggregation + model's own early attempts) |
| **When does it typically occur?** | Mid-task, after a hallucination event | Late in long tasks, as context balloons | At task start, due to prompt/tool design | During multi-turn or multi-source workflows |
| **Failure pattern** | Cascading — errors snowball | Gradual — quality slowly degrades | Immediate — quality drops as soon as irrelevant context is added | Sudden — contradictions cause sharp drops in coherence |
| **Fix strategy** | Validate outputs before they enter context; use guardrails | Summarize/compress history; rotate context windows | Curate tools and docs; only include what's relevant to the current step | Deduplicate and reconcile sources; clear stale/incorrect prior turns |

### 🌳 Root Cause Breakdown

![Root cause decision tree for diagnosing context failures](images/root_cause_tree.png)

**Reading the decision tree:**

1. **Is the bad context actually wrong?** → If yes, it's **Poisoning**. A lie got into the system.
2. **Is it correct but has nothing to do with the task?** → That's **Confusion**. Junk is cluttering the workspace.
3. **Is it correct and relevant but fights with other correct info?** → That's a **Clash**. The model is getting contradictory orders.
4. **Is it correct, relevant, and consistent — but there's just too damn much of it?** → That's **Distraction**. The model is drowning in its own history.

> [!NOTE]
> In practice, these failure modes often co-occur. A long-running agent might experience **Distraction** (ballooning history) that makes it more susceptible to **Confusion** (losing focus on what's relevant), while a hallucination creates **Poisoning** that later causes a **Clash** with corrected information. Good context engineering guards against all four simultaneously.

---

**The takeaway:** All four failures share one root cause — *the model was given context it shouldn't have had, or wasn't given context it needed.* Context engineering is the practice of being ruthlessly intentional about what enters the context window, when it enters, and how long it stays.

---

## Solving the Context Problem: Four Strategies

Anthropic, in their research on building effective agents, stressed the urgency:

> **Agents often have conversations with hundreds of turns, so managing context carefully is crucial.**

So how are practitioners solving this problem today? The common strategies for agent context engineering can be grouped into four main types:

| Strategy | Core Idea | One-Liner |
|---|---|---|
| ✍️ **Write** | Craft clear, useful context from the start | *Give the model the right script before it steps on stage* |
| 🎯 **Select** | Pick only the most relevant information | *Hand the plumber a wrench, not the entire hardware store* |
| 🗜️ **Compress** | Shorten context to save space | *Summarize the novel into chapter notes* |
| 🧱 **Isolate** | Keep different types of context separate | *Don't mix the recipe book with the tax returns* |


![The four context engineering strategies: Write, Select, Compress, Isolate](images/four_strategies.png)

---

### 1. Write ✍️

> **Creating clear and useful context — before the model ever sees a prompt.**

Writing is the most proactive strategy: instead of reacting to context problems *after* they emerge, you engineer high-quality context *upfront*. This includes crafting precise system prompts, writing unambiguous tool descriptions, structuring few-shot examples, and defining output schemas that leave no room for misinterpretation.

**🗣️ In plain English:**

Think of it like writing a brief for a new employee on their first day. If the brief is vague — "just handle customer issues" — they'll flounder. But if it says "greet the customer by name, check their order status in System X, and escalate billing disputes to Team Y" — they hit the ground running. Writing good context is writing a good brief.

> [!TIP]
> The highest-leverage context engineering you can do is often the simplest: rewrite a vague system prompt into a specific, structured one. Models follow clear instructions far more reliably than clever ones.

---

### 2. Select 🎯

> **Picking only the most relevant information for the current step.**

Selection is about *what enters the context window* — and, critically, what doesn't. This means dynamically choosing which documents to retrieve, which tools to expose, and which conversation history to include based on the agent's current task. RAG (Retrieval-Augmented Generation) is the most common selection mechanism, but tool filtering, relevant-history windowing, and conditional prompt assembly all fall under this umbrella.

**🗣️ In plain English:**

Imagine you're studying for a biology exam, but someone dumps your entire school transcript on your desk — math homework, English essays, gym class attendance. You *could* read through it all, but you'd waste time and get confused. Selection means pulling out just the biology notes and leaving everything else in the drawer.

> [!IMPORTANT]
> Selection directly combats **Context Confusion** and **Context Distraction**. If irrelevant information never enters the context window, it can't degrade performance.

---

### 3. Compress 🗜️

> **Shortening context to save space without losing essential meaning.**

Compression tackles the inevitable growth of context over long-running agent tasks. Instead of feeding the model every raw tool output, every verbose API response, and every turn of dialogue verbatim, you summarize, truncate, or distill. Techniques include rolling conversation summaries, extracting key facts from tool outputs, and replacing verbose documents with structured bullet points.

**🗣️ In plain English:**

It's like taking meeting notes. Nobody replays the entire two-hour recording before the next meeting — you read the one-page summary of decisions made and action items. Compression gives the model the summary instead of the full recording, keeping it focused and fast.

> [!WARNING]
> Compression is a lossy operation. Every time you summarize, you risk dropping a detail that matters later. The art is knowing *what* to compress and *when* — aggressive early summarization can cause the same problems as Context Poisoning if the summary itself is inaccurate.

---

### 4. Isolate 🧱

> **Keeping different types of context separate so they don't interfere with each other.**

Isolation means architecturally separating concerns: giving sub-agents their own context windows, maintaining separate memory stores for different task types, or splitting long workflows into independent stages that don't share a single ballooning context. This prevents cross-contamination between unrelated tasks and limits the blast radius when context goes wrong in one area.

**🗣️ In plain English:**

Think of a hospital. The ER doesn't share a single whiteboard with the pharmacy, the radiology lab, and the cafeteria. Each department has its own workspace, its own notes, and its own priorities. When they need to coordinate, they pass specific, structured information — not their entire internal state. Isolation gives each part of the agent system its own clean workspace.

> [!NOTE]
> Isolation is the primary defense against **Context Clash**. When sub-agents or tool calls operate in separate contexts, contradictory information from one source can't corrupt another.

---

### How the Strategies Map to the Failure Modes

| Strategy | 🧪 Poisoning | 🌫️ Distraction | 🔀 Confusion | ⚔️ Clash |
|---|---|---|---|---|
| ✍️ **Write** | ✅ Clear instructions reduce hallucination triggers | ✅ Focused prompts keep the model on-task | ✅ Precise tool descriptions prevent mis-selection | ⚠️ Helps indirectly by reducing ambiguity |
| 🎯 **Select** | ⚠️ Can filter out poisoned content if detected | ✅ Keeps only relevant history in view | ✅ **Primary defense** — irrelevant content never enters | ⚠️ Helps if conflicting sources are excluded |
| 🗜️ **Compress** | ⚠️ Risky — summaries can propagate errors | ✅ **Primary defense** — shrinks ballooning history | ⚠️ Reduces volume but not relevance | ⚠️ Can accidentally merge conflicting facts |
| 🧱 **Isolate** | ✅ Limits blast radius of poisoned context | ⚠️ Helps by keeping each agent's context small | ⚠️ Helps by scoping each agent's tools | ✅ **Primary defense** — sources can't contradict each other |

**The takeaway:** No single strategy solves all four failure modes. Effective context engineering combines all four — **Write** good context, **Select** the right pieces, **Compress** what's too long, and **Isolate** what shouldn't mix — to keep agents sharp over hundreds of turns.

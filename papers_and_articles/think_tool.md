# The "Think" Tool: Giving Claude a Scratchpad Mid-Action

---

## The Core Idea

| Concept | What It Means |
|---|---|
| Extended Thinking | What Claude does *before* it starts generating a response — deep planning and iteration |
| **Think Tool** | What Claude does *during* a response — pausing mid-action to reason about new information |
| The difference | Extended thinking = pre-flight checklist. Think tool = in-flight course correction. |

The "think" tool gives Claude a **dedicated scratchpad** — a place to stop, reason about tool results, verify policy compliance, and plan its next move — all *within* an ongoing tool-use chain. It doesn't fetch new information or change any state. It just thinks.

![Extended Thinking vs Think Tool comparison](images/think_vs_extended.png)

---

## Why Does This Matter?

Agentic workflows — where Claude chains together multiple tool calls over many steps — are where mistakes compound fastest. Without a structured place to pause and reason:

| Problem | What Happens |
|---|---|
| Skipped policy checks | Claude acts before verifying it's allowed to |
| Misread tool outputs | Results from one tool are misinterpreted before the next call |
| Cascading errors | One wrong step early in the chain poisons every subsequent action |
| Inconsistent behavior | The same task yields different results across runs |

> [!IMPORTANT]
> The "think" tool is not about making Claude *smarter* — it's about giving it **space to be careful**. In complex, policy-heavy, multi-step workflows, that space is the difference between reliable and unreliable.

**🗣️ In plain English:**

Imagine a surgeon in the middle of an operation. They don't just cut-cut-cut without pausing. At key moments, they stop, examine what they see, consult the scan on the monitor, check the patient's vitals, and *then* proceed. The "think" tool is that pause — a moment where Claude looks at what just happened before deciding what to do next.

---

## How Does It Work?

![How the Think Tool fits into an agentic workflow](images/think_tool_flow.png)

The implementation is deceptively simple. You add a tool definition — literally a JSON object — to your tool list. When Claude decides it needs to reason through something, it "calls" this tool with its thought. The tool does nothing except log the thought. But that act of writing out the reasoning forces structured deliberation.

### The Tool Definition (from τ-Bench)

```json
{
  "name": "think",
  "description": "Use the tool to think about something. It will not obtain new information or change the database, but just append the thought to the log. Use it when complex reasoning or some cache memory is needed.",
  "input_schema": {
    "type": "object",
    "properties": {
      "thought": {
        "type": "string",
        "description": "A thought to think about."
      }
    },
    "required": ["thought"]
  }
}
```

**🗣️ In plain English:**

It's like giving someone a sticky note during a meeting. They don't have to use it, but when the discussion gets complicated — "Wait, did they say the budget was $50k or $500k?" — they jot down a note, double-check their reasoning, and *then* speak up. Without the sticky note, they'd just blurt out whatever felt right.

---

## The Evidence: τ-Bench Results

Anthropic evaluated the "think" tool using [τ-bench (tau-bench)](https://arxiv.org/abs/2406.12045), a benchmark that tests an LLM's ability to handle realistic customer service scenarios — navigating complex policies, using tools to access databases, and maintaining consistency across multiple interactions.

The key metric is **pass^k** — the probability that *all* k independent trials succeed for a given task. Unlike pass@k (where at least one success counts), pass^k measures **consistency and reliability** — exactly what you need in production customer service systems.

### Airline Domain (Hard)

> The airline domain has notoriously complex policies — cancellation rules, baggage calculations, payment restrictions, membership tiers. This is where the "think" tool shines brightest.

| Configuration | *k*=1 | *k*=2 | *k*=3 | *k*=4 | *k*=5 |
|---|---|---|---|---|---|
| **"Think" + Optimized Prompt** | **0.584** | **0.444** | **0.384** | **0.356** | **0.340** |
| "Think" alone | 0.404 | 0.254 | 0.186 | 0.140 | 0.100 |
| Extended Thinking | 0.412 | 0.290 | 0.232 | 0.192 | 0.160 |
| Baseline | 0.332 | 0.206 | 0.148 | 0.116 | 0.100 |

- **54% relative improvement** at pass^1 (0.584 vs. 0.370 baseline)
- The "think" tool with optimized prompting **dramatically outperformed** both extended thinking and baseline
- Gains held across all k values, meaning **consistency improved**, not just peak performance

### Retail Domain (Easier)

| Configuration | *k*=1 | *k*=2 | *k*=3 | *k*=4 | *k*=5 |
|---|---|---|---|---|---|
| **"Think" (no prompt)** | **0.812** | **0.735** | **0.685** | **0.650** | **0.626** |
| Extended Thinking | 0.770 | 0.681 | 0.623 | 0.581 | 0.548 |
| Baseline | 0.783 | 0.695 | 0.643 | 0.607 | 0.583 |

- Even **without** an optimized prompt, the "think" tool achieved the highest pass^1 score of **0.812**
- For simpler domains, just having the space to think was enough — no additional prompting required

> [!NOTE]
> The retail policy is significantly easier to navigate than the airline domain. Claude was able to self-improve just by having a scratchpad — no hand-holding needed.

### SWE-Bench (Code)

A domain-adapted "think" tool contributed to Claude 3.7 Sonnet's **state-of-the-art SWE-bench score of 0.623**. In isolated experiments (n=30 with "think" vs. n=144 without), the tool improved performance by **1.6% on average** — statistically significant (Welch's *t*-test: *t*(38.89) = 6.71, *p* < .001, *d* = 1.47).

The SWE-bench variant used a more coding-specific description:

```json
{
  "name": "think",
  "description": "Use the tool to think about something. It will not obtain new information or make any changes to the repository, but just log the thought. Use it when complex reasoning or brainstorming is needed. For example, if you explore the repo and discover the source of a bug, call this tool to brainstorm several unique ways of fixing the bug, and assess which change(s) are likely to be simplest and most effective. Alternatively, if you receive some test results, call this tool to brainstorm ways to fix the failing tests.",
  "input_schema": {
    "type": "object",
    "properties": {
      "thought": {
        "type": "string",
        "description": "Your thoughts."
      }
    },
    "required": ["thought"]
  }
}
```

---

## Key Insight: Prompting Multiplies the Effect

The single most important finding from the τ-bench experiments is that **the "think" tool alone helps, but the "think" tool + optimized prompting is transformative**.

| Approach | Airline pass^1 | Improvement |
|---|---|---|
| Baseline (no think, no extended thinking) | 0.332 | — |
| Extended Thinking alone | 0.412 | +24% |
| "Think" tool alone | 0.404 | +22% |
| **"Think" tool + optimized prompt** | **0.584** | **+76%** |

The optimized prompt gives Claude **examples of how to think** — not just permission to think. Here's the prompt that achieved the best results:

```
## Using the think tool

Before taking any action or responding to the user after receiving tool results,
use the think tool as a scratchpad to:
- List the specific rules that apply to the current request
- Check if all required information is collected
- Verify that the planned action complies with all policies
- Iterate over tool results for correctness

Here are some examples of what to iterate over inside the think tool:

<think_tool_example_1>
User wants to cancel flight ABC123
- Need to verify: user ID, reservation ID, reason
- Check cancellation rules:
  * Is it within 24h of booking?
  * If not, check ticket class and insurance
- Verify no segments flown or are in the past
- Plan: collect missing info, verify rules, get confirmation
</think_tool_example_1>

<think_tool_example_2>
User wants to book 3 tickets to NYC with 2 checked bags each
- Need user ID to check:
  * Membership tier for baggage allowance
  * Which payments methods exist in profile
- Baggage calculation:
  * Economy class × 3 passengers
  * If regular member: 1 free bag each → 3 extra bags = $150
  * If silver member: 2 free bags each → 0 extra bags = $0
  * If gold member: 3 free bags each → 0 extra bags = $0
- Payment rules to verify:
  * Max 1 travel certificate, 1 credit card, 3 gift cards
  * All payment methods must be in profile
  * Travel certificate remainder goes to waste
- Plan:
1. Get user ID
2. Verify membership level for bag fees
3. Check which payment methods in profile and if their combination is allowed
4. Calculate total: ticket price + any bag fees
5. Get explicit confirmation for booking
</think_tool_example_2>
```

**🗣️ In plain English:**

It's the difference between telling someone "feel free to take notes" and handing them a structured template: "Here's how to take notes — break the problem into these categories, check these specific things, and plan your next steps like this." The template doesn't just give permission — it teaches a method.

> [!TIP]
> Place complex "think" tool guidance in the **system prompt**, not in the tool description. The system prompt provides broader context and helps the model integrate thinking into its overall behavior more naturally.

---

## When to Use the Think Tool

![Decision tree for when to use the Think Tool](images/think_tool_decision.png)

### ✅ Use the Think Tool When:

| Scenario | Why It Helps |
|---|---|
| **Tool output analysis** | Claude needs to carefully process previous tool results before acting — and might need to backtrack |
| **Policy-heavy environments** | Detailed guidelines require step-by-step verification before each action |
| **Sequential decision making** | Each action builds on previous ones, and mistakes are costly and compound |
| **Long tool call chains** | Many steps in sequence where mid-chain reasoning prevents drift |

### ❌ Don't Use the Think Tool When:

| Scenario | Why It Doesn't Help |
|---|---|
| **Non-sequential tool calls** | Single calls or parallel calls don't benefit from mid-chain reasoning |
| **Simple instruction following** | Few constraints, default behavior is already good enough |
| **Pure reasoning tasks** | Coding, math, physics without tool use — use Extended Thinking instead |

> [!WARNING]
> The "think" tool does add output tokens (the thoughts themselves). In scenarios where it doesn't help, you're paying for extra tokens with no benefit. Be selective.

---

## Implementation Best Practices

### 1. Strategic Prompting with Domain-Specific Examples

> **The most effective approach is to provide clear instructions on when and how to use the "think" tool, tailored to your domain.**

Your optimized prompt should model:
- The **level of detail** expected in reasoning
- How to **break down complex instructions** into actionable steps
- **Decision trees** for handling common scenarios
- How to **check if all necessary information has been collected**

### 2. Place Complex Guidance in the System Prompt

When "think" tool instructions are long or complex, placing them in the **system prompt** is more effective than cramming them into the tool description. The system prompt gives the model broader context for when and how to integrate thinking into its workflow.

### 3. Monitor and Refine

Watch how Claude uses the tool in practice:
- Is it thinking at the right moments?
- Are the thoughts structured and useful?
- Adjust your prompting to encourage more effective thinking patterns

---

## The Connection to Context Engineering

The "think" tool is a form of **context engineering** — specifically, it's an example of the **Write ✍️** and **Isolate 🧱** strategies working together:

| Strategy | How the Think Tool Applies |
|---|---|
| ✍️ **Write** | The optimized prompt *writes* high-quality reasoning examples into the context, showing Claude *how* to think |
| 🧱 **Isolate** | The tool creates a *separate thinking space* — reasoning that's structurally distinct from tool calls and responses |
| 🎯 **Select** | Claude *selects* when to think — it's not forced to think at every step, only when complexity demands it |
| 🗜️ **Compress** | The act of thinking *compresses* complex multi-step reasoning into a structured summary before acting |

> [!NOTE]
> The "think" tool directly combats **Context Distraction** and **Context Confusion**. By giving Claude a structured pause, it prevents the model from blindly repeating patterns from its growing context history, and forces it to actively reason about what's relevant *right now*.

---

**The takeaway:** The "think" tool is a minimal-effort, high-impact technique. For simple tasks, Extended Thinking is sufficient. But for complex, policy-heavy, multi-step agentic workflows — especially those with long tool call chains — giving Claude a scratchpad to pause and reason mid-action can improve performance by **up to 76%**. And the best part: pairing it with a well-crafted prompt that teaches Claude *how* to think is what turns a good tool into a great one.

---

## References

- [The "think" tool: Enabling Claude to stop and think in complex tool use situations — Anthropic Engineering](https://www.anthropic.com/engineering/claude-think-tool)

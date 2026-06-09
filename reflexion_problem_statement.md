# Problem Statement: Reflexion-Based Client Investment Proposal Generator

## The Business Problem

A wealth management firm onboards new clients daily. For each client, an **AI advisor agent** must generate a personalized investment proposal — a recommended portfolio of specific funds, ETFs, and asset allocations tailored to that client's financial situation, goals, and constraints.

This sounds straightforward, but in practice it's a **multi-constraint suitability problem** governed by regulatory rules (SEC/FINRA suitability obligations), firm policies, and client-specific preferences that frequently conflict with each other:

| Constraint Category | Examples |
|---|---|
| **Regulatory suitability** | A retiree living on fixed income cannot be placed into a high-volatility growth portfolio, even if the expected return is higher |
| **Risk tolerance alignment** | Client scored "conservative" on the risk questionnaire → equity allocation must stay below 40% |
| **Liquidity needs** | Client needs $50K for a home down payment in 18 months → cannot lock funds in illiquid alternatives |
| **ESG / values-based screens** | Client explicitly excludes fossil fuels, tobacco, and weapons manufacturers |
| **Fee sensitivity** | Client's stated preference for low-cost funds → proposal should not include funds with expense ratios above 0.5% |
| **Tax situation** | Client is in the highest marginal bracket → should favor municipal bonds and tax-efficient index funds over actively managed funds with high turnover |
| **Concentration limits** | Firm policy: no single holding may exceed 10% of the proposed portfolio |
| **Minimum diversification** | At least 4 asset classes must be represented |

> [!IMPORTANT]
> The core challenge is that these constraints **interact**. Satisfying the client's ESG screen might push the agent toward a small set of specialty funds that are expensive (violating fee sensitivity) and concentrated (violating diversification rules). A naive proposal that optimizes for one constraint often violates another. The agent needs to **fail, understand why, and adjust** — which is exactly the Reflexion pattern.

---

## Why Reflexion Fits This Problem

### Why a single-shot LLM call isn't enough

An LLM given all the constraints in one prompt will frequently:
- Miss subtle interactions between constraints (ESG screen + fee cap + diversification creates a very narrow feasible set)
- Hallucinate fund tickers that don't exist or misstate expense ratios
- Satisfy the "letter" of a constraint but not the "spirit" (e.g., technically 4 asset classes, but 85% in one)
- Overlook the client's stated preferences buried in a long intake form

### Why scalar feedback isn't enough

A compliance system that returns "Suitability Score: 0.6" tells the agent nothing. But a reflection that says *"I recommended ARKK (expense ratio 0.75%) for a fee-sensitive client — I need to find a growth ETF under 0.50%, such as VUG (0.04%)"* is directly actionable.

### The Reflexion mapping

| Reflexion Component | Role in This Problem |
|---|---|
| **Actor** | Generates the investment proposal (fund selections, allocations, rationale) |
| **Evaluator** | Checks the proposal against all suitability rules, firm policies, and client constraints — returns a structured violation report |
| **Self-Reflection** | Analyzes the violations and writes a verbal lesson: what went wrong, why, and what to do differently |
| **Memory** | Carries 1–3 past reflections into the next attempt so the agent doesn't repeat the same mistakes |

---

## Concrete Example: Client "Raj Patel"

### Client Intake Summary

```
Client:        Raj Patel, age 62, retiring in 3 years
Income:        $210,000/year (highest marginal tax bracket: 37%)
Investable:    $850,000 (rollover from 401k + taxable brokerage)
Risk Score:    Conservative (questionnaire score: 28/100)
Liquidity:     Needs $120,000 accessible within 12 months (home renovation)
ESG Screen:    Excludes fossil fuels and tobacco
Fee Pref:      "I don't want to pay high fees" → expense ratio cap: 0.50%
Goals:         Capital preservation + income generation for retirement
```

---

### Trial 1 — The Actor's First Proposal

The agent generates:

```
PROPOSED PORTFOLIO FOR RAJ PATEL
─────────────────────────────────
  35%  BND   (Vanguard Total Bond Market ETF)        — Fixed Income
  20%  VYM   (Vanguard High Dividend Yield ETF)      — US Equity / Income
  15%  VXUS  (Vanguard Total Intl Stock ETF)          — International Equity
  15%  XLE   (Energy Select Sector SPDR)              — Energy Sector
  10%  PAXLX (Pax Large Cap Fund)                     — ESG Large-Cap
   5%  Cash  (Money Market)                           — Liquidity

Rationale: Conservative allocation with income focus. BND provides
stability, VYM generates dividends, VXUS adds international
diversification, XLE provides commodity exposure for inflation
hedging, PAXLX satisfies ESG preference.
```

### Trial 1 — Evaluator Violation Report

```
❌ VIOLATION: ESG Screen
   XLE (Energy Select Sector SPDR) holds major fossil fuel companies
   (ExxonMobil, Chevron, ConocoPhillips). Client explicitly excludes
   fossil fuels. This is a hard suitability failure.

❌ VIOLATION: Fee Sensitivity
   PAXLX has an expense ratio of 0.81%, exceeding the client's 0.50% cap.

❌ VIOLATION: Liquidity Needs
   Client needs $120,000 within 12 months. Cash allocation is only 5%
   ($42,500). Even adding liquid equity positions, the proposal doesn't
   clearly earmark sufficient liquid reserves for the renovation.

⚠️ WARNING: Risk Alignment
   Total equity exposure = 60% (VYM 20% + VXUS 15% + XLE 15% + PAXLX 10%).
   For a conservative client (score 28/100), equity should be ≤ 40%.

⚠️ WARNING: Tax Efficiency
   No municipal bond allocation despite client being in the 37% bracket.
   BND holds taxable bonds — interest taxed at ordinary income rates.

RESULT: FAIL (3 hard violations, 2 warnings)
```

### Trial 1 — Self-Reflection

```
REFLECTION #1:
"I made three critical errors:
(1) I included XLE for inflation hedging, but XLE is a fossil fuel
    energy ETF — directly violating Raj's ESG exclusion. For inflation
    hedging without fossil fuels, I should use TIP (iShares TIPS Bond
    ETF) or a clean energy fund like ICLN.
(2) I chose PAXLX (0.81% expense ratio) as the ESG fund. I should use
    ESGV (Vanguard ESG US Stock ETF, 0.09%) instead — much cheaper and
    still ESG-screened.
(3) I allocated only 5% to cash ($42,500), but Raj needs $120,000
    liquid within 12 months. I need to set aside at least 15% in cash
    or short-term instruments to cover this.
Also, total equity is 60% but should be ≤ 40% for a conservative
profile. And I should add municipal bonds (VTEB) instead of all
taxable bonds given his 37% tax bracket."
```

### Trial 2 — The Actor Retries (Conditioned on Reflection #1)

```
PROPOSED PORTFOLIO FOR RAJ PATEL (Revised)
───────────────────────────────────────────
  25%  VTEB  (Vanguard Tax-Exempt Bond ETF)           — Muni Bonds
  20%  BND   (Vanguard Total Bond Market ETF)         — Taxable Bonds
  10%  TIP   (iShares TIPS Bond ETF)                  — Inflation Protection
  10%  ESGV  (Vanguard ESG US Stock ETF)              — ESG US Equity
  10%  VYM   (Vanguard High Dividend Yield ETF)       — Dividend Income
   5%  VXUS  (Vanguard Total Intl Stock ETF)          — Intl Diversification
   5%  VNQ   (Vanguard Real Estate ETF)               — Real Assets
  15%  Cash  (Money Market / Short-Term Treasuries)   — Liquidity Reserve

Rationale: Reduced equity to 30% (conservative). Added VTEB for
tax-exempt income. Replaced XLE with TIP (inflation hedge, no fossil
fuels). Replaced PAXLX with ESGV (0.09% ER). Increased cash to 15%
($127,500) to cover the $120K liquidity need.
```

### Trial 2 — Evaluator Report

```
✅ ESG Screen:       No holdings violate fossil fuel or tobacco exclusions
✅ Fee Sensitivity:  All funds ≤ 0.50% expense ratio (highest: ESGV at 0.09%)
✅ Liquidity:        Cash = 15% ($127,500) > $120,000 requirement
✅ Risk Alignment:   Equity = 30% ≤ 40% cap for conservative profile
✅ Tax Efficiency:   25% in munis (VTEB) — appropriate for 37% bracket
✅ Concentration:    No single holding exceeds 10% (largest: VTEB at 25%...

⚠️ WARNING: Concentration
   VTEB at 25% exceeds the firm's 10% single-holding concentration limit.

RESULT: FAIL (1 hard violation)
```

### Trial 2 — Self-Reflection

```
REFLECTION #2:
"Almost there. The only remaining violation is VTEB at 25% — it
exceeds the firm's 10% concentration limit per holding. I need to split
the municipal bond allocation across two or more muni funds. I can use
VTEB (Vanguard national munis) and TFI (SPDR Nuveen Muni Bond ETF) to
spread the allocation while maintaining tax-exempt exposure. I'll
allocate 10% to each, and shift the remaining 5% into BND to stay
diversified."
```

### Trial 3 — Final Attempt (Conditioned on Reflections #1 + #2)

```
PROPOSED PORTFOLIO FOR RAJ PATEL (Final)
────────────────────────────────────────
  10%  VTEB  (Vanguard Tax-Exempt Bond ETF)           — Muni Bonds
  10%  TFI   (SPDR Nuveen Muni Bond ETF)              — Muni Bonds
   5%  MUB   (iShares National Muni Bond ETF)         — Muni Bonds
  10%  BND   (Vanguard Total Bond Market ETF)         — Taxable Bonds
  10%  TIP   (iShares TIPS Bond ETF)                  — Inflation Protection
  10%  ESGV  (Vanguard ESG US Stock ETF)              — ESG US Equity
  10%  VYM   (Vanguard High Dividend Yield ETF)       — Dividend Income
   5%  VXUS  (Vanguard Total Intl Stock ETF)          — Intl Diversification
   5%  VNQ   (Vanguard Real Estate ETF)               — Real Assets
  15%  Cash  (Money Market / Short-Term Treasuries)   — Liquidity Reserve
```

### Trial 3 — Evaluator Report

```
✅ ESG Screen:        All clear
✅ Fee Sensitivity:   All funds under 0.50%
✅ Liquidity:         $127,500 cash > $120,000 need
✅ Risk Alignment:    Equity = 30%, within conservative cap
✅ Tax Efficiency:    25% in munis across 3 funds
✅ Concentration:     No holding exceeds 10%
✅ Diversification:   6 asset classes represented (bonds, munis, equity,
                      intl, real estate, cash)

RESULT: PASS ✓ — Proposal is compliant and suitable.
```

---

## Why This Example Demonstrates Reflexion's Value

| Reflexion Principle | How This Example Shows It |
|---|---|
| **Language > scalar rewards** | "PAXLX has 0.81% ER, use ESGV at 0.09% instead" is infinitely more useful than "score: 0.6" |
| **Memory prevents repeated mistakes** | The agent never re-introduces fossil fuel funds or high-fee funds after reflecting on those errors |
| **Iterative convergence** | Trial 1 had 5 issues → Trial 2 had 1 issue → Trial 3 passed. Each reflection narrowed the error surface |
| **Interpretable learning** | A compliance officer can read the reflections and verify the agent's reasoning — essential in regulated finance |
| **Constraint interaction discovery** | The agent discovered that ESG + low fees + diversification creates tension — something a single prompt doesn't anticipate |

> [!NOTE]
> In a production setting, the **Evaluator is deterministic** (coded rules, not LLM-based) to avoid false positives — the same lesson from Reflexion's MBPP results where a 16.3% false-positive rate in self-generated tests caused incorrect submissions. Financial compliance checking must be exact.

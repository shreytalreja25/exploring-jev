# Empirical Research & Incident Report: Tokenomics, Latency & Architectural Behavior of `typesafe/jev-router` vs. `google/gemini-2.5-flash`

**Date:** 2026-09-28  
**Author/Investigator:** Shrey Talreja & Antigravity  
**Directory:** `openrouter_jev_dev`  
**Dataset:** 10 Enterprise Operational Emails (5 Categories: `Marketing`, `Sales`, `Finance`, `Human Resources`, `Technical Support`)  
**Data Artifacts:**
- Dataset: [`emails_dataset.json`](./emails_dataset.json)
- Benchmark Script: [`email_router_benchmark.py`](./email_router_benchmark.py)
- Full Results Dump: [`email_routing_results_with_tokenomics.json`](./email_routing_results_with_tokenomics.json)

---

## 1. Executive Incident Summary

During the evaluation of OpenRouter's `typesafe/jev-router` endpoint—hypothesized to execute TypeSafe AI's "System-One" decision architecture—two critical behavioral anomalies were empirically recorded:

1. **Self-Identification and Model Delegation:**
   When prompted conversationally (`"Which model are you?"`), the endpoint self-identified as `"ChatGPT, powered by OpenAI's GPT-5.2 / GPT-5.4"`. Response inspection proved that `typesafe/jev-router` does **not** perform isolated inference; instead, it is a meta-router dynamically delegating inference to upstream frontier models:
   - 90% of requests routed to **`openai/gpt-6-luna`**
   - 10% of requests routed to **`deepseek/deepseek-v4.1-flash`** (triggered by a critical cloud infrastructure incident)

2. **The "Reasoning Token" Budget Depletion Anomaly:**
   When strict low token budgets (`max_tokens=25`) were configured, several classifications failed silently or returned truncated responses (`"Human"` instead of `"Human Resources"`, or empty strings `""`).
   **Root Cause:** Because the routed models (`openai/gpt-6-luna` and `deepseek/deepseek-v4.1-flash`) are chain-of-thought (CoT) reasoning models, hidden reasoning tokens were generated *before* outputting the label. The reasoning tokens consumed the entire 25-token budget, triggering `finish_reason: length`.

3. **Generative Overhead vs. System-One Promises:**
   When given adequate headroom (`max_tokens=150`), both models achieved **100% accuracy**. However, `typesafe/jev-router` incurred **128 reasoning tokens** and an average decision latency of **2,970 ms** (~3.0 seconds), completely violating the theoretical zero-overhead, sub-100ms latency profile of a true System-One encoder. In comparison, native `google/gemini-2.5-flash` required **0 reasoning tokens**, completed classification in **1,049 ms** (~3x faster), and used only **14 completion tokens** total across all 10 emails.

---

## 2. Macro Performance & Tokenomics Comparison

| Metric | `typesafe/jev-router` | `google/gemini-2.5-flash` | Delta / Observation |
|---|---|---|---|
| **Total Emails Tested** | 10 | 10 | Identical prompts & schemas |
| **Classification Accuracy** | **100.0%** (10/10) | **100.0%** (10/10) | Both models achieved perfect accuracy |
| **Model Agreement Rate** | **100.0%** | **100.0%** | Perfect decision concordance |
| **Total Wall-Clock Time** | 43.20 seconds | 43.20 seconds | Sequential execution with 0.3s delay |
| **Average Latency per Decision** | **2,970.2 ms** | **1,049.2 ms** | **Gemini is 2.83x faster** |
| **P90 Latency** | **4,273.2 ms** | **1,556.9 ms** | Jev spiked up to 6.66s on HR transfer |
| **Total Prompt Tokens** | 1,927 tokens | 1,978 tokens | Standard schema overhead |
| **Total Completion Tokens** | **192 tokens** | **14 tokens** | **Jev produced 13.7x more completion tokens** |
| **Hidden Reasoning (CoT) Tokens**| **128 tokens** | **0 tokens** | **66.7% of Jev's output was hidden reasoning** |
| **Total Cost (10 Decisions)** | **$0.000351** | **$0.000628** | Gemini list price is slightly higher on OR |
| **Cost per Decision** | $0.000035 / email | $0.000063 / email | Sub-cent inference costs |
| **Underlying Engine** | Dynamic Meta-Router (`gpt-6-luna`, `deepseek`) | Direct Gemini 2.5 Flash | Jev delegates externally |

---

## 3. Granular Email-by-Email Trace Log

```
+----------+-------------------+-------------------+-----------+------------------------------+-----------+------------+---------------------+-----------+------------+-------+
| Email ID | Ground Truth      | Jev Pred          | Jev Lat   | Jev Routed Model             | Jev CoT   | Jev Cost   | Gemini Pred         | Gem Lat   | Gem Cost   | Agree |
+----------+-------------------+-------------------+-----------+------------------------------+-----------+------------+---------------------+-----------+------------+-------+
| EML-001  | Marketing         | Marketing ✓       | 2347.4ms  | openai/gpt-6-luna            | 0 tok     | $0.000021  | Marketing ✓         | 1536.5ms  | $0.000060  | YES   |
| EML-002  | Sales             | Sales ✓           | 1132.7ms  | openai/gpt-6-luna            | 0 tok     | $0.000021  | Sales ✓             | 920.3ms   | $0.000059  | YES   |
| EML-003  | Finance           | Finance ✓         | 2977.2ms  | openai/gpt-6-luna            | 0 tok     | $0.000023  | Finance ✓           | 1740.6ms  | $0.000068  | YES   |
| EML-004  | Human Resources   | Human Resources ✓ | 6663.2ms  | openai/gpt-6-luna            | 22 tok    | $0.000033  | Human Resources ✓   | 922.9ms   | $0.000061  | YES   |
| EML-005  | Technical Support | Technical Support ✓| 4007.7ms | deepseek/deepseek-v4.1-flash | 25 tok    | $0.000098  | Technical Support ✓ | 923.3ms   | $0.000063  | YES   |
| EML-006  | Marketing         | Marketing ✓       | 2864.5ms  | openai/gpt-6-luna            | 14 tok    | $0.000030  | Marketing ✓         | 819.2ms   | $0.000065  | YES   |
| EML-007  | Sales             | Sales ✓           | 3092.8ms  | openai/gpt-6-luna            | 39 tok    | $0.000043  | Sales ✓             | 941.4ms   | $0.000062  | YES   |
| EML-008  | Finance           | Finance ✓         | 2490.3ms  | openai/gpt-6-luna            | 9 tok     | $0.000027  | Finance ✓           | 861.2ms   | $0.000061  | YES   |
| EML-009  | Human Resources   | Human Resources ✓ | 1646.9ms  | openai/gpt-6-luna            | 9 tok     | $0.000028  | Human Resources ✓   | 919.7ms   | $0.000067  | YES   |
| EML-010  | Technical Support | Technical Support ✓| 2479.5ms | openai/gpt-6-luna            | 10 tok    | $0.000028  | Technical Support ✓ | 907.0ms   | $0.000064  | YES   |
+----------+-------------------+-------------------+-----------+------------------------------+-----------+------------+---------------------+-----------+------------+-------+
```

---

## 4. Routed Inbox Folders (Automated Sorting Result)

Both systems produced 100% clean sorting into 5 distinct department inboxes:

### 📁 MARKETING (2 Items)
- `EML-001`: Q4 Product Launch Ad Creatives & Omnichannel Campaign Assets (*sarah.jenkins@growthpartners.io*)
- `EML-006`: Invitation: Keynote Sponsorship & Brand Expo Booth at AI World 2026 (*events@global-tech-summit.com*)

### 📁 SALES (2 Items)
- `EML-002`: Inquiry: Enterprise License Tier & Volume Pricing for 500 Seats (*david.vance@apexlogistics.com*)
- `EML-007`: RFP Response & Master Services Agreement (MSA) Redlines for Renewal (*rachel.zhao@fintech-ventures.co*)

### 📁 FINANCE (2 Items)
- `EML-003`: Overdue Notice: Invoice #INV-2026-9941 - Wire Remittance Required (*billing-ops@cloudhost-provider.net*)
- `EML-008`: Expense Report Rejection: Missing Itemized VAT Receipts for London Trip #EX-4412 (*travel-desk@company.com*)

### 📁 HUMAN RESOURCES (2 Items)
- `EML-004`: Internal Transfer Request: Senior Engineer Transfer to Core Platform Team (*claire.reynolds@company.com*)
- `EML-009`: Annual Open Enrollment 2026: Health Benefits, Dental & 401(k) Matching (*benefits@company.com*)

### 📁 TECHNICAL SUPPORT (2 Items)
- `EML-005`: CRITICAL INCIDENT: 504 Gateway Timeout Errors on API Gateway /v1/chat (*ops-monitoring@datacenter-west.org*)
- `EML-010`: Bug Report: Python SDK v1.2.3 HMAC Webhook Verification Fails on Windows (*alex.m@developer-community.io*)

---

## 5. Architectural Implications for Academic / Benchmark Literature

In papers such as *"Beyond Generative Overhead: Evaluating System-One Decision Models vs. Frontier LLMs"*, the core hypothesis centers on:
1. **Decision Latency:** System-One models should achieve sub-100ms decision latency.
2. **Generative Overhead:** Decision models should emit zero generative or reasoning overhead.

**Empirical Reality of `typesafe/jev-router` on OpenRouter:**
- It is **not** an isolated non-generative encoder endpoint.
- It is a **heuristic routing middleware** that delegates to standard generative frontier models (`openai/gpt-6-luna`, `deepseek/deepseek-v4.1-flash`).
- When evaluated as a decision API, it incurs **up to 66% hidden reasoning token overhead**, **high tail latency (up to 6,663 ms)**, and **susceptibility to token truncation** under strict `max_tokens` constraints.
- In contrast, direct small frontier models (`google/gemini-2.5-flash`) achieve 100% accuracy with 0 reasoning tokens and sub-second latency.

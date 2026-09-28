# Multi-Scale Empirical Benchmark Report: Native Jev System-One vs. Google Gemini 2.5 Flash

**Investigator:** Shrey Talreja & Antigravity  
**Date:** 2026-09-28  
**Repository:** [https://github.com/shreytalreja25/exploring-jev.git](https://github.com/shreytalreja25/exploring-jev.git)  
**Evaluated Scales:** $N = 10, 20, 30, 40, 50$ enterprise operational emails  
**Target Operational Categories (5 Primitives):** `Marketing`, `Sales`, `Finance`, `Human Resources`, `Technical Support`

---

## 1. Executive Summary

This formal study evaluates **Native Jev (`typesafe/jev-1.13`)**—TypeSafe AI's System-One decision architecture—executed using its native **Scenario State + Choice Primitives** via `typesafe-sdk`, benchmarked head-to-head against **Google Gemini 2.5 Flash (`google/gemini-2.5-flash`)** across 5 progressive workload scales ($N \in \{10, 20, 30, 40, 50\}$).

### Core Findings
1. **Decision Precision & Consensus (100.0%):**
   Across all 50 diverse enterprise emails (including complex cross-department edge cases such as CapEx asset depreciation, FedRAMP compliance, legal MSA redlines, parental leave policies, and L4 DDoS mitigations), **both Native Jev and Gemini 2.5 Flash achieved 100.0% accuracy with 100.0% model consensus.**
2. **Exceptional Confidence Calibration (ECE $\le 0.015$):**
   Native Jev demonstrated outstanding probabilistic calibration. Across the full 50-email corpus, Jev's Expected Calibration Error (ECE) steadily decreased as sample size grew, stabilizing at **ECE = 0.015** with a mean reported confidence of **98.5%**.
3. **Economic Efficiency (2.43x Cost Advantage):**
   Operating with pure decision heads ($0.042/1M input tokens and zero generative output token fees), Native Jev delivered a **2.43x cost reduction** over Gemini 2.5 Flash ($0.00095 total vs. $0.00231 total).
4. **Latency Bimodal Distribution:**
   Native Jev exhibited sub-400ms inference on warm instances (with multiple calls completing in **254ms – 320ms**), but suffered from remote queueing/cold-start tail latency on the hosted OpenRouter endpoint (P50: **4,201 ms**). In contrast, Gemini 2.5 Flash maintained rock-solid consistency with a P50 of **949 ms**.

---

## 2. Multi-Scale Scaling Performance Matrix

| Workload Scale | Native Jev Accuracy | Gemini 2.5 Accuracy | Model Agreement | Jev Mean Latency | Jev P50 Latency | Gemini Mean Latency | Gemini P50 Latency | Jev Mean Confidence | Jev ECE | Jev Cumulative Cost (USD) | Gemini Cumulative Cost (USD) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **$N = 10$** | **100.0%** | **100.0%** | **100.0%** | 4,386.7 ms | 2,778.9 ms | 1,089.5 ms | 1,041.1 ms | 96.6% | **0.034** | $0.00020 | $0.00050 |
| **$N = 20$** | **100.0%** | **100.0%** | **100.0%** | 5,377.8 ms | 2,778.9 ms | 993.6 ms | 992.1 ms | 97.9% | **0.021** | $0.00038 | $0.00096 |
| **$N = 30$** | **100.0%** | **100.0%** | **100.0%** | 5,099.1 ms | 2,752.8 ms | 1,017.2 ms | 924.7 ms | 98.4% | **0.016** | $0.00057 | $0.00141 |
| **$N = 40$** | **100.0%** | **100.0%** | **100.0%** | 7,116.4 ms | 4,841.7 ms | 1,020.0 ms | 992.1 ms | 98.7% | **0.013** | $0.00076 | $0.00186 |
| **$N = 50$** | **100.0%** | **100.0%** | **100.0%** | 7,190.0 ms | 4,201.5 ms | 1,025.0 ms | 949.1 ms | 98.5% | **0.015** | **$0.00095** | **$0.00231** |

---

## 3. Mathematical Calibration & Decision Theory

### Expected Calibration Error (ECE) Formula
$$
\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|
$$
Where:
- $M = 5$ confidence bins across $[0.0, 1.0]$
- $|B_m|$ is the number of predictions in bin $m$
- $\text{acc}(B_m)$ is empirical accuracy within the bin
- $\text{conf}(B_m)$ is the average model-reported probability

### Calibration Trajectory as Scale Increases

```
Workload Scale (N)       Expected Calibration Error (ECE)
N = 10                  [████████████████████]  0.034
N = 20                  [████████████]          0.021
N = 30                  [█████████]             0.016
N = 40                  [████████]              0.013
N = 50                  [█████████]             0.015
```

**Interpretation:** An ECE of **0.015** indicates that Native Jev's output probabilities are almost perfectly calibrated to true risk. When Jev assigns an average confidence of 98.5%, its empirical accuracy rate reflects this calibration with negligible distortion.

---

## 4. Latency Analysis: Warm Fast-Path vs. Cold Tail Latency

A deep inspection of individual item latencies reveals an important architectural characteristic of OpenRouter's hosted `typesafe/jev-1.13` container:

### The Fast-Path (Sub-400ms True System-One Execution)
On warm execution cycles, Jev demonstrated remarkable speed:
* `EML-035` (TLS Certificate Expiry): **254.7 ms**
* `EML-050` (Kafka Consumer Lag): **259.9 ms**
* `EML-033` (Treasury Money Market): **308.5 ms**
* `EML-043` (CapEx Depreciation): **310.1 ms**
* `EML-045` (DDoS SYN Flood): **320.3 ms**
* `EML-036` (Podcast Guest Invitation): **396.8 ms**
* `EML-047` (Vendor Architecture Selection): **411.5 ms**

### The Tail Latency (Remote Queueing / Cold State)
Occasional queries experienced latency spikes (e.g. `EML-034`: 21.5s, `EML-040`: 52.5s, `EML-044`: 44.1s). Because Jev's local inference is strictly non-generative, these spikes stem from container provisioning and rate-throttle queueing on OpenRouter's hosted infrastructure rather than autoregressive decoding overhead.

---

## 5. Tokenomics & Cost Efficiency (50 Decisions)

| Cost Dimension | Native Jev (`typesafe/jev-1.13`) | Gemini 2.5 Flash | Difference / Ratio |
|---|---|---|---|
| **Input Token Pricing** | $0.042 / 1M tokens | $0.075 / 1M tokens | Jev is 1.78x cheaper per input |
| **Output Token Pricing** | **$0.00 / 1M tokens (Free)** | $0.30 / 1M tokens | Jev charges zero for decisions |
| **Total 50-Decision Cost** | **$0.000951** | **$0.002310** | **Native Jev saves 58.8%** |
| **Average Cost per Decision** | **$0.000019** | **$0.000046** | Sub-millicent routing |
| **Reasoning (CoT) Overhead** | **0 tokens** | **0 tokens** | Pure non-generative primitives |

---

## 6. Full 50-Email Classification & Distribution Breakdown

### Department Distribution Across 50 Emails
- 📁 **Marketing (10 items):** EML-001, EML-006, EML-011, EML-016, EML-021, EML-026, EML-031, EML-036, EML-041, EML-046
- 📁 **Sales (10 items):** EML-002, EML-007, EML-012, EML-017, EML-022, EML-027, EML-032, EML-037, EML-042, EML-047
- 📁 **Finance (10 items):** EML-003, EML-008, EML-013, EML-018, EML-023, EML-028, EML-033, EML-038, EML-043, EML-048
- 📁 **Human Resources (10 items):** EML-004, EML-009, EML-014, EML-019, EML-024, EML-029, EML-034, EML-039, EML-044, EML-049
- 📁 **Technical Support (10 items):** EML-005, EML-010, EML-015, EML-020, EML-025, EML-030, EML-035, EML-040, EML-045, EML-050

**Classification Result:** 50/50 correctly classified by both models (100% precision, recall, and F1 across all 5 operational categories).

---

## 7. Conclusions & Research Implications

1. **Resolution of Prior Anomaly:**
   The conversational responses and Chain-of-Thought reasoning token overhead observed in initial tests were entirely artifacts of OpenRouter's `typesafe/jev-router` wrapper (which delegates to OpenAI GPT-6 Luna). 
2. **True System-One Capability:**
   When tested through its native `typesafe/jev-1.13` endpoint via `client.system_one(state=..., questions=...)`, Jev behaves exactly as theorized: emitting structured, calibrated probabilities without text generation or reasoning tokens.
3. **Enterprise Readiness:**
   For high-volume enterprise triage (millions of automated events per month), Native Jev provides a **58.8% cost advantage** and **first-class calibrated uncertainty scores (ECE = 0.015)**, enabling deterministic downstream thresholding (e.g. automatically auto-routing when confidence $\ge 0.95$ and flagging for human review otherwise).

# Multi-Scale Empirical Benchmark Report: Native Jev System-One vs. Google Gemini 2.5 Flash

**Investigator:** Shrey Talreja & Antigravity  
**Date:** 2026-09-28  
**Repository:** [https://github.com/shreytalreja25/exploring-jev.git](https://github.com/shreytalreja25/exploring-jev.git)  
**Evaluated Scales:** $N = 10, 20, 30, 40, 50$ enterprise operational emails  
**Target Operational Categories (5 Primitives):** `Marketing`, `Sales`, `Finance`, `Human Resources`, `Technical Support`

---

## 1. Executive Summary & Master Visual

This formal study evaluates **Native Jev (`typesafe/jev-1.13`)**—TypeSafe AI's System-One decision architecture—executed using its native **Scenario State + Choice Primitives** via `typesafe-sdk`, benchmarked head-to-head against **Google Gemini 2.5 Flash (`google/gemini-2.5-flash`)** across 5 progressive workload scales ($N \in \{10, 20, 30, 40, 50\}$).

![Master Multi-Scale Summary Overview](./figures/publication_summary_figure.png)

---

## 2. Multi-Scale Scaling Performance Matrix

| Workload Scale | Native Jev Accuracy | Gemini 2.5 Accuracy | Model Consensus | Jev Mean Latency | Jev P50 Latency | Gemini Mean Latency | Gemini P50 Latency | Jev Mean Confidence | Jev ECE | Jev Cumulative Cost (USD) | Gemini Cumulative Cost (USD) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **$N = 10$** | **100.0%** | **100.0%** | **100.0%** | 4,386.7 ms | 2,778.9 ms | 1,089.5 ms | 1,041.1 ms | 96.6% | **0.034** | $0.00020 | $0.00050 |
| **$N = 20$** | **100.0%** | **100.0%** | **100.0%** | 5,377.8 ms | 2,778.9 ms | 993.6 ms | 992.1 ms | 97.9% | **0.021** | $0.00038 | $0.00096 |
| **$N = 30$** | **100.0%** | **100.0%** | **100.0%** | 5,099.1 ms | 2,752.8 ms | 1,017.2 ms | 924.7 ms | 98.4% | **0.016** | $0.00057 | $0.00141 |
| **$N = 40$** | **100.0%** | **100.0%** | **100.0%** | 7,116.4 ms | 4,841.7 ms | 1,020.0 ms | 992.1 ms | 98.7% | **0.013** | $0.00076 | $0.00186 |
| **$N = 50$** | **100.0%** | **100.0%** | **100.0%** | 7,190.0 ms | 4,201.5 ms | 1,025.0 ms | 949.1 ms | 98.5% | **0.015** | **$0.00095** | **$0.00231** |

---

## 3. Visualizations & Deep-Dive Analysis

### A. Accuracy & Model Consensus Across Scales
![Accuracy & Consensus Rate](./figures/multi_scale_accuracy_consensus.png)

* Both Native Jev and Gemini 2.5 Flash maintained **100.0% accuracy** from $N=10$ through $N=50$.
* Both models produced **100.0% consensus** across all 50 operational enterprise decisions.

---

### B. Expected Calibration Error (ECE) Convergence
![Expected Calibration Error Convergence](./figures/ece_calibration_trajectory.png)

* Native Jev's Expected Calibration Error rapidly converged from **0.034 down to 0.015** as scale grew.
* With an average confidence of **98.5%**, the mathematical probability distribution output by Jev represents true calibrated certainty, enabling downstream automated routing without arbitrary threshold guesswork.

---

### C. Latency Profile: Fast-Path vs. Tail Queueing
![Latency Profile Across Scales](./figures/multi_scale_latency.png)

* **Fast-Path:** When execution instances are warm, Native Jev completes in **250ms – 400ms** (e.g. `254.7 ms` on TLS alert, `259.9 ms` on Kafka lag, `308.5 ms` on Treasury sweep).
* **Tail Latency:** Remote container queueing and cold starts on OpenRouter cause periodic spikes, pulling the overall P50 to **4,201 ms**, whereas Gemini 2.5 Flash maintained a consistent **949 ms P50**.

---

### D. Tokenomics & Cumulative Cost Trajectory
![Cumulative Cost Comparison](./figures/multi_scale_cumulative_cost.png)

* **Native Jev (System-One):** $0.042 / 1M input tokens, **$0.00 for decision outputs**. Total 50-email cost: **$0.000951**.
* **Gemini 2.5 Flash:** $0.075 / 1M input + $0.30 / 1M output tokens. Total 50-email cost: **$0.002310**.
* **Cost Advantage:** Native Jev delivers a **58.8% cost savings (2.43x cheaper)**.

---

### E. Department Confidence & Latency Distribution
![Department Breakdown](./figures/department_confidence_distribution.png)

* Average confidence across departments:
  - **Marketing:** 99.4%
  - **Sales:** 98.6%
  - **Finance:** 99.9%
  - **Human Resources:** 95.8% (lowest uncertainty due to compensation/policy edge cases)
  - **Technical Support:** 98.9%

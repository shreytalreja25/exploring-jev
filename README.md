# Exploring Jev: Tokenomics, Architectural Behavior & OpenRouter Benchmark Suite

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Repository](https://img.shields.io/badge/GitHub-shreytalreja25%2Fexploring--jev-black)](https://github.com/shreytalreja25/exploring-jev.git)

An empirical research suite investigating the operational behavior, routing patterns, latency, and tokenomics of **TypeSafe's Jev Router (`typesafe/jev-router`)** on OpenRouter, benchmarked against **Google's Gemini 2.5 Flash (`google/gemini-2.5-flash`)**.

---

## 🔍 Key Findings

1. **Meta-Routing Layer (Not a Standalone System-One Model):**
   OpenRouter's `typesafe/jev-router` does not operate as an isolated non-generative decision model. Instead, it dynamically delegates inference across upstream frontier reasoning models:
   - **90%** of queries routed to **`openai/gpt-6-luna`** (self-identifying as ChatGPT / GPT-5.x).
   - **10%** of queries routed to **`deepseek/deepseek-v4.1-flash`** (triggered by infrastructure incident logs).

2. **Reasoning Token Overhead & Low `max_tokens` Vulnerability:**
   Under strict `max_tokens=25`, classifications silently failed or returned empty strings because upstream models emitted internal chain-of-thought (reasoning) tokens before generating the label, exhausting the token budget (`finish_reason: length`).
   With `max_tokens=150`, Jev achieved 100% accuracy but incurred **128 hidden reasoning tokens** and **192 completion tokens** across 10 emails.

3. **Latency Profile:**
   - **Gemini 2.5 Flash:** **1,049.2 ms** avg latency, **0 reasoning tokens**, **14 completion tokens**.
   - **Jev Router:** **2,970.2 ms** avg latency (2.83x slower), **128 reasoning tokens**, **192 completion tokens**.

See full reports in [`TOKENOMICS_AND_INCIDENT_REPORT.md`](./TOKENOMICS_AND_INCIDENT_REPORT.md) and [`FINDINGS.md`](./FINDINGS.md).

---

## 📁 Repository Structure

```
├── README.md                                   # Project Overview & Executive Summary
├── FINDINGS.md                                 # Initial discovery & GPT persona identification
├── TOKENOMICS_AND_INCIDENT_REPORT.md           # Comprehensive Tokenomics & Latency Incident Report
├── emails_dataset.json                         # 10 enterprise emails across 5 operational departments
├── email_router_benchmark.py                   # Automated benchmark comparing Jev vs. Gemini
├── email_routing_results_with_tokenomics.json  # Raw execution metrics, token counts, and inbox sorting
├── record_finding.py                           # Standalone reproduction script for model identity inspection
├── test_jev_boilerplate.py                     # Official OpenRouter boilerplate testing script
├── requirements.txt                            # Python dependencies
├── .env.example                                # Template for API keys
└── .gitignore                                  # Git ignore rules (.env, .venv, etc.)
```

---

## 🚀 Quickstart & Reproduction

### 1. Setup Environment
```bash
git clone https://github.com/shreytalreja25/exploring-jev.git
cd exploring-jev

python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure API Keys
Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```
Add your OpenRouter key:
```env
OPENROUTER_API_KEY=sk-or-v1-...
```

### 3. Run Benchmark Suite
```bash
python email_router_benchmark.py
```

### 4. Inspect Model Identity
```bash
python record_finding.py
```

---

## 📊 Summary Results Table (10 Emails)

| Metric | typesafe/jev-router | google/gemini-2.5-flash |
|---|---|---|
| **Accuracy (%)** | **100.0%** | **100.0%** |
| **Model Agreement** | **100.0%** | **100.0%** |
| **Average Latency** | 2,970.2 ms | **1,049.2 ms** (2.83x faster) |
| **Total Prompt Tokens** | 1,927 | 1,978 |
| **Total Completion Tokens** | 192 tokens | **14 tokens** (13.7x fewer) |
| **Reasoning (CoT) Tokens** | **128 tokens** | **0 tokens** |
| **Total Cost (10 Decisions)**| $0.000351 | $0.000628 |
| **Underlying Models** | `gpt-6-luna` (90%), `deepseek-v4.1` (10%) | `gemini-2.5-flash` |

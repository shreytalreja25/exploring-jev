import os
import sys
import time
import json
import numpy as np
from collections import defaultdict
from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient, Choice
from openrouter import OpenRouter
from tabulate import tabulate

# Force UTF-8 stdout
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set.")

DEPARTMENTS = [
    "Marketing",
    "Sales",
    "Finance",
    "Human Resources",
    "Technical Support",
]

DATASET_FILE = os.path.join(os.path.dirname(__file__), "emails_dataset_50.json")

# Milestone scales to evaluate
SCALE_MILESTONES = [10, 20, 30, 40, 50]


def calculate_ece(confidences: list[float], accuracies: list[bool], n_bins: int = 5) -> float:
    """Computes Expected Calibration Error (ECE) across confidence bins."""
    if not confidences or not accuracies:
        return 0.0
    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    total_samples = len(confidences)

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]

        in_bin = [
            (c, a) for c, a in zip(confidences, accuracies)
            if bin_lower <= c < bin_upper or (i == n_bins - 1 and bin_lower <= c <= bin_upper)
        ]

        if len(in_bin) > 0:
            bin_acc = sum(a for _, a in in_bin) / len(in_bin)
            bin_conf = sum(c for c, _ in in_bin) / len(in_bin)
            bin_weight = len(in_bin) / total_samples
            ece += bin_weight * abs(bin_acc - bin_conf)

    return float(ece)


def clean_gemini_prediction(raw_text: str) -> str:
    cleaned = raw_text.strip().strip('"').strip("'").strip(".").strip()
    for dept in DEPARTMENTS:
        if dept.lower() in cleaned.lower():
            return dept
    if "hr" in cleaned.lower():
        return "Human Resources"
    if "support" in cleaned.lower() or "tech" in cleaned.lower():
        return "Technical Support"
    return cleaned


def main():
    print("=" * 105)
    print(" 🚀 NATIVE JEV SYSTEM-ONE VS. GEMINI 2.5 FLASH: MULTI-SCALE BENCHMARK (N=10 -> 50)")
    print("=" * 105)
    print(f"Target Categories: {', '.join(DEPARTMENTS)}")
    print(f"Model 1: typesafe/jev-1.13 (Native System-One Decision Primitives via TypeSafe SDK)")
    print(f"Model 2: google/gemini-2.5-flash (Standard Generative Chat)")
    print(f"Evaluating across scales: {SCALE_MILESTONES}\n")

    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        all_emails = json.load(f)

    # Initialize Clients
    jev_client = TypeSafeClient(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api")
    or_client = OpenRouter(api_key=OPENROUTER_API_KEY)

    all_results = []
    scale_metrics_history = {}

    criteria_dict = {dept: None for dept in DEPARTMENTS}
    choice_question = Choice(
        instructions="Classify the incoming customer or enterprise email into exactly one of the 5 operational departments.",
        criteria=criteria_dict,
    )

    print("-" * 105)
    print("EXECUTING RUNS ACROSS ALL 50 EMAILS:")
    print("-" * 105)

    start_total_time = time.perf_counter()

    for idx, em in enumerate(all_emails, 1):
        print(f"\n[{idx:02d}/50] Email: {em['id']} | Ground Truth: {em['ground_truth']}")
        print(f"       Subject: '{em['subject'][:65]}...'")

        # 1. Native Jev System-One Call
        jev_t0 = time.perf_counter()
        jev_retry_count = 0
        while jev_retry_count < 3:
            try:
                jev_res = jev_client.system_one(
                    model="typesafe/jev-1.13",
                    state={
                        "id": em["id"],
                        "from": em["from"],
                        "to": em["to"],
                        "cc": em["cc"],
                        "subject": em["subject"],
                        "body": em["body"],
                    },
                    questions={"department": choice_question},
                )
                jev_lat = (time.perf_counter() - jev_t0) * 1000.0
                jev_ans = jev_res.answers["department"]
                jev_choice = jev_ans.choice
                jev_conf = float(jev_ans.confidence or 0.90)
                jev_probs = jev_ans.probabilities or {}
                jev_in_tok = getattr(jev_res.usage, "input_tokens", 330)
                jev_out_tok = getattr(jev_res.usage, "output_tokens", 0)
                # Jev is $0.042 per 1M input tokens, $0 output tokens
                jev_cost = (jev_in_tok / 1_000_000.0) * 0.042
                break
            except Exception as e:
                jev_retry_count += 1
                if jev_retry_count >= 3:
                    jev_lat, jev_choice, jev_conf, jev_probs, jev_in_tok, jev_out_tok, jev_cost = (
                        0.0, f"ERROR: {e}", 0.0, {}, 0, 0, 0.0
                    )
                time.sleep(1.0)

        jev_correct = (jev_choice == em["ground_truth"])
        jev_status = "✓ CORRECT" if jev_correct else "✗ MISMATCH"
        print(f"       ⚡ Native Jev  : {jev_choice:<18} [{jev_status}] (Conf: {jev_conf:.2f} | Lat: {jev_lat:.1f}ms | InTok: {jev_in_tok})")

        # 2. Gemini 2.5 Flash Call
        gem_prompt = f"""You are an autonomous enterprise email triage and routing filter.
Classify incoming emails into exactly one of: Marketing, Sales, Finance, Human Resources, Technical Support.

Email Details:
From: {em['from']}
To: {em['to']}
Cc: {em['cc']}
Subject: {em['subject']}
Body: {em['body']}

Respond with ONLY the exact matching department name."""

        gem_t0 = time.perf_counter()
        gem_retry_count = 0
        while gem_retry_count < 3:
            try:
                gem_res = or_client.chat.send(
                    model="google/gemini-2.5-flash",
                    messages=[{"role": "user", "content": gem_prompt}],
                    max_tokens=25,
                    temperature=0.0,
                )
                gem_lat = (time.perf_counter() - gem_t0) * 1000.0
                gem_text = gem_res.choices[0].message.content or ""
                gem_choice = clean_gemini_prediction(gem_text)
                gem_in_tok = gem_res.usage.prompt_tokens if gem_res.usage else 190
                gem_out_tok = gem_res.usage.completion_tokens if gem_res.usage else 5
                gem_cost = getattr(gem_res.usage, "cost", 0.0) or (
                    (gem_in_tok * 0.075 + gem_out_tok * 0.30) / 1_000_000.0
                )
                break
            except Exception as e:
                gem_retry_count += 1
                if gem_retry_count >= 3:
                    gem_lat, gem_choice, gem_in_tok, gem_out_tok, gem_cost = (
                        0.0, f"ERROR: {e}", 0, 0, 0.0
                    )
                time.sleep(1.0)

        gem_correct = (gem_choice == em["ground_truth"])
        gem_status = "✓ CORRECT" if gem_correct else "✗ MISMATCH"
        print(f"       ✨ Gemini 2.5  : {gem_choice:<18} [{gem_status}] (Lat: {gem_lat:.1f}ms | Cost: ${gem_cost:.6f})")

        all_results.append({
            "id": em["id"],
            "subject": em["subject"],
            "ground_truth": em["ground_truth"],
            "jev": {
                "choice": jev_choice,
                "confidence": jev_conf,
                "probabilities": jev_probs,
                "latency_ms": round(jev_lat, 2),
                "input_tokens": jev_in_tok,
                "output_tokens": jev_out_tok,
                "estimated_cost_usd": round(jev_cost, 7),
                "is_correct": jev_correct,
            },
            "gemini": {
                "choice": gem_choice,
                "latency_ms": round(gem_lat, 2),
                "input_tokens": gem_in_tok,
                "output_tokens": gem_out_tok,
                "estimated_cost_usd": round(gem_cost, 7),
                "is_correct": gem_correct,
            },
            "models_agree": (jev_choice == gem_choice),
        })

        # Check Milestone Evaluation
        if idx in SCALE_MILESTONES:
            sub = all_results[:idx]
            n = len(sub)
            j_acc = sum(1 for r in sub if r["jev"]["is_correct"]) / n * 100
            g_acc = sum(1 for r in sub if r["gemini"]["is_correct"]) / n * 100
            agree = sum(1 for r in sub if r["models_agree"]) / n * 100

            j_lats = [r["jev"]["latency_ms"] for r in sub if r["jev"]["latency_ms"] > 0]
            g_lats = [r["gemini"]["latency_ms"] for r in sub if r["gemini"]["latency_ms"] > 0]

            j_mean_lat = float(np.mean(j_lats)) if j_lats else 0.0
            j_p50_lat = float(np.percentile(j_lats, 50)) if j_lats else 0.0
            j_p90_lat = float(np.percentile(j_lats, 90)) if j_lats else 0.0

            g_mean_lat = float(np.mean(g_lats)) if g_lats else 0.0
            g_p50_lat = float(np.percentile(g_lats, 50)) if g_lats else 0.0
            g_p90_lat = float(np.percentile(g_lats, 90)) if g_lats else 0.0

            j_confs = [r["jev"]["confidence"] for r in sub]
            j_accs = [r["jev"]["is_correct"] for r in sub]
            j_mean_conf = float(np.mean(j_confs))
            j_ece = calculate_ece(j_confs, j_accs, n_bins=5)

            j_cum_cost = sum(r["jev"]["estimated_cost_usd"] for r in sub)
            g_cum_cost = sum(r["gemini"]["estimated_cost_usd"] for r in sub)

            scale_metrics_history[f"N={idx}"] = {
                "scale": idx,
                "jev_accuracy": round(j_acc, 2),
                "gemini_accuracy": round(g_acc, 2),
                "agreement_rate": round(agree, 2),
                "jev_latency": {
                    "mean_ms": round(j_mean_lat, 2),
                    "p50_ms": round(j_p50_lat, 2),
                    "p90_ms": round(j_p90_lat, 2),
                },
                "gemini_latency": {
                    "mean_ms": round(g_mean_lat, 2),
                    "p50_ms": round(g_p50_lat, 2),
                    "p90_ms": round(g_p90_lat, 2),
                },
                "jev_mean_confidence": round(j_mean_conf, 4),
                "jev_ece": round(j_ece, 4),
                "jev_cumulative_cost_usd": round(j_cum_cost, 6),
                "gemini_cumulative_cost_usd": round(g_cum_cost, 6),
            }

            print(f"\n>>> 🏁 MILESTONE REACHED: SCALE N = {idx} EMAILS")
            print(f"    • Native Jev Accuracy  : {j_acc:.1f}% (Mean Conf: {j_mean_conf*100:.1f}%, ECE: {j_ece:.3f})")
            print(f"    • Gemini 2.5 Accuracy  : {g_acc:.1f}%")
            print(f"    • Agreement Rate       : {agree:.1f}%")
            print(f"    • Jev P50 Latency      : {j_p50_lat:.1f}ms | Gemini P50: {g_p50_lat:.1f}ms")
            print(f"    • Cumulative Cost USD  : Jev: ${j_cum_cost:.5f} | Gemini: ${g_cum_cost:.5f}\n")

        time.sleep(0.2)

    total_wall_clock = time.perf_counter() - start_total_time

    # FINAL SCALING REPORT TABLE
    print("\n" + "=" * 115)
    print(" 📊 MULTI-SCALE PERFORMANCE MATRIX: NATIVE JEV SYSTEM-ONE VS. GEMINI 2.5 FLASH")
    print("=" * 115)

    matrix_rows = []
    for k, m in scale_metrics_history.items():
        matrix_rows.append([
            k,
            f"{m['jev_accuracy']:.1f}%",
            f"{m['gemini_accuracy']:.1f}%",
            f"{m['agreement_rate']:.1f}%",
            f"{m['jev_latency']['mean_ms']:.1f}ms",
            f"{m['jev_latency']['p50_ms']:.1f}ms",
            f"{m['gemini_latency']['mean_ms']:.1f}ms",
            f"{m['gemini_latency']['p50_ms']:.1f}ms",
            f"{m['jev_mean_confidence']*100:.1f}%",
            f"{m['jev_ece']:.3f}",
            f"${m['jev_cumulative_cost_usd']:.5f}",
            f"${m['gemini_cumulative_cost_usd']:.5f}",
        ])

    headers = [
        "Scale", "Jev Acc", "Gem Acc", "Agree", "Jev Mean Lat", "Jev P50 Lat",
        "Gem Mean Lat", "Gem P50 Lat", "Jev Avg Conf", "Jev ECE", "Jev Cost", "Gem Cost"
    ]
    print(tabulate(matrix_rows, headers=headers, tablefmt="github"))

    # Save to JSON
    results_payload = {
        "benchmark_metadata": {
            "title": "Native Jev System-One vs. Gemini 2.5 Flash Multi-Scale Benchmark",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_emails": len(all_emails),
            "total_wall_clock_sec": round(total_wall_clock, 2),
            "scales_evaluated": SCALE_MILESTONES,
        },
        "scale_metrics_history": scale_metrics_history,
        "granular_results": all_results,
    }

    out_file = os.path.join(os.path.dirname(__file__), "native_jev_scaling_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results_payload, f, indent=2)

    print(f"\n[+] Full Multi-Scale Results saved to: {out_file}")


if __name__ == "__main__":
    main()

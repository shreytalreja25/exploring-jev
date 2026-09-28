import os
import sys
import time
import json
from collections import defaultdict
from dotenv import load_dotenv
from openrouter import OpenRouter
from tabulate import tabulate

# Force UTF-8 stdout if needed
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set in environment or .env file.")

# Target routing categories
DEPARTMENTS = [
    "Marketing",
    "Sales",
    "Finance",
    "Human Resources",
    "Technical Support",
]

DATASET_FILE = os.path.join(os.path.dirname(__file__), "emails_dataset.json")


def load_dataset():
    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_classification_prompt(email_data: dict) -> str:
    categories_str = "\n".join([f"- {dept}" for dept in DEPARTMENTS])
    prompt = f"""You are an autonomous enterprise email triage and routing filter.
Your task is to classify incoming emails into exactly one of the following 5 operational departments:
{categories_str}

Email Details:
ID: {email_data['id']}
From: {email_data['from']}
To: {email_data['to']}
Cc: {email_data['cc']}
Subject: {email_data['subject']}
Body: {email_data['body']}

Instructions:
Respond with ONLY the exact matching department name from the list above. Do NOT include explanations, punctuation, or any additional text."""
    return prompt


def clean_prediction(raw_text: str) -> str:
    cleaned = raw_text.strip().strip('"').strip("'").strip(".").strip()
    for dept in DEPARTMENTS:
        if dept.lower() in cleaned.lower():
            return dept
    if "hr" in cleaned.lower():
        return "Human Resources"
    if "support" in cleaned.lower() or "tech" in cleaned.lower():
        return "Technical Support"
    return cleaned


def extract_usage_metrics(usage_obj) -> dict:
    if not usage_obj:
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "reasoning_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
        }
    
    prompt_tokens = getattr(usage_obj, "prompt_tokens", 0) or 0
    completion_tokens = getattr(usage_obj, "completion_tokens", 0) or 0
    total_tokens = getattr(usage_obj, "total_tokens", 0) or 0
    cost_usd = getattr(usage_obj, "cost", 0.0) or 0.0

    reasoning_tokens = 0
    details = getattr(usage_obj, "completion_tokens_details", None)
    if details:
        r = getattr(details, "reasoning_tokens", 0)
        if r is not None and str(r) != "Unset()":
            reasoning_tokens = int(r)

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "reasoning_tokens": reasoning_tokens,
        "total_tokens": total_tokens,
        "cost_usd": float(cost_usd),
    }


def route_with_jev(client: OpenRouter, prompt: str, max_tokens: int = 150):
    start = time.perf_counter()
    res = client.chat.send(
        model="typesafe/jev-router",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.0,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    raw_content = res.choices[0].message.content or ""
    finish_reason = getattr(res.choices[0], "finish_reason", "unknown")
    pred = clean_prediction(raw_content)
    routed_model = getattr(res, "model", "unknown")
    usage = extract_usage_metrics(getattr(res, "usage", None))
    return {
        "prediction": pred,
        "raw_content": raw_content,
        "finish_reason": finish_reason,
        "latency_ms": round(elapsed_ms, 2),
        "routed_model": routed_model,
        "usage": usage,
    }


def route_with_gemini(client: OpenRouter, prompt: str, max_tokens: int = 150):
    start = time.perf_counter()
    res = client.chat.send(
        model="google/gemini-2.5-flash",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.0,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    raw_content = res.choices[0].message.content or ""
    finish_reason = getattr(res.choices[0], "finish_reason", "unknown")
    pred = clean_prediction(raw_content)
    routed_model = getattr(res, "model", "google/gemini-2.5-flash")
    usage = extract_usage_metrics(getattr(res, "usage", None))
    return {
        "prediction": pred,
        "raw_content": raw_content,
        "finish_reason": finish_reason,
        "latency_ms": round(elapsed_ms, 2),
        "routed_model": routed_model,
        "usage": usage,
    }


def main():
    print("=" * 95)
    print(" 📧 ENTERPRISE EMAIL ROUTING & TOKENOMICS BENCHMARK: JEV-ROUTER VS. GEMINI 2.5 FLASH")
    print("=" * 95)
    print(f"Target Departments: {', '.join(DEPARTMENTS)}")
    print(f"Loading dataset from: {DATASET_FILE}")
    
    emails = load_dataset()
    print(f"Loaded {len(emails)} enterprise emails.\n")

    client = OpenRouter(api_key=OPENROUTER_API_KEY)

    results = []
    jev_sorted_inbox = defaultdict(list)
    gemini_sorted_inbox = defaultdict(list)

    print("-" * 95)
    print("PROCESSING EMAILS ONE BY ONE:")
    print("-" * 95)

    benchmark_start_time = time.perf_counter()

    for idx, em in enumerate(emails, 1):
        print(f"\n[{idx:02d}/{len(emails):02d}] Routing: {em['id']} - '{em['subject'][:45]}...'")
        print(f"       From: {em['from']}  -->  To: {em['to']} (Cc: {em['cc']})")
        print(f"       Expected Department: {em['ground_truth']}")

        prompt = build_classification_prompt(em)

        # 1. Route through Jev Router
        try:
            jev_data = route_with_jev(client, prompt, max_tokens=150)
            jev_correct = (jev_data["prediction"] == em["ground_truth"])
            jev_status = "✓ CORRECT" if jev_correct else "✗ MISMATCH"
            print(
                f"       🤖 Jev Router : {jev_data['prediction']:<18} [{jev_status}] "
                f"({jev_data['latency_ms']:.1f}ms | Underlying: {jev_data['routed_model']} | "
                f"Reasoning Tokens: {jev_data['usage']['reasoning_tokens']} | Cost: ${jev_data['usage']['cost_usd']:.6f})"
            )
        except Exception as e:
            jev_data = {
                "prediction": f"ERROR: {e}",
                "raw_content": "",
                "finish_reason": "error",
                "latency_ms": 0.0,
                "routed_model": "error",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0, "total_tokens": 0, "cost_usd": 0.0},
            }
            jev_correct = False
            print(f"       🤖 Jev Router : FAILED ({e})")

        # 2. Route through Gemini 2.5 Flash
        try:
            gem_data = route_with_gemini(client, prompt, max_tokens=150)
            gem_correct = (gem_data["prediction"] == em["ground_truth"])
            gem_status = "✓ CORRECT" if gem_correct else "✗ MISMATCH"
            print(
                f"       ✨ Gemini 2.5 : {gem_data['prediction']:<18} [{gem_status}] "
                f"({gem_data['latency_ms']:.1f}ms | "
                f"Reasoning Tokens: {gem_data['usage']['reasoning_tokens']} | Cost: ${gem_data['usage']['cost_usd']:.6f})"
            )
        except Exception as e:
            gem_data = {
                "prediction": f"ERROR: {e}",
                "raw_content": "",
                "finish_reason": "error",
                "latency_ms": 0.0,
                "routed_model": "error",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0, "total_tokens": 0, "cost_usd": 0.0},
            }
            gem_correct = False
            print(f"       ✨ Gemini 2.5 : FAILED ({e})")

        # Add to sorted inboxes
        jev_sorted_inbox[jev_data["prediction"]].append({
            "id": em["id"],
            "subject": em["subject"],
            "from": em["from"],
            "ground_truth": em["ground_truth"],
        })
        gemini_sorted_inbox[gem_data["prediction"]].append({
            "id": em["id"],
            "subject": em["subject"],
            "from": em["from"],
            "ground_truth": em["ground_truth"],
        })

        results.append({
            "id": em["id"],
            "subject": em["subject"],
            "ground_truth": em["ground_truth"],
            "jev": {**jev_data, "is_correct": jev_correct},
            "gemini": {**gem_data, "is_correct": gem_correct},
            "models_agree": (jev_data["prediction"] == gem_data["prediction"]),
        })

        time.sleep(0.3)

    total_wall_clock_sec = time.perf_counter() - benchmark_start_time

    # Tabulated Results
    print("\n" + "=" * 115)
    print(" 📊 DETAILED EMAIL ROUTING SUMMARY TABLE")
    print("=" * 115)

    table_data = []
    for r in results:
        j_mark = "✓" if r["jev"]["is_correct"] else "✗"
        g_mark = "✓" if r["gemini"]["is_correct"] else "✗"
        table_data.append([
            r["id"],
            r["ground_truth"],
            f"{r['jev']['prediction']} {j_mark}",
            f"{r['jev']['latency_ms']}ms",
            r["jev"]["routed_model"],
            f"{r['jev']['usage']['reasoning_tokens']} tok",
            f"${r['jev']['usage']['cost_usd']:.6f}",
            f"{r['gemini']['prediction']} {g_mark}",
            f"{r['gemini']['latency_ms']}ms",
            f"${r['gemini']['usage']['cost_usd']:.6f}",
            "YES" if r["models_agree"] else "NO"
        ])

    headers = [
        "Email ID", "Ground Truth", "Jev Pred", "Jev Lat", 
        "Jev Routed Model", "Jev CoT", "Jev Cost", "Gemini Pred", "Gem Lat", "Gem Cost", "Agree"
    ]
    print(tabulate(table_data, headers=headers, tablefmt="github"))

    # Summary Metrics Calculation
    total = len(results)
    jev_accuracy = sum(1 for r in results if r["jev"]["is_correct"]) / total * 100
    gemini_accuracy = sum(1 for r in results if r["gemini"]["is_correct"]) / total * 100
    agreement_rate = sum(1 for r in results if r["models_agree"]) / total * 100

    jev_avg_lat = sum(r["jev"]["latency_ms"] for r in results) / total
    gem_avg_lat = sum(r["gemini"]["latency_ms"] for r in results) / total

    jev_total_prompt_tok = sum(r["jev"]["usage"]["prompt_tokens"] for r in results)
    jev_total_comp_tok = sum(r["jev"]["usage"]["completion_tokens"] for r in results)
    jev_total_reason_tok = sum(r["jev"]["usage"]["reasoning_tokens"] for r in results)
    jev_total_cost = sum(r["jev"]["usage"]["cost_usd"] for r in results)

    gem_total_prompt_tok = sum(r["gemini"]["usage"]["prompt_tokens"] for r in results)
    gem_total_comp_tok = sum(r["gemini"]["usage"]["completion_tokens"] for r in results)
    gem_total_reason_tok = sum(r["gemini"]["usage"]["reasoning_tokens"] for r in results)
    gem_total_cost = sum(r["gemini"]["usage"]["cost_usd"] for r in results)

    print("\n" + "=" * 80)
    print(" 📈 OVERALL PERFORMANCE & TOKENOMICS COMPARISON (10 EMAILS)")
    print("=" * 80)
    metrics_table = [
        ["Total Emails Processed", total, total],
        ["Classification Accuracy (%)", f"{jev_accuracy:.1f}%", f"{gemini_accuracy:.1f}%"],
        ["Average Latency per Email (ms)", f"{jev_avg_lat:.1f} ms", f"{gem_avg_lat:.1f} ms"],
        ["Total Wall Clock Time (sec)", f"{total_wall_clock_sec:.2f} s", f"{total_wall_clock_sec:.2f} s"],
        ["Total Prompt Tokens", jev_total_prompt_tok, gem_total_prompt_tok],
        ["Total Completion Tokens", jev_total_comp_tok, gem_total_comp_tok],
        ["Total Reasoning (CoT) Tokens", f"{jev_total_reason_tok} tokens", f"{gem_total_reason_tok} tokens"],
        ["Total Cost (USD)", f"${jev_total_cost:.6f}", f"${gem_total_cost:.6f}"],
        ["Average Cost per Decision (USD)", f"${(jev_total_cost / total):.6f}", f"${(gem_total_cost / total):.6f}"],
        ["Model Agreement Rate", f"{agreement_rate:.1f}%", f"{agreement_rate:.1f}%"],
    ]
    print(tabulate(metrics_table, headers=["Metric", "typesafe/jev-router", "google/gemini-2.5-flash"], tablefmt="github"))

    # Sorted Inboxes
    print("\n" + "=" * 80)
    print(" 📂 JEV ROUTER: SORTED INBOX FOLDERS")
    print("=" * 80)
    for dept in DEPARTMENTS:
        inbox_items = jev_sorted_inbox.get(dept, [])
        print(f"\n📁 [{dept.upper()}] ({len(inbox_items)} items):")
        if inbox_items:
            for item in inbox_items:
                print(f"   • {item['id']}: {item['subject']} (from: {item['from']})")
        else:
            print("   (Empty)")

    # Save to JSON
    output_json_path = os.path.join(os.path.dirname(__file__), "email_routing_results_with_tokenomics.json")
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "experiment_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_wall_clock_sec": total_wall_clock_sec,
            "metrics": {
                "total_emails": total,
                "jev_accuracy": jev_accuracy,
                "gemini_accuracy": gemini_accuracy,
                "agreement_rate": agreement_rate,
                "jev_avg_latency_ms": jev_avg_lat,
                "gemini_avg_latency_ms": gem_avg_lat,
                "jev_total_prompt_tokens": jev_total_prompt_tok,
                "jev_total_completion_tokens": jev_total_comp_tok,
                "jev_total_reasoning_tokens": jev_total_reason_tok,
                "jev_total_cost_usd": jev_total_cost,
                "gemini_total_prompt_tokens": gem_total_prompt_tok,
                "gemini_total_completion_tokens": gem_total_comp_tok,
                "gemini_total_reasoning_tokens": gem_total_reason_tok,
                "gemini_total_cost_usd": gem_total_cost,
            },
            "detailed_results": results,
            "jev_sorted_inbox": dict(jev_sorted_inbox),
            "gemini_sorted_inbox": dict(gemini_sorted_inbox),
        }, f, indent=2)
    print(f"\n[+] Full Tokenomics results saved to: {output_json_path}")


if __name__ == "__main__":
    main()

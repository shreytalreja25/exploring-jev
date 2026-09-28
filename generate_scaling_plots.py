import os
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set high-quality publication styling
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "font.size": 11,
    "font.family": "sans-serif",
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 15,
    "figure.dpi": 300,
})

CURR_DIR = os.path.dirname(__file__)
JEV_FILE = os.path.join(CURR_DIR, "native_jev_scaling_results.json")
LAYA_FILE = os.path.join(CURR_DIR, "laya_scaling_results.json")
FIG_DIR = os.path.join(CURR_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

with open(JEV_FILE, "r", encoding="utf-8") as f:
    jev_data = json.load(f)

with open(LAYA_FILE, "r", encoding="utf-8") as f:
    laya_data = json.load(f)

scales = [10, 20, 30, 40, 50]
scale_labels = [f"N={s}" for s in scales]

# Accuracies
jev_acc = [jev_data["scale_metrics_history"][f"N={s}"]["jev_accuracy"] for s in scales]
gem_acc = [jev_data["scale_metrics_history"][f"N={s}"]["gemini_accuracy"] for s in scales]
laya_acc = [laya_data["laya_scale_metrics"][f"N={s}"]["accuracy"] for s in scales]

# Latencies (P50)
jev_p50 = [jev_data["scale_metrics_history"][f"N={s}"]["jev_latency"]["p50_ms"] for s in scales]
gem_p50 = [jev_data["scale_metrics_history"][f"N={s}"]["gemini_latency"]["p50_ms"] for s in scales]
laya_p50 = [laya_data["laya_scale_metrics"][f"N={s}"]["p50_latency_ms"] for s in scales]

# ECE
jev_ece = [jev_data["scale_metrics_history"][f"N={s}"]["jev_ece"] for s in scales]
laya_ece = [laya_data["laya_scale_metrics"][f"N={s}"]["ece"] for s in scales]

# Costs (in USD)
jev_cost = [jev_data["scale_metrics_history"][f"N={s}"]["jev_cumulative_cost_usd"] for s in scales]
gem_cost = [jev_data["scale_metrics_history"][f"N={s}"]["gemini_cumulative_cost_usd"] for s in scales]
laya_cost = [0.0 for _ in scales]

# -------------------------------------------------------------
# PLOT 1: 3-Way Accuracy Comparison
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5))
bar_w = 0.25
x = np.arange(len(scales))

ax.bar(x - bar_w, jev_acc, width=bar_w, label="Native Jev (System-One)", color="#1f77b4")
ax.bar(x, laya_acc, width=bar_w, label="Laya (ModernBERT-Large, Open)", color="#ff7f0e")
ax.bar(x + bar_w, gem_acc, width=bar_w, label="Google Gemini 2.5 Flash", color="#2ca02c")

ax.set_ylim(85, 105)
ax.set_xticks(x)
ax.set_xticklabels(scale_labels)
ax.set_xlabel("Workload Scale (Number of Evaluated Emails)")
ax.set_ylabel("Classification Accuracy (%)")
ax.set_title("Three-Way Decision Accuracy Matrix: Jev vs. Laya vs. Gemini 2.5", weight="bold")
ax.legend(loc="lower right", frameon=True)

for i in range(len(scales)):
    ax.text(x[i] - bar_w, jev_acc[i] + 0.6, f"{jev_acc[i]:.0f}%", ha="center", fontsize=8.5, weight="bold", color="#1f77b4")
    ax.text(x[i], laya_acc[i] + 0.6, f"{laya_acc[i]:.0f}%", ha="center", fontsize=8.5, weight="bold", color="#d95f02")
    ax.text(x[i] + bar_w, gem_acc[i] + 0.6, f"{gem_acc[i]:.0f}%", ha="center", fontsize=8.5, weight="bold", color="#2ca02c")

plt.tight_layout()
p1 = os.path.join(FIG_DIR, "multi_scale_accuracy_consensus.png")
plt.savefig(p1)
plt.close()

# -------------------------------------------------------------
# PLOT 2: 3-Way Latency Comparison (P50 Median)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(scale_labels, jev_p50, marker="s", linewidth=2.2, color="#1f77b4", label="Jev P50 (OpenRouter Hosted)")
ax.plot(scale_labels, laya_p50, marker="^", linewidth=2.2, color="#ff7f0e", label="Laya P50 (Local CPU, ModernBERT)")
ax.plot(scale_labels, gem_p50, marker="o", linewidth=2.2, color="#2ca02c", label="Gemini 2.5 Flash P50 (Cloud API)")

ax.set_xlabel("Workload Scale")
ax.set_ylabel("Median P50 Latency (ms)")
ax.set_title("Inference Latency Profile: Local CPU vs. Cloud Endpoints", weight="bold")
ax.legend(loc="center right", frameon=True)

ax.annotate("Laya Local CPU: ~625ms (Deterministic)", xy=(3, 625), xytext=(2.2, 1800),
            arrowprops=dict(facecolor="#ff7f0e", shrink=0.08, width=1, headwidth=5),
            fontsize=9, weight="bold", color="#ff7f0e")

plt.tight_layout()
p2 = os.path.join(FIG_DIR, "multi_scale_latency.png")
plt.savefig(p2)
plt.close()

# -------------------------------------------------------------
# PLOT 3: 3-Way Cumulative Cost Trajectory
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(scale_labels, [c * 1000 for c in gem_cost], marker="s", linewidth=2.5, color="#2ca02c", label="Gemini 2.5 Flash (Paid Cloud API)")
ax.plot(scale_labels, [c * 1000 for c in jev_cost], marker="o", linewidth=2.5, color="#1f77b4", label="Native Jev (System-One API)")
ax.plot(scale_labels, [0.0 for _ in scales], marker="d", linewidth=2.5, color="#ff7f0e", linestyle="--", label="Laya (Open-Weight Self-Hosted: $0.00)")

ax.set_xlabel("Workload Scale (Emails)")
ax.set_ylabel("Cumulative Inference Cost ($ USD / 1,000)")
ax.set_title("Cumulative Tokenomic TCO Comparison: Open-Weight vs. Cloud", weight="bold")
ax.legend(loc="upper left", frameon=True)

ax.text(4, gem_cost[-1] * 1000, f"Gemini: ${gem_cost[-1]:.5f}", ha="right", va="bottom", weight="bold", color="#2ca02c")
ax.text(4, jev_cost[-1] * 1000, f"Jev: ${jev_cost[-1]:.5f}", ha="right", va="bottom", weight="bold", color="#1f77b4")
ax.text(4, 0.05, f"Laya: $0.00000 (Free)", ha="right", va="bottom", weight="bold", color="#d95f02")

plt.tight_layout()
p3 = os.path.join(FIG_DIR, "multi_scale_cumulative_cost.png")
plt.savefig(p3)
plt.close()

# -------------------------------------------------------------
# PLOT 4: Expected Calibration Error: Jev vs. Laya
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4.5))
b_w = 0.35
ax.bar(x - b_w/2, jev_ece, width=b_w, label="Native Jev (Sharp Calibration)", color="#1f77b4", alpha=0.9)
ax.bar(x + b_w/2, laya_ece, width=b_w, label="Laya (High Entropy / Uncalibrated)", color="#ff7f0e", alpha=0.9)

ax.set_xticks(x)
ax.set_xticklabels(scale_labels)
ax.set_xlabel("Workload Scale")
ax.set_ylabel("Expected Calibration Error (ECE)")
ax.set_title("Probabilistic Uncertainty Calibration: Jev vs. Laya", weight="bold")
ax.legend(loc="upper right", frameon=True)

for i in range(len(scales)):
    ax.text(x[i] - b_w/2, jev_ece[i] + 0.015, f"{jev_ece[i]:.3f}", ha="center", fontsize=8.5, weight="bold", color="#1f77b4")
    ax.text(x[i] + b_w/2, laya_ece[i] + 0.015, f"{laya_ece[i]:.3f}", ha="center", fontsize=8.5, weight="bold", color="#d95f02")

plt.tight_layout()
p4 = os.path.join(FIG_DIR, "ece_calibration_trajectory.png")
plt.savefig(p4)
plt.close()

# -------------------------------------------------------------
# PLOT 6: Master 4-Panel Triad Overview Figure
# -------------------------------------------------------------
fig, ((ax_a, ax_b), (ax_c, ax_d)) = plt.subplots(2, 2, figsize=(14, 9.5))

# (A) Accuracy
ax_a.bar(x - bar_w, jev_acc, width=bar_w, label="Native Jev", color="#1f77b4")
ax_a.bar(x, laya_acc, width=bar_w, label="Laya (Local)", color="#ff7f0e")
ax_a.bar(x + bar_w, gem_acc, width=bar_w, label="Gemini 2.5", color="#2ca02c")
ax_a.set_ylim(85, 105)
ax_a.set_xticks(x)
ax_a.set_xticklabels(scale_labels)
ax_a.set_title("(A) Multi-Scale Accuracy Across 5 Departments", weight="bold")
ax_a.set_ylabel("Accuracy (%)")
ax_a.legend(loc="lower right")

# (B) Latency
ax_b.plot(scale_labels, jev_p50, marker="s", color="#1f77b4", label="Jev P50")
ax_b.plot(scale_labels, laya_p50, marker="^", color="#ff7f0e", label="Laya P50 (Local CPU)")
ax_b.plot(scale_labels, gem_p50, marker="o", color="#2ca02c", label="Gemini P50 (Cloud API)")
ax_b.set_title("(B) Median (P50) Inference Latency", weight="bold")
ax_b.set_ylabel("Latency (ms)")
ax_b.legend(loc="center right")

# (C) Calibration
ax_c.plot(scale_labels, jev_ece, marker="o", color="#1f77b4", label="Jev ECE (Calibrated)")
ax_c.plot(scale_labels, laya_ece, marker="d", color="#ff7f0e", label="Laya ECE (Uncalibrated)")
ax_c.set_title("(C) Expected Calibration Error (ECE) Comparison", weight="bold")
ax_c.set_ylabel("ECE Score")
ax_c.legend(loc="center right")

# (D) Cost
ax_d.plot(scale_labels, [c * 1000 for c in gem_cost], marker="s", color="#2ca02c", label="Gemini 2.5 Flash")
ax_d.plot(scale_labels, [c * 1000 for c in jev_cost], marker="o", color="#1f77b4", label="Native Jev API")
ax_d.plot(scale_labels, [0.0 for _ in scales], marker="d", color="#ff7f0e", linestyle="--", label="Laya (Open Weights)")
ax_d.set_title("(D) Cumulative Cost ($ USD / 1,000 Decisions)", weight="bold")
ax_d.set_ylabel("Cost ($ USD / 1,000)")
ax_d.legend(loc="upper left")

plt.suptitle("Triad Decision Benchmark: Native Jev vs. Laya vs. Gemini 2.5 Flash (N=10 -> 50)", weight="bold", y=0.995)
plt.tight_layout()
p6 = os.path.join(FIG_DIR, "publication_summary_figure.png")
plt.savefig(p6)
plt.close()
print("[+] Successfully regenerated all 3-way figures!")

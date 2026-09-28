import os
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set high-quality style
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

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "native_jev_scaling_results.json")
FIG_DIR = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(FIG_DIR, exist_ok=True)

with open(RESULTS_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

scale_history = data["scale_metrics_history"]
granular = data["granular_results"]

scales = [10, 20, 30, 40, 50]
scale_labels = [f"N={s}" for s in scales]

jev_acc = [scale_history[f"N={s}"]["jev_accuracy"] for s in scales]
gem_acc = [scale_history[f"N={s}"]["gemini_accuracy"] for s in scales]
agreement = [scale_history[f"N={s}"]["agreement_rate"] for s in scales]

jev_mean_lat = [scale_history[f"N={s}"]["jev_latency"]["mean_ms"] for s in scales]
jev_p50_lat = [scale_history[f"N={s}"]["jev_latency"]["p50_ms"] for s in scales]
gem_mean_lat = [scale_history[f"N={s}"]["gemini_latency"]["mean_ms"] for s in scales]
gem_p50_lat = [scale_history[f"N={s}"]["gemini_latency"]["p50_ms"] for s in scales]

jev_ece = [scale_history[f"N={s}"]["jev_ece"] for s in scales]
jev_conf = [scale_history[f"N={s}"]["jev_mean_confidence"] * 100 for s in scales]

jev_cost = [scale_history[f"N={s}"]["jev_cumulative_cost_usd"] * 1000 for s in scales] # in millicents / $0.001
gem_cost = [scale_history[f"N={s}"]["gemini_cumulative_cost_usd"] * 1000 for s in scales]

# -------------------------------------------------------------
# PLOT 1: Multi-Scale Accuracy & Consensus (Dual Model Bar/Line)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 4.5))
bar_width = 0.28
x = np.arange(len(scales))

ax.bar(x - bar_width/2, jev_acc, width=bar_width, label="Native Jev (System-One)", color="#1f77b4", alpha=0.9)
ax.bar(x + bar_width/2, gem_acc, width=bar_width, label="Gemini 2.5 Flash", color="#2ca02c", alpha=0.9)
ax.plot(x, agreement, color="#d62728", marker="o", linewidth=2.2, label="Model Agreement (%)", linestyle="--")

ax.set_ylim(90, 105)
ax.set_xticks(x)
ax.set_xticklabels(scale_labels)
ax.set_xlabel("Workload Scale (Number of Evaluated Emails)")
ax.set_ylabel("Metric Score (%)")
ax.set_title("Multi-Scale Decision Accuracy & Consensus Rate (N=10 -> 50)", weight="bold")
ax.legend(loc="lower right", frameon=True)
for i in range(len(scales)):
    ax.text(x[i] - bar_width/2, jev_acc[i] + 0.6, f"{jev_acc[i]:.0f}%", ha="center", fontsize=9, weight="bold", color="#1f77b4")
    ax.text(x[i] + bar_width/2, gem_acc[i] + 0.6, f"{gem_acc[i]:.0f}%", ha="center", fontsize=9, weight="bold", color="#2ca02c")

plt.tight_layout()
p1_path = os.path.join(FIG_DIR, "multi_scale_accuracy_consensus.png")
plt.savefig(p1_path)
plt.close()
print(f"[+] Saved: {p1_path}")

# -------------------------------------------------------------
# PLOT 2: Latency Profile Across Scales (Mean & P50)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4.5))
ax.plot(scale_labels, jev_mean_lat, marker="s", linewidth=2, color="#1f77b4", label="Jev Mean Latency")
ax.plot(scale_labels, jev_p50_lat, marker="^", linewidth=2, linestyle=":", color="#17becf", label="Jev P50 Latency")
ax.plot(scale_labels, gem_mean_lat, marker="o", linewidth=2, color="#2ca02c", label="Gemini Mean Latency")
ax.plot(scale_labels, gem_p50_lat, marker="d", linewidth=2, linestyle=":", color="#8c564b", label="Gemini P50 Latency")

ax.set_xlabel("Workload Scale")
ax.set_ylabel("Latency (milliseconds)")
ax.set_title("Inference Latency Profile Across Increasing Workload Scales", weight="bold")
ax.legend(loc="upper left", frameon=True)

# Annotate fast-path vs queueing
ax.annotate(
    "Gemini Sub-Second Baseline (~950ms P50)",
    xy=(2, 950), xytext=(1.5, 2500),
    arrowprops=dict(facecolor="#2ca02c", shrink=0.08, width=1, headwidth=6),
    fontsize=9, weight="semibold", color="#2ca02c"
)
ax.annotate(
    "Jev Container Cold-Start & Queueing Spikes",
    xy=(4, 7190), xytext=(2.2, 6500),
    arrowprops=dict(facecolor="#1f77b4", shrink=0.08, width=1, headwidth=6),
    fontsize=9, weight="semibold", color="#1f77b4"
)

plt.tight_layout()
p2_path = os.path.join(FIG_DIR, "multi_scale_latency.png")
plt.savefig(p2_path)
plt.close()
print(f"[+] Saved: {p2_path}")

# -------------------------------------------------------------
# PLOT 3: Cumulative Tokenomics & Cost Trajectory
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(scale_labels, [c / 1000 for c in jev_cost], marker="o", linewidth=2.5, color="#1f77b4", label="Native Jev (System-One: $0.042/1M in, $0 out)")
ax.plot(scale_labels, [c / 1000 for c in gem_cost], marker="s", linewidth=2.5, color="#2ca02c", label="Gemini 2.5 Flash ($0.075/1M in + $0.30/1M out)")

ax.set_xlabel("Workload Scale (Emails)")
ax.set_ylabel("Cumulative Inference Cost ($ USD)")
ax.set_title("Cumulative Tokenomics Cost Trajectory (2.43x Savings)", weight="bold")
ax.legend(loc="upper left", frameon=True)

diff_50 = (gem_cost[-1] - jev_cost[-1]) / 1000
ax.text(
    4, (jev_cost[-1] / 1000) + 0.0001,
    f"Jev Total: ${jev_cost[-1]/1000:.5f}\n(58.8% Cheaper)",
    ha="right", va="bottom", fontsize=9.5, weight="bold", color="#1f77b4"
)
ax.text(
    4, (gem_cost[-1] / 1000) + 0.0001,
    f"Gemini Total: ${gem_cost[-1]/1000:.5f}",
    ha="right", va="bottom", fontsize=9.5, weight="bold", color="#2ca02c"
)

plt.tight_layout()
p3_path = os.path.join(FIG_DIR, "multi_scale_cumulative_cost.png")
plt.savefig(p3_path)
plt.close()
print(f"[+] Saved: {p3_path}")

# -------------------------------------------------------------
# PLOT 4: Expected Calibration Error (ECE) Trajectory
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 4.2))
bars = ax.bar(scale_labels, jev_ece, color="#ff7f0e", width=0.45, alpha=0.85, edgecolor="#d95f02", linewidth=1.2)
ax.set_xlabel("Workload Scale")
ax.set_ylabel("Expected Calibration Error (ECE)")
ax.set_title("Native Jev Probabilistic Calibration: ECE Convergence", weight="bold")
ax.set_ylim(0, 0.045)

for bar, ece in zip(bars, jev_ece):
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.0015, f"{ece:.3f}", ha="center", va="bottom", fontsize=9.5, weight="bold")

ax.axhline(0.015, color="gray", linestyle="--", linewidth=1, alpha=0.7, label="Asymptotic ECE Target (0.015)")
ax.legend(loc="upper right", frameon=True)

plt.tight_layout()
p4_path = os.path.join(FIG_DIR, "ece_calibration_trajectory.png")
plt.savefig(p4_path)
plt.close()
print(f"[+] Saved: {p4_path}")

# -------------------------------------------------------------
# PLOT 5: Per-Department Confidence & Latency Distribution
# -------------------------------------------------------------
dept_confs = {}
dept_lats = {}
for r in granular:
    d = r["ground_truth"]
    dept_confs.setdefault(d, []).append(r["jev"]["confidence"] * 100)
    dept_lats.setdefault(d, []).append(r["jev"]["latency_ms"])

departments = sorted(list(dept_confs.keys()))
mean_confs = [np.mean(dept_confs[d]) for d in departments]
mean_lats = [np.mean(dept_lats[d]) for d in departments]

fig, ax1 = plt.subplots(figsize=(8, 4.5))
ax2 = ax1.twinx()

x_dept = np.arange(len(departments))
w = 0.35

b1 = ax1.bar(x_dept - w/2, mean_confs, width=w, color="#1f77b4", label="Mean Confidence (%)", alpha=0.9)
b2 = ax2.bar(x_dept + w/2, mean_lats, width=w, color="#aec7e8", edgecolor="#1f77b4", label="Mean Latency (ms)", alpha=0.85)

ax1.set_ylim(80, 105)
ax1.set_ylabel("Confidence Score (%)", color="#1f77b4", weight="bold")
ax2.set_ylabel("Latency (ms)", color="#3182bd", weight="bold")
ax1.set_xticks(x_dept)
ax1.set_xticklabels(departments, rotation=15, ha="right")
ax1.set_title("Native Jev: Confidence Calibration & Latency Across 5 Operational Departments", weight="bold")

for bar in b1:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, h + 0.6, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5, weight="bold")

plt.tight_layout()
p5_path = os.path.join(FIG_DIR, "department_confidence_distribution.png")
plt.savefig(p5_path)
plt.close()
print(f"[+] Saved: {p5_path}")

# -------------------------------------------------------------
# PLOT 6: Master Publication-Ready 2x2 Overview Figure
# -------------------------------------------------------------
fig, ((ax_a, ax_b), (ax_c, ax_d)) = plt.subplots(2, 2, figsize=(13, 9))

# (A) Accuracy
ax_a.bar(x - bar_width/2, jev_acc, width=bar_width, label="Native Jev", color="#1f77b4")
ax_a.bar(x + bar_width/2, gem_acc, width=bar_width, label="Gemini 2.5 Flash", color="#2ca02c")
ax_a.plot(x, agreement, color="#d62728", marker="o", linestyle="--", label="Consensus Rate")
ax_a.set_ylim(92, 104)
ax_a.set_xticks(x)
ax_a.set_xticklabels(scale_labels)
ax_a.set_title("(A) Multi-Scale Accuracy & Model Agreement", weight="bold")
ax_a.set_ylabel("Accuracy (%)")
ax_a.legend(loc="lower right")

# (B) Latency Trajectory
ax_b.plot(scale_labels, jev_p50_lat, marker="s", linewidth=2, color="#1f77b4", label="Jev P50 Latency")
ax_b.plot(scale_labels, gem_p50_lat, marker="o", linewidth=2, color="#2ca02c", label="Gemini P50 Latency")
ax_b.plot(scale_labels, jev_mean_lat, marker="^", linestyle=":", color="#17becf", label="Jev Mean Latency")
ax_b.set_title("(B) Median (P50) & Mean Inference Latency", weight="bold")
ax_b.set_ylabel("Latency (ms)")
ax_b.legend(loc="upper left")

# (C) ECE Calibration
ax_c.plot(scale_labels, jev_ece, marker="d", linewidth=2.5, color="#ff7f0e", label="Jev ECE")
ax_c.fill_between(scale_labels, 0, jev_ece, color="#ff7f0e", alpha=0.2)
ax_c.set_ylim(0, 0.045)
ax_c.set_title("(C) Expected Calibration Error (ECE) Convergence", weight="bold")
ax_c.set_ylabel("ECE Score")
for s, val in zip(scale_labels, jev_ece):
    ax_c.annotate(f"{val:.3f}", (s, val), textcoords="offset points", xytext=(0,7), ha="center", weight="bold", fontsize=9)

# (D) Cost Trajectory
ax_d.plot(scale_labels, [c / 1000 for c in jev_cost], marker="o", linewidth=2.5, color="#1f77b4", label="Native Jev Total")
ax_d.plot(scale_labels, [c / 1000 for c in gem_cost], marker="s", linewidth=2.5, color="#2ca02c", label="Gemini 2.5 Total")
ax_d.set_title("(D) Cumulative Inference Cost ($ USD)", weight="bold")
ax_d.set_ylabel("Cost ($ USD)")
ax_d.legend(loc="upper left")

plt.suptitle("Empirical Multi-Scale Evaluation: Native Jev System-One vs. Gemini 2.5 Flash (N=10 -> 50)", weight="bold", y=0.995)
plt.tight_layout()
p6_path = os.path.join(FIG_DIR, "publication_summary_figure.png")
plt.savefig(p6_path)
plt.close()
print(f"[+] Saved: {p6_path}")

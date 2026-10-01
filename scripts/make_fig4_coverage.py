# -*- coding: utf-8 -*-
"""Figure 4: Coverage design + difficulty, seaborn deep palette."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

plt.rcParams.update({"font.family": "Times New Roman", "mathtext.fontset": "stix", "font.size": 9})

# seaborn deep palette (CV paper standard)
BLUE   = "#4C72B0"
GREEN  = "#55A868"
RED    = "#C44E52"
PURPLE = "#8172B2"
LBLUE  = "#8CB4D9"  # lighter blue for val
C_FRAME = "#1A1A1A"; C_GRID = "#D8D8D8"

def style(ax):
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    for s in ax.spines.values():
        s.set_visible(True); s.set_color(C_FRAME); s.set_linewidth(0.8)
    ax.tick_params(direction="in", which="major", length=4, width=0.8, top=True, right=True)
    ax.tick_params(direction="in", which="minor", length=2.2, width=0.6, top=True, right=True)
    ax.set_axisbelow(True)

v2raw = json.load(open("v2_coverage_buckets.json", encoding="utf-8"))
v2 = {k: v["buckets"] for k, v in v2raw.items()}
buckets = ["0–5", "5–20", "20–50", "50–80", "80–100", "100"]
BUCKET_MID = [2.5, 12.5, 35.0, 65.0, 90.0]

r = json.load(open(r"bench_results/results.json", encoding="utf-8"))
BUCKETS = ["0-5", "5-20", "20-50", "50-80", "80-100"]
METHODS = [
    ("XLM-R-span",    BLUE,   "D", "-"),
    ("XLM-R-CLS",     RED,    "s", "--"),
    ("GLTR",          GREEN,  "^", "-."),
    ("DetectLLM-LRR", PURPLE, "o", ":"),
]
perf = {m: [r["stratified"][m]["coverage"][b]["f1"] for b in BUCKETS] for m, _, _, _ in METHODS}

fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6))

# Panel (a): coverage distribution
ax = axes[0]
x = np.arange(len(buckets)); w = 0.24
for i, (split, color) in enumerate([("train", BLUE), ("val", LBLUE), ("test", RED)]):
    tot = sum(v2[split])
    prop = [c / tot * 100 for c in v2[split]]
    bars = ax.bar(x + (i - 1) * w, prop, w, color=color, zorder=3, label=split)
    for b, p in zip(bars, prop):
        if p >= 3:
            ax.text(b.get_x() + b.get_width() / 2, p + 0.4, f"{p:.0f}",
                    ha="center", va="bottom", fontsize=6.5, color="#333333", rotation=90)
ax.set_xticks(x); ax.set_xticklabels(buckets, fontsize=8.5)
ax.set_xlabel("AI coverage (%)", fontsize=9)
ax.set_ylabel("Mixed docs (%)", fontsize=9)
ax.set_ylim(0, 40)
ax.legend(frameon=False, fontsize=8, loc="upper right")
ax.yaxis.grid(True, color=C_GRID, lw=0.7, linestyle=":")
ax.set_title("(A) Coverage distribution (C1–C11 quota design)", fontsize=10.5,
             fontweight="bold", color="#1A1A1A", loc="left", pad=8)
style(ax)

# Panel (b): performance vs coverage
ax = axes[1]
for label, color, marker, ls in METHODS:
    ys = perf[label]
    ax.plot(BUCKET_MID, ys, color=color, marker=marker, ms=6, lw=1.6,
            ls=ls, markeredgecolor=color, markerfacecolor=color, zorder=3, label=label)
    if label == "XLM-R-span":
        ax.annotate("F1 = 0.27", (BUCKET_MID[0], ys[0]), textcoords="offset points",
                    xytext=(12, -12), fontsize=8, color=color, fontweight="bold")
    elif label == "XLM-R-CLS":
        ax.annotate("F1 = 0.11", (BUCKET_MID[0], ys[0]), textcoords="offset points",
                    xytext=(12, 8), fontsize=8, color=color, fontweight="bold")
ax.axhline(0.5, color="#999999", lw=0.8, ls="--", zorder=1)
ax.text(88, 0.515, "chance", fontsize=7.5, color="#999999", ha="right")
ax.set_xlabel("AI coverage (%)", fontsize=9)
ax.set_ylabel("F1 (Human vs. AI)", fontsize=9)
ax.set_xticks(BUCKET_MID)
ax.set_xticklabels(["0–5", "5–20", "20–50", "50–80", "80–100"], fontsize=8.5)
ax.set_ylim(-0.02, 1.08)
ax.legend(frameon=True, fancybox=False, edgecolor="#888888", facecolor="white",
          fontsize=8, loc="lower right", borderpad=0.5, labelspacing=0.35,
          handlelength=2.0, handletextpad=0.4)
ax.yaxis.grid(True, color=C_GRID, lw=0.7, linestyle=":")
ax.set_title("(B) Detection performance vs. AI coverage", fontsize=10.5,
             fontweight="bold", color="#1A1A1A", loc="left", pad=8)
style(ax)

fig.suptitle("Coverage quota design and its impact on detection difficulty",
             fontsize=12, fontweight="bold", color="#1A1A1A", y=1.03)
fig.tight_layout()
fig.savefig("figures/fig4_coverage.png", dpi=600, bbox_inches="tight", facecolor="white")
fig.savefig("figures/fig4_coverage.pdf", bbox_inches="tight", facecolor="white")
print("FIG4_SNS_SAVED")

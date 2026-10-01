# -*- coding: utf-8 -*-
"""Figure 9 v2: Per-generator 3-class F1 heatmap (correct: AI+human mixed subsets)."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "Times New Roman", "mathtext.fontset": "stix", "font.size": 9})

data = json.load(open(r"bench_results/generator_f1_v2.json", encoding="utf-8"))

SEEN = ["SEEN_deepseek-v4-flash", "SEEN_minimax-m2.5"]
UNSEEN = ["gpt-5.5", "gemini-3.7-flash", "glm-5.3", "hy3", "kimi-k2.7-code", "qwen3.6-35b-a3b"]
ALL = SEEN + UNSEEN

GMAP = {"SEEN_deepseek-v4-flash": "DeepSeek\n(seen)", "SEEN_minimax-m2.5": "MiniMax\n(seen)",
        "gpt-5.5": "GPT-5.5", "gemini-3.7-flash": "Gemini", "glm-5.3": "GLM-5.3",
        "hy3": "HY3", "kimi-k2.7-code": "Kimi", "qwen3.6-35b-a3b": "Qwen"}
labels = [GMAP[g] for g in ALL]

ROWS = [
    ("Macro-F1",   [data[g]["macro_f1"] for g in ALL]),
    ("HUMAN F1",   [data[g]["HUMAN_f1"] for g in ALL]),
    ("PARTIAL F1", [data[g]["PARTIAL_f1"] for g in ALL]),
    ("FULL_AI F1", [data[g]["FULL_f1"] for g in ALL]),
]
mat = np.array([r[1] for r in ROWS])

fig, ax = plt.subplots(figsize=(10.5, 3.5))
im = ax.imshow(mat, cmap="RdYlBu_r", vmin=0.0, vmax=1.0, aspect="auto", interpolation="nearest")

ax.set_xticks(range(len(ALL)))
ax.set_xticklabels(labels, fontsize=8.5)
ax.set_yticks(range(len(ROWS)))
ax.set_yticklabels([r[0] for r in ROWS], fontsize=9)

for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        v = mat[i, j]
        color = "white" if (v < 0.30 or v > 0.85) else "#222222"
        txt = f"{v:.2f}" if v > 0.005 else "0.00"
        ax.text(j, i, txt, ha="center", va="center", fontsize=8, color=color)

ax.axvline(1.5, color="#333333", lw=1.5, ls="--")
ax.text(0.5, -0.7, "Seen", fontsize=8.5, ha="center", color="#333333", fontweight="bold")
ax.text(4.5, -0.7, "Unseen (held-out)", fontsize=8.5, ha="center", color="#333333", fontweight="bold")

for s in ax.spines.values():
    s.set_visible(True); s.set_color("#1A1A1A"); s.set_linewidth(0.8)
ax.tick_params(direction="out", which="major", length=3, width=0.8)

cb = fig.colorbar(im, ax=ax, shrink=0.9, pad=0.01, aspect=10)
cb.set_label("F1", fontsize=8.5)
cb.ax.tick_params(labelsize=7.5)
cb.outline.set_linewidth(0.5)

ax.set_title("3-class F1 by generator (XLM-R-CLS, full test set)",
             fontsize=10.5, color="#1A1A1A", fontweight="bold", pad=8)

fig.tight_layout()
fig.savefig("figures/fig_generator_heatmap.png", dpi=600, bbox_inches="tight",
            facecolor="white", pad_inches=0.05)
fig.savefig("figures/fig_generator_heatmap.pdf", bbox_inches="tight",
            facecolor="white", pad_inches=0.05)
print("FIG9_GEN_V2_SAVED")

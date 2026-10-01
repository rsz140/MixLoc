# -*- coding: utf-8 -*-
"""Figure 11 v2: Compact 3-class F1 heatmap, minimal whitespace."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "Times New Roman", "mathtext.fontset": "stix", "font.size": 9})

data = json.load(open(r"bench_results/language_f1_full.json", encoding="utf-8"))
mf1 = data["macro_f1"]
pcf = data["per_class_f1"]

langs = sorted(mf1["XLM-R-CLS"].keys(),
               key=lambda l: mf1["XLM-R-CLS"][l], reverse=True)

ROWS = [
    ("CLS  Macro-F1",    [mf1["XLM-R-CLS"].get(l, np.nan) for l in langs]),
    ("span Macro-F1",    [mf1["XLM-R-span"].get(l, np.nan) for l in langs]),
    ("     HUMAN",       [pcf["HUMAN"].get(l, np.nan) for l in langs]),
    ("     PARTIAL",     [pcf["PARTIAL_AI"].get(l, np.nan) for l in langs]),
    ("     FULL_AI",     [pcf["FULL_AI"].get(l, np.nan) for l in langs]),
]

mat = np.array([row[1] for row in ROWS])
row_labels = [row[0] for row in ROWS]

fig, ax = plt.subplots(figsize=(11.0, 3.2))
im = ax.imshow(mat, cmap="RdYlBu_r", vmin=0.0, vmax=1.0, aspect="auto",
               interpolation="nearest")

ax.set_xticks(np.arange(len(langs)))
ax.set_xticklabels(langs, fontsize=8.5)
ax.set_yticks(np.arange(len(ROWS)))
ax.set_yticklabels(row_labels, fontsize=8.5)

for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        if not np.isnan(mat[i, j]):
            v = mat[i, j]
            color = "white" if (v < 0.30 or v > 0.85) else "#222222"
            txt = f"{v:.2f}" if v > 0.005 else "0"
            ax.text(j, i, txt, ha="center", va="center", fontsize=7, color=color)

ax.axhline(1.5, color="#333333", lw=1.0)
ax.axhline(0.5, color="#666666", lw=0.5, linestyle=":")

for s in ax.spines.values():
    s.set_visible(True); s.set_color("#1A1A1A"); s.set_linewidth(0.8)
ax.tick_params(direction="out", which="major", length=3, width=0.8, pad=2)

cb = fig.colorbar(im, ax=ax, shrink=0.9, pad=0.01, aspect=12)
cb.set_label("F1", fontsize=8.5)
cb.ax.tick_params(labelsize=7.5, pad=1)
cb.outline.set_linewidth(0.5)

ax.set_title("3-class Macro-F1 by language (full test set, n=202,762)",
             fontsize=10, color="#1A1A1A", fontweight="bold", pad=6)

fig.subplots_adjust(left=0.10, right=0.92, top=0.88, bottom=0.08, wspace=0, hspace=0)
fig.savefig("figures/fig_lang_f1_full.png", dpi=600, bbox_inches="tight",
            facecolor="white", pad_inches=0.05)
fig.savefig("figures/fig_lang_f1_full.pdf", bbox_inches="tight",
            facecolor="white", pad_inches=0.05)
print("FIG11_COMPACT_SAVED")

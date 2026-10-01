# -*- coding: utf-8 -*-
"""Generate additional paper figures from full-set evaluation data."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

plt.rcParams.update({"font.family": "Times New Roman", "mathtext.fontset": "stix", "font.size": 9})
BLUE="#4C72B0"; GREEN="#55A868"; RED="#C44E52"; PURPLE="#8172B2"; LBLUE="#8CB4D9"; GREY="#8C8C8C"
FRAME="#1A1A1A"; GRID="#D8D8D8"

FR = json.load(open(r"bench_results/full_results.json", encoding="utf-8"))
SR = json.load(open(r"bench_results/results.json", encoding="utf-8"))

def style(ax):
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    for s in ax.spines.values():
        s.set_visible(True); s.set_color(FRAME); s.set_linewidth(0.8)
    ax.tick_params(direction="in", which="major", length=4, width=0.8, top=True, right=True)
    ax.tick_params(direction="in", which="minor", length=2.2, width=0.6, top=True, right=True)
    ax.set_axisbelow(True)

# ========== 1) Main results: 3-panel bar chart ==========
METHODS = list(FR["binary"].keys())
MCOLS = [GREY, GREEN, LBLUE, RED, BLUE, PURPLE, "#CCB974"]
if len(METHODS) > len(MCOLS):
    MCOLS = MCOLS * 2

fig, axes = plt.subplots(1, 3, figsize=(14.0, 4.6))
x = np.arange(len(METHODS))
names = [m.replace("-style", "\n(adapted)") for m in METHODS]

# AUROC
auroc = [FR["binary"][m]["auroc"] for m in METHODS]
bars = axes[0].bar(x, auroc, 0.62, color=MCOLS[:len(METHODS)], zorder=3)
for b, v in zip(bars, auroc):
    axes[0].text(b.get_x()+b.get_width()/2, v+0.012, f"{v:.3f}", ha="center", fontsize=7.5)
axes[0].set_xticks(x); axes[0].set_xticklabels(names, fontsize=7, rotation=25, ha="right")
axes[0].set_ylim(0, 1.05); axes[0].set_ylabel("AUROC")
axes[0].set_title("(A) Binary Detection: AUROC", fontsize=10.5, fontweight="bold", color=FRAME, loc="left")
style(axes[0])

# BACC
bacc = [FR["binary"][m]["bacc"] for m in METHODS]
bars = axes[1].bar(x, bacc, 0.62, color=MCOLS[:len(METHODS)], zorder=3)
for b, v in zip(bars, bacc):
    axes[1].text(b.get_x()+b.get_width()/2, v+0.012, f"{v:.3f}", ha="center", fontsize=7.5)
axes[1].set_xticks(x); axes[1].set_xticklabels(names, fontsize=7, rotation=25, ha="right")
axes[1].set_ylim(0, 1.05); axes[1].set_ylabel("Balanced Accuracy")
axes[1].set_title("(B) Binary Detection: BACC", fontsize=10.5, fontweight="bold", color=FRAME, loc="left")
style(axes[1])

# 3-class macro F1 + diagnostics
d3 = ["XLM-R-span", "XLM-R-CLS"]
diag = ["Majority", "Length-only LR", "Source-only LR"]
vals = [FR["doc3"][m]["macro_f1"] for m in d3] + [SR["shortcut_diagnostic"][d]["macro_f1"] for d in diag]
cols = [BLUE, RED, "#BBBBBB", "#BBBBBB", "#888888"]
labs = ["XLM-R-span", "XLM-R-CLS", "Majority", "Length-LR", "Source-LR"]
bars = axes[2].bar(np.arange(5), vals, 0.62, color=cols, zorder=3)
for b, v in zip(bars, vals):
    axes[2].text(b.get_x()+b.get_width()/2, v+0.012, f"{v:.3f}", ha="center", fontsize=7.5)
axes[2].set_xticks(np.arange(5)); axes[2].set_xticklabels(labs, fontsize=7, rotation=25, ha="right")
axes[2].set_ylim(0, 1.05); axes[2].set_ylabel("Macro-F1 (3-class)")
axes[2].set_title("(C) 3-Class + Shortcuts", fontsize=10.5, fontweight="bold", color=FRAME, loc="left")
style(axes[2])

fig.suptitle("Document-level benchmark results (full test set, n=202,762)",
             fontsize=12, fontweight="bold", color=FRAME, y=1.03)
fig.tight_layout()
fig.savefig("figures/fig_main_results.png", dpi=600, bbox_inches="tight", facecolor="white")
fig.savefig("figures/fig_main_results.pdf", bbox_inches="tight", facecolor="white")
plt.close()
print("1) main_results DONE")

# ========== 2) Confusion matrices ==========
LAB = ["HUMAN", "PARTIAL", "FULL"]
fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.4))
for ax, m in zip(axes, ["XLM-R-span", "XLM-R-CLS"]):
    cm = np.array(FR["doc3"][m]["confusion"], dtype=float)
    cmn = cm / cm.sum(1, keepdims=True)
    im = ax.imshow(cmn, cmap="Blues", vmin=0, vmax=1)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{cmn[i,j]:.2f}\n({int(cm[i,j]):,})", ha="center", va="center",
                    fontsize=8.5, color="white" if cmn[i,j] > 0.5 else "#333333")
    ax.set_xticks(range(3)); ax.set_yticks(range(3))
    ax.set_xticklabels(LAB, fontsize=8.5); ax.set_yticklabels(LAB, fontsize=8.5)
    ax.set_xlabel("Predicted", fontsize=9); ax.set_ylabel("Gold", fontsize=9)
    acc = FR["doc3"][m]["acc"]; mf1 = FR["doc3"][m]["macro_f1"]
    ax.set_title(f"{m}  (Acc {acc:.3f}, mF1 {mf1:.3f})", fontsize=10, color=BLUE, fontweight="bold")
fig.suptitle("3-class confusion matrices (row-normalized, full test set)", fontsize=11.5, color=BLUE, fontweight="bold", y=1.03)
fig.tight_layout()
fig.savefig("figures/fig_confusion.png", dpi=600, bbox_inches="tight", facecolor="white")
fig.savefig("figures/fig_confusion.pdf", bbox_inches="tight", facecolor="white")
plt.close()
print("2) confusion DONE")

# ========== 3) Generator heatmap (sample-based F1) ==========
gens_all = set()
for m in SR["stratified"]:
    gens_all.update(SR["stratified"][m].get("generator", {}).keys())
gens = sorted(gens_all - {"HUMAN(cols)"})
GMAP = {"deepseek-v4-flash":"DeepSeek\n(Seen)","minimax-m2.5":"MiniMax\n(Seen)",
        "gpt-5.5":"GPT-5.5","gemini-3.7-flash":"Gemini","glm-5.3":"GLM-5.3",
        "hy3":"HY3","kimi-k2.7-code":"Kimi","qwen3.6-35b-a3b":"Qwen"}
glabels = [GMAP.get(g, g) for g in gens]
hm_methods = list(SR["stratified"].keys())
mat = np.full((len(hm_methods), len(gens)), np.nan)
for i, m in enumerate(hm_methods):
    gd = SR["stratified"][m].get("generator", {})
    for j, g in enumerate(gens):
        v = gd.get(g, {})
        if "f1" in v:
            mat[i, j] = v["f1"]

fig, ax = plt.subplots(figsize=(11.5, 4.5))
im = ax.imshow(mat, cmap="RdYlBu_r", vmin=0.3, vmax=1.0, aspect="auto")
ax.set_xticks(range(len(gens))); ax.set_xticklabels(glabels, fontsize=8)
ax.set_yticks(range(len(hm_methods))); ax.set_yticklabels(hm_methods, fontsize=9)
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        if not np.isnan(mat[i, j]):
            c = "white" if (mat[i,j] < 0.45 or mat[i,j] > 0.9) else "#222222"
            ax.text(j, i, f"{mat[i,j]:.2f}", ha="center", va="center", fontsize=7.5, color=c)
# vertical line between seen and unseen generators
seen_count = sum(1 for g in gens if "Seen" in GMAP.get(g, ""))
if seen_count > 0:
    ax.axvline(seen_count - 0.5, color="#333333", lw=1.5, ls="--")
    ax.text(seen_count - 0.5, -0.8, "Seen | Unseen", fontsize=8, ha="center", color="#333333")
cb = fig.colorbar(im, ax=ax, shrink=0.85); cb.set_label("F1", fontsize=9)
ax.set_title("Binary F1 by generator (test = unseen generators for supervised models)",
             fontsize=11, color=BLUE, fontweight="bold", pad=10)
fig.tight_layout()
fig.savefig("figures/fig_generator_heatmap.png", dpi=600, bbox_inches="tight", facecolor="white")
fig.savefig("figures/fig_generator_heatmap.pdf", bbox_inches="tight", facecolor="white")
plt.close()
print("3) generator_heatmap DONE")

# ========== 4) Paraphrase attack ==========
AT = json.load(open(r"bench_results/attack_results.json", encoding="utf-8"))
ms = list(AT["methods"].keys())
before = [AT["methods"][m]["auroc_before"] for m in ms]
after = [AT["methods"][m]["auroc_after"] for m in ms]
fig, ax = plt.subplots(figsize=(8.8, 4.2))
xx = np.arange(len(ms)); w = 0.36
ax.bar(xx - w/2, before, w, color=BLUE, label="Before attack", zorder=3)
ax.bar(xx + w/2, after, w, color=RED, label="After paraphrase", zorder=3)
for i, (b, a) in enumerate(zip(before, after)):
    ax.text(i - w/2, b + 0.012, f"{b:.3f}", ha="center", fontsize=8)
    ax.text(i + w/2, a + 0.012, f"{a:.3f}", ha="center", fontsize=8)
ax.set_xticks(xx); ax.set_xticklabels(ms, fontsize=8.5, rotation=12, ha="right")
ax.set_ylim(0, 1.1); ax.set_ylabel("AUROC")
ax.legend(frameon=True, fancybox=False, edgecolor="#888888", fontsize=9)
ax.set_title("Paraphrase attack (English subset, n=800)", fontsize=11.5, color=BLUE, fontweight="bold")
ax.yaxis.grid(True, color=GRID, lw=0.7, linestyle=":")
style(ax)
fig.tight_layout()
fig.savefig("figures/fig_attack.png", dpi=600, bbox_inches="tight", facecolor="white")
fig.savefig("figures/fig_attack.pdf", bbox_inches="tight", facecolor="white")
plt.close()
print("4) attack DONE")

print("ALL_EXTRA_FIGS_DONE")

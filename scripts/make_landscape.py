# -*- coding: utf-8 -*-
"""Fig.2 Dataset Landscape / Positioning Map (English, Times New Roman, journal style)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.legend_handler import HandlerTuple
import numpy as np

plt.rcParams.update({
    "font.family": "Times New Roman",
    "mathtext.fontset": "stix",
    "font.size": 11,
    "axes.edgecolor": "#666666",
})

BLUE   = "#55A868"   # mixed-authorship (seaborn deep green)
GREY   = "#4C72B0"   # document-level (seaborn deep blue)
ORANGE = "#C44E52"   # ours (seaborn deep red)
RING   = "#4A4A4A"   # fine-grained provenance ring (charcoal dashed)

# name: (size_texts, langs, generators, type, provenance)
DATA = [
    ("HC3",        85449, 2,  1,  "doc",  False),
    ("TuringBench",200000,1,  20, "doc",  False),
    ("M4",        147470, 7,  8,  "doc",  False),
    ("RAID",     6000000, 1,  11, "doc",  False),
    ("MULTITuDE",  74081, 11, 11, "doc",  False),
    ("RoFT",        7257, 1,  1,  "mix",  False),
    ("MixSet",      3600, 1,  3,  "mix",  False),
    ("LLMTrace",   54309, 2,  31, "mix",  True),
    ("HACo-Det",   11200, 1,  4,  "mix",  True),
    ("Ours",      601846, 20, 8,  "mix",  True),
]

def rad(g):
    return 90 + 200 * np.sqrt(g) / np.sqrt(31.0)   # area-ish scaling, 1..31 gens

fig, ax = plt.subplots(figsize=(8.8, 5.4))
LABEL_OFF = {
    "HC3":        (10, -14, "left"),
    "TuringBench": (0, 11, "center"),
    "M4":         (-12, -16, "left"),
    "RAID":       (-8, 10, "right"),
    "MULTITuDE":  (-8, 12, "left"),
    "RoFT":       (-6, -16, "center"),
    "MixSet":     (0, 12, "center"),
    "LLMTrace":   (-12, 24, "left"),
    "HACo-Det":   (10, -25, "left"),
    "Ours":       (30, 2, "left"),
}
for name, size, langs, gens, typ, prov in DATA:
    x, y = size, langs
    r = rad(gens)
    ours = name == "Ours"
    fc = ORANGE if ours else (BLUE if typ == "mix" else GREY)
    marker = "s" if typ == "mix" else "o"
    ax.scatter(x, y, s=r, marker=marker, facecolor=fc, edgecolor="white",
               linewidth=1.2, zorder=4, alpha=0.95)
    if ours:
        ax.scatter(x, y, s=r + 260, marker=marker, facecolor="none",
                   edgecolor="#6E3034", linewidth=2.2, zorder=5)
    if prov:
        ax.scatter(x, y, s=r + 720, marker=marker, facecolor="none",
                   edgecolor=RING, linewidth=1.6, linestyle=(0, (4, 2.4)), zorder=3)
    dx, dy, ha = LABEL_OFF[name]
    ax.annotate(name, (x, y), textcoords="offset points", xytext=(dx, dy),
                ha=ha, fontsize=11,
                fontweight="bold" if ours else "normal",
                color="#6E3034" if ours else "#333333")
ax.annotate("601,846 texts · 20 langs · char-level gold",
            (601846, 20), textcoords="offset points", xytext=(30, -14),
            ha="left", fontsize=9.5, style="italic", color="#8C4A02")

ax.set_xscale("log")
ax.set_xlim(2500, 2.2e7)
ax.set_ylim(-1.5, 23.5)
ax.set_xticks([3e3, 1e4, 1e5, 1e6, 1e7])
ax.set_xticklabels(["$3\\times10^3$", "$10^4$", "$10^5$", "$10^6$", "$10^7$"])
ax.set_xlabel("Dataset size (number of texts, $\\log_{10}$ scale)", fontsize=12)
ax.set_ylabel("Number of languages", fontsize=12)
for s in ax.spines.values():
    s.set_visible(True)
    s.set_color("#444444")
    s.set_linewidth(1.0)
ax.tick_params(direction="in", top=True, right=True, width=1.0, length=4.5)
ax.tick_params(which="minor", direction="in", top=True, right=True, length=2.8)
ax.yaxis.grid(True, color="#EAEAEA", lw=0.7); ax.set_axisbelow(True)
ax.xaxis.grid(True, color="#E8E8E8", lw=0.8)

handles = [
    Line2D([], [], marker="o", ls="", color=GREY, markersize=9, label="Document-level"),
    Line2D([], [], marker="s", ls="", color=BLUE, markersize=9, label="Mixed-authorship"),
    Line2D([], [], marker="s", ls="", markeredgecolor=RING, markerfacecolor="none",
           markersize=12, label="Fine-grained provenance (char/word-level)", linestyle="none"),
    Line2D([], [], marker="s", ls="", markerfacecolor=ORANGE, markeredgecolor="#7A1F16",
           markeredgewidth=2, markersize=11, label="Ours"),
]
leg1 = ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=10,
                 handletextpad=0.4, borderaxespad=0.2)
ax.add_artist(leg1)

# size legend (bottom-right)
for g in [1, 10, 31]:
    ax.scatter([], [], s=rad(g), facecolor="#BBBBBB", edgecolor="white", label=str(g))
ax.legend(loc="upper right", frameon=False, fontsize=10, title="Number of generators",
          labelspacing=1.5, borderpad=0.6, title_fontsize=10, scatterpoints=1)

ax.set_title("Landscape of AIGT detection & attribution benchmarks",
             fontsize=13, color="#2F2F2F", fontweight="bold", pad=10)

fig.savefig("figures/fig_landscape.png", dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig("figures/fig_landscape.pdf", bbox_inches="tight", facecolor="white")
print("LANDSCAPE_SAVED")

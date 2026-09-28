"""Figures for the A2 report. Run after analysis.py: python3 python/make_figures.py"""
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from mlxtend.frequent_patterns import association_rules, fpgrowth
from mlxtend.preprocessing import TransactionEncoder

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results"

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#d8d7d2"
plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False,
    "axes.spines.right": False, "figure.facecolor": "white", "axes.facecolor": "white"})

baskets = [[i.strip() for i in l.split(",") if i.strip()]
           for l in (ROOT / "data" / "groceries.csv").read_text(encoding="utf-8").splitlines() if l.strip()]
n = len(baskets)
counts = Counter(i for b in baskets for i in b)

# Figure 1 -- item frequency: magnitude by identity, one series, one hue.
top = counts.most_common(20)[::-1]
fig, ax = plt.subplots(figsize=(6.2, 4.6))
ys = range(len(top))
vals = [v / n * 100 for _, v in top]
ax.barh(list(ys), vals, height=0.68, color=BLUE, zorder=3)
ax.set_yticks(list(ys))
ax.set_yticklabels([k for k, _ in top])
ax.set_xlabel("Share of baskets containing the item (%)")
ax.xaxis.grid(True, color=GRID, lw=0.6, zorder=0)
ax.set_axisbelow(True)
for i, v in zip(ys, vals):
    ax.text(v + 0.25, i, f"{v:.1f}", va="center", fontsize=7.5, color=MUTED)
ax.set_xlim(0, max(vals) * 1.12)
ax.spines["left"].set_color(MUTED)
fig.tight_layout()
fig.savefig(OUT / "fig_item_frequency.png", dpi=200)
plt.close(fig)

# Figure 2 -- confidence against lift, whole milk against everything else.
encoder = TransactionEncoder()
matrix = pd.DataFrame(encoder.fit(baskets).transform(baskets), columns=encoder.columns_)
rules = association_rules(fpgrowth(matrix, min_support=0.01, use_colnames=True),
                          metric="confidence", min_threshold=0.20)
rules["c_"] = rules.consequents.map(lambda s: ", ".join(sorted(s)))
milk, rest = rules[rules.c_ == "whole milk"], rules[rules.c_ != "whole milk"]

fig, ax = plt.subplots(figsize=(6.2, 4.0))
ax.axhline(1.0, color=MUTED, lw=1.0, ls="--", zorder=2)
ax.text(0.598, 1.02, "lift = 1: the rule says nothing", fontsize=7.5, color=MUTED, ha="right")
ax.scatter(rest.confidence, rest.lift, s=26, c=BLUE, alpha=0.75, lw=0.7,
           edgecolors="white", zorder=3, label="all other rules")
ax.scatter(milk.confidence, milk.lift, s=26, c=ORANGE, alpha=0.85, lw=0.7,
           edgecolors="white", zorder=4, label="consequent = whole milk")
ax.set_xlabel("Confidence")
ax.set_ylabel("Lift")
ax.yaxis.grid(True, color=GRID, lw=0.6, zorder=0)
ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=8, loc="upper left")
worst = rules.nsmallest(1, "lift").iloc[0]
ax.annotate(f"soda $\\to$ whole milk\nconf {worst.confidence:.2f}, lift {worst.lift:.2f}",
            xy=(worst.confidence, worst.lift), xytext=(worst.confidence + 0.04, 0.62),
            fontsize=7.5, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
best = rules.nlargest(1, "lift").iloc[0]
ax.annotate("fresh-produce cluster", xy=(best.confidence, best.lift),
            xytext=(best.confidence + 0.03, 3.35), fontsize=7.5, color=INK,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
ax.set_ylim(0.55, 3.6)
fig.tight_layout()
fig.savefig(OUT / "fig_conf_lift.png", dpi=200)
plt.close(fig)

print("wrote", OUT / "fig_item_frequency.png")
print("wrote", OUT / "fig_conf_lift.png")

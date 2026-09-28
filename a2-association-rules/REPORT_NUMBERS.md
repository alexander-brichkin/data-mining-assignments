# A2 — verified numbers for the report

Everything below was produced by `python/analysis.py` on `data/groceries.csv` and is
re-checked every time that script runs (it exits non-zero if anything drifts).
Thresholds are the ones in the RapidMiner process: **min support 0.01, min confidence 0.20**.

## Data understanding

| | |
|---|---|
| Baskets (transactions) | 9,835 |
| Distinct items | 169 |
| Item instances | 43,367 |
| Basket size min / mean / max | 1 / 4.41 / 32 |
| Baskets with a single item | 2,159 |
| Most frequent item | whole milk, 25.55 % of baskets |

Top items by share of baskets: whole milk 25.6 %, other vegetables 19.3 %, rolls/buns 18.4 %,
soda 17.4 %, yogurt 14.0 %, bottled water 11.1 %, root vegetables 10.9 %, tropical fruit 10.5 %.

Figure: `results/fig_item_frequency.png`.

## Data preparation

The file is one basket per line, variable length, comma separated, **no header row**. It goes
into a 9,835 × 169 binary matrix — one column per item, true when the basket contains it.
In RapidMiner that is Read CSV → Split → Generate ID → De-Pivot → Pivot (count) →
Replace Missing (0) → Set Role (id) → Numerical to Binominal.

Two fixes were needed in the process: the CSV path was absolute
(`C:/Users/…/Downloads/…`) and is now relative, and `first_row_as_names` was true — with
no header in the file that ate the first basket (`citrus fruit, semi-finished bread,
margarine, ready soups`) as column names.

## Modeling

| Threshold | Result |
|---|---|
| min support 0.01 | 333 frequent itemsets — 88 of size 1, 213 of size 2, 32 of size 3 |
| min confidence 0.20 | 234 rules |
| lift range | 0.899 … 3.295 |
| rules with a single item on the left | 154 (80 have two) |

Threshold sensitivity, for the "how much did you have to tune" question:

| support | confidence | rules | max lift |
|---|---|---|---|
| 0.01 | 0.20 | 234 | 3.295 |
| 0.01 | 0.30 | 125 | 3.295 |
| 0.01 | 0.50 | 15 | 3.030 |
| 0.005 | 0.20 | 892 | 5.212 |
| 0.005 | 0.50 | 120 | 3.691 |

At support 0.01 nothing longer than a 3-itemset survives; dropping to 0.005 produces
4-itemsets and 892 rules, which is more than can be read.

## Evaluation — the three findings

**1. Confidence alone is misleading.** Whole milk appears in 25.55 % of baskets, so it is the
consequent of 70 of the 234 rules and it holds the highest confidences in the whole set. Three
of those rules have lift below 1:

| rule | support | confidence | lift |
|---|---|---|---|
| soda → whole milk | 0.0400 | 0.230 | **0.899** |
| shopping bags → whole milk | 0.0245 | 0.249 | **0.973** |
| bottled beer → whole milk | 0.0205 | 0.254 | **0.993** |

A soda buyer is *less* likely than the average shopper to buy milk, yet the rule passes a
0.20 confidence filter comfortably. Figure `results/fig_conf_lift.png` shows the whole milk
band sitting below everything else.

**2. Ranked by lift, one cluster comes out.** Highest-lift rules:

| rule | support | confidence | lift |
|---|---|---|---|
| citrus fruit, other vegetables → root vegetables | 0.0104 | 0.359 | 3.295 |
| other vegetables, yogurt → whipped/sour cream | 0.0102 | 0.234 | 3.267 |
| other vegetables, tropical fruit → root vegetables | 0.0123 | 0.343 | 3.145 |
| beef → root vegetables | 0.0174 | 0.331 | 3.040 |
| citrus fruit, root vegetables → other vegetables | 0.0104 | 0.586 | 3.030 |

Root vegetables, other vegetables, citrus and tropical fruit, beef, onions, chicken, curd —
one cook-from-scratch cluster, against the soda / beer / snacks / shopping-bags baskets that
are anti-correlated with it.

**3. The single cleanest rule is beef → root vegetables.** 516 baskets contain beef, 171 of
them also contain root vegetables: confidence 0.331 against a baseline of 0.109, lift 3.040.
One item in, one item out, and an ordinary explanation — a roast.

## Tools Insights -- the one number that differs

| | rules | max lift |
|---|---|---|
| Python (mlxtend FP-Growth) | 234 | 3.295 |
| RapidMiner (FP-Growth + Create Association Rules) | 234 | 3.295 |
| KNIME (Association Rule Learner) | **231** | 3.295 |

KNIME's Association Rule Learner produces rules with a **single item on the right-hand side**.
Python and RapidMiner also produce rules whose consequent is a set. Exactly three rules here have
a two-item consequent -- all three predict `other vegetables, whole milk`, from root vegetables
(lift 2.842), whipped/sour cream (2.729) and butter (2.771) -- and 234 - 3 = 231. Everything the
two tools do share matches: the same frequent itemsets, the same supports and confidences, and
the same rule at the top of the lift ranking.

The KNIME pipeline is three nodes: CSV Reader (delimiter `;`, no header row, so each line arrives
as one string) -> Cell Splitter (split on `,`, output as a set) -> Association Rule Learner
(minimum support 0.01, itemset type Free, output association rules, minimum confidence 0.20).

## Answers to the five questions

- *Which rules did you find?* 234 at support 0.01 / confidence 0.20, the strongest by lift
  listed above.
- *Which products are most strongly connected?* Root vegetables with other vegetables and
  citrus/tropical fruit (lift ~3.0–3.3), and beef with root vegetables (3.04).
- *What surprised you?* That the highest-confidence rules are the least informative — three of
  them have lift below 1, so they are actively wrong as predictions.
- *How much did you have to tune support and confidence?* See the sensitivity table: 0.01/0.20
  is the setting where the rule list is long enough to be interesting and short enough to read.
- *Can you make decisions from these rules?* For placement and cross-selling in the fresh aisle,
  yes. Not from the milk rules — milk's base rate is so high that the rules carry no signal,
  which is exactly what lift exposes.

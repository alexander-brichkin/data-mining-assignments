# A2 — Association rules

## Dataset

`data/groceries.csv` — the Groceries basket dataset, one basket per line, comma separated,
no header. **9,835 baskets, 169 distinct items, 43,367 item instances**, basket size 1 / 4.41 /
32 (min / mean / max). Chosen by the group.

Alternatives that were evaluated sit in `data/alternatives/` (UCI Online Retail non-UK subset,
The Bread Basket, a second rendering of Groceries). The Online Retail line of work is kept
under `alternatives/` in `python/` and `rapidminer/` as well.

## Pipeline

```
9,835 baskets  ->  one-hot 9,835 x 169  ->  FP-Growth, min support 0.01  ->  333 frequent itemsets
                                        ->  min confidence 0.20          ->  234 rules
```

Itemset sizes: 88 singletons, 213 pairs, 32 triples. Lift ranges 0.899 ... 3.295.

## What the rules say

1. **Confidence on its own is misleading here.** Whole milk is in 25.6% of all baskets, so
   almost anything predicts it: 70 of the 234 rules have whole milk as consequent and they
   hold the highest confidences in the set. Three of them have **lift below 1** --
   `soda -> whole milk` has confidence 0.230 and lift **0.899**, i.e. a soda buyer is *less*
   likely than average to buy milk. A high-confidence rule can be worse than useless.
2. **Ranking by lift gives one coherent story.** The top of the lift ranking is a single
   cluster -- root vegetables, other vegetables, citrus and tropical fruit, beef, onions,
   chicken, curd. `citrus fruit, root vegetables -> other vegetables` reaches lift 3.030 at
   confidence 0.586. These are cook-from-scratch baskets.
3. **The cleanest single rule is `beef -> root vegetables`**: 516 baskets contain beef, 171 of
   those also contain root vegetables -- confidence 0.331 against a 0.109 baseline, lift 3.040.
   One item in, one item out, and a plain explanation: a roast.

## Reproducing

```bash
cd a2-association-rules
python3 python/analysis.py       # needs pandas + mlxtend; exits non-zero if the numbers drift
python3 python/make_figures.py   # writes the two report figures into results/
```

RapidMiner: `rapidminer/A2_AssociationRules.rmp`, with `groceries.csv` beside it.
The process is a groupmate's, with two fixes: the absolute Windows path was made relative, and
`first_row_as_names` was set to false -- groceries.csv has no header row, so the first basket
was being consumed as column names.

KNIME: `knime/A2_AssociationRules.knwf`. Three nodes --
CSV Reader -> Cell Splitter -> Association Rule Learner. The CSV Reader reads
`knime://knime.workflow/data/groceries.csv`, so the dataset travels inside the archive and the
workflow runs on any machine. Exported after a full run with all three nodes green, and
re-imported from the archive to confirm it loads that way.

## The three implementations agree

| | rules | max lift | rule at max lift |
|---|---|---|---|
| Python (mlxtend FP-Growth) | 234 | 3.295 | citrus fruit, other vegetables -> root vegetables |
| RapidMiner (FP-Growth) | 234 | 3.295 | same |
| KNIME (Association Rule Learner) | **231** | 3.295 | same |

The 231 is not a disagreement. KNIME's Association Rule Learner emits only **single-item
consequents**; Python and RapidMiner also allow a consequent of two or more items. Exactly three
rules in this run have a two-item consequent, and 234 - 3 = 231:

| rule | support | confidence | lift |
|---|---|---|---|
| root vegetables -> other vegetables, whole milk | 0.0232 | 0.213 | 2.842 |
| whipped/sour cream -> other vegetables, whole milk | 0.0146 | 0.204 | 2.729 |
| butter -> other vegetables, whole milk | 0.0115 | 0.207 | 2.771 |

`python/analysis.py` checks both counts, so the reconciliation is tested rather than asserted.

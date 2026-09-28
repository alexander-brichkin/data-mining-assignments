# A1 — Correlations

**Organisation:** S&P Dow Jones Indices — the S&P 500 index and its constituents.
**Dataset:** `constituents-financials.csv`, 503 companies, 14 columns, ODC-PDDL.

## Pipeline

```
503 rows
  → drop rows with missing values in the 10 base numeric columns   → 350
  → keep Market Cap > 0, EBITDA > 0, Price/Sales > 0, Price/Book > 0 → 324
  → derive 5 attributes
  → 15 numeric attributes
  → Pearson correlation matrix
```

Derived attributes:

```
Revenue        = Market Cap / (Price/Sales)
Book Value     = Market Cap / (Price/Book)
EBITDA Margin  = EBITDA / Revenue
Range 52W pct  = (52W High - 52W Low) / 52W Low * 100
Price Pos 52W  = (Price - 52W Low) / (52W High - 52W Low)
```

## Findings

1. **The strongest correlations are empty.** Price ↔ 52-week High = +0.982 is one quantity
   measured twice; Market Cap ↔ EBITDA = +0.958 is company size. A correlation matrix over
   raw financial data is dominated by scale.
2. **Two relationships are real.** Price/Sales ↔ EBITDA Margin = **+0.651** — the market pays
   a higher revenue multiple for a higher operating margin. And Dividend Yield runs against
   price (−0.423), earnings per share (−0.335) and annual range (−0.281): the value/growth split.
3. **Pearson is fragile here.** Price/Earnings correlates with nothing under Pearson (max
   |r| = 0.175); under Spearman the relationships surface — with Dividend Yield −0.048 → **−0.300**,
   with Price +0.029 → +0.237. Eight companies above P/E 100 and one at 522 dominate the
   statistic. A coefficient near zero on an attribute with skewness 8.7 means outliers, not
   independence.

## Cross-check

| | rows out | Price ↔ 52W High | Market Cap ↔ EBITDA | Price/Sales ↔ EBITDA Margin |
|---|---|---|---|---|
| Python | 324 | 0.982 | 0.958 | 0.651 |
| KNIME | 324 | 0.982 | 0.958 | 0.651 |
| RapidMiner | 324 | 0.982 | 0.958 | 0.651 |

The KNIME workflow was exported after a full run with all nine nodes green; the data path
inside it is relative (`data/sp500.csv`, bundled in the archive), so it runs on any machine.
The RapidMiner process ran without an error on first import.

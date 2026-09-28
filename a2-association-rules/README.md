# A2 — Association rules

Dataset choice and cleaning rules: [`notes/DATASET.md`](notes/DATASET.md).

## Data

UCI *Online Retail* (Chen 2015, CC BY 4.0), non-UK customers only:
`data/online_retail_nonUK.csv`, 46,431 rows, the original eight columns, untouched. The
only step done outside the tools is the country subset; all cleaning happens in the
RapidMiner process (and in the same way in the Python reference).

## Pipeline

| Step | RapidMiner operator | Result |
|---|---|---|
| read | Read CSV | 46,431 rows |
| drop cancellations (`InvoiceNo` starting with C), `Quantity` ≤ 0, `UnitPrice` ≤ 0, non-product codes (POST, C2, M, D) | Filter Examples "Clean" | 43,754 rows |
| keep invoice and product | Select Attributes | 2 columns |
| one row per invoice, one column per product | Pivot → Replace Missing (0) → Set Role (id) → Numerical to Binominal | 1,872 × 2,899 |
| frequent itemsets, min support 0.03 | FP-Growth | 185 itemsets |
| rules, min confidence 0.5 | Create Association Rules | 45 rules |

Postage (`POST`) is on 1,112 of the 2,406 non-UK invoices. Left in, it would be the most
frequent "product" and would show up in rules that say nothing about what customers buy.

Support sweep at confidence 0.5: 0.10 → 0 rules, 0.07 → 1, 0.05 → 11, 0.04 → 21,
0.03 → 45, 0.02 → 188.

## Reproduce

```bash
cd a2-association-rules
python3 python/analysis.py     # needs pandas and mlxtend; exits non-zero on drift
```

RapidMiner: File → Import Process → `rapidminer/A2_AssociationRules.rmp` → run.
The CSV path is relative, so `online_retail_nonUK.csv` sits next to the `.rmp`.
Verified in AI Studio 2026.1.1: 185 itemsets and 45 rules, same supports and confidences as
Python.

The process is a rework of the group's first version (built on the arules *Groceries*
basket file); the operator chain from Pivot onwards is the same, the front end is new
because the data is one row per invoice line instead of one row per basket.

# Data mining — correlations and association rules

Each assignment is solved three times over — once in Python as a reference, once in
KNIME and once in RapidMiner (Altair AI Studio) — and the three are required to agree
before anything is written up. The repository holds the data, both tool processes and the
Python reference.

| Assignment | Topic |
|---|---|
| [A1](a1-correlations/) | Correlations, full CRISP-DM cycle |
| [A2](a2-association-rules/) | Association rules |

## Layout

```
a1-correlations/
  data/          sp500.csv — the dataset
  python/        analysis.py — reference pipeline, prints checkpoints and exits non-zero on mismatch
  knime/         .knwf workflow, exported from KNIME 5.12 after a full run
  rapidminer/    .rmp process, exported from AI Studio 2026.1.1 (keep sp500.csv beside it)
  results/       correlation matrices and figures
a2-association-rules/
  data/          Online Retail (full gzip + non-UK subset) plus two fallback basket datasets
  python/        analysis.py — reference pipeline with checkpoints
  rapidminer/    .rmp process (keep online_retail_nonUK.csv beside it)
  results/       rules from the Python reference
  notes/         dataset choice, cleaning rules and the FP-Growth pre-check
```

## Reproducing A1

```bash
cd a1-correlations
python3 python/analysis.py        # needs pandas
```

Expected: 503 raw rows → 350 complete cases → 324 after the positivity filter →
15 attributes. Every checkpoint printed must say `ok`.

KNIME: File → Import KNIME Workflow → pick `knime/*.knwf` → open → Shift+F7.
RapidMiner: File → Import Process → pick `rapidminer/*.rmp` → run. The CSV path in the
Read CSV operator is relative, so `sp500.csv` has to sit next to the `.rmp`; it does.

## Data licences

- `a1-correlations/data/sp500.csv` — S&P 500 constituent financials, ODC-PDDL (public domain).
- `a2-association-rules/data/online_retail_UCI.csv.gz` — Chen, D. (2015), *Online Retail*,
  UCI Machine Learning Repository, <https://doi.org/10.24432/C5BW33>, CC BY 4.0.
- The two files under `a2-association-rules/data/` named `groceries_*` and `breadbasket_*`
  are fallbacks with unclear licensing and are not used in the analysis.

# A2 — Association rules

Dataset choice, cleaning rules and the FP-Growth pre-check live in
[`notes/DATASET.md`](notes/DATASET.md).

Short version: UCI *Online Retail* (541,909 rows, a UK online gift retailer, Dec 2010 –
Dec 2011), restricted to non-UK customers after dropping cancellations, non-positive
quantities and prices, and non-product stock codes — 43,754 rows, 1,872 transactions,
~2,900 products, 37 countries.

```bash
cd data && gunzip -k online_retail_UCI.csv.gz
```

Two fallback datasets sit beside it (`groceries_basket_format.csv`, `breadbasket_DMS.csv`);
both produce weak rules and have unclear licensing, so they are not the plan.

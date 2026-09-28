"""A2 Association Rules — Python reference for the RapidMiner/KNIME processes.

Input : data/online_retail_nonUK.csv  (UCI Online Retail, non-UK customers, raw columns)
Steps : same as the RapidMiner process
  1. drop cancellations      InvoiceNo must be all digits (cancellations start with "C")
  2. drop returns / errors   Quantity > 0, UnitPrice > 0
  3. products only           StockCode = 5 digits + optional letters (removes POST, C2, M, D)
  4. basket matrix           one row per invoice, one binary column per Description
  5. FP-Growth               min support 0.03
  6. association rules       min confidence 0.5
Prints checkpoints and exits non-zero if any drifts.
"""
import sys
from pathlib import Path
import pandas as pd
from mlxtend.frequent_patterns import fpgrowth, association_rules

MIN_SUPPORT, MIN_CONF = 0.03, 0.5
here = Path(__file__).resolve().parent.parent
df = pd.read_csv(here / "data" / "online_retail_nonUK.csv", dtype=str, keep_default_na=False)
raw = len(df)
df = df[df.InvoiceNo.str.fullmatch(r"[0-9]+")]
df = df[(df.Quantity.astype(int) > 0) & (df.UnitPrice.astype(float) > 0)]
df = df[df.StockCode.str.fullmatch(r"[0-9]{5}[A-Za-z]*")]
clean = len(df)

basket = pd.crosstab(df.InvoiceNo, df.Description).gt(0)
itemsets = fpgrowth(basket, min_support=MIN_SUPPORT, use_colnames=True)
rules = association_rules(itemsets, metric="confidence", min_threshold=MIN_CONF)

print(f"raw rows            {raw}")
print(f"clean rows          {clean}")
print(f"transactions        {basket.shape[0]}")
print(f"distinct products   {basket.shape[1]}")
print(f"frequent itemsets   {len(itemsets)}   (support >= {MIN_SUPPORT})")
print(f"rules               {len(rules)}   (confidence >= {MIN_CONF})")
print("\nsupport sweep (confidence 0.5):")
for s in (0.10, 0.07, 0.05, 0.04, 0.03, 0.02):
    fi = fpgrowth(basket, min_support=s, use_colnames=True)
    r = association_rules(fi, metric="confidence", min_threshold=MIN_CONF) if len(fi) else []
    print(f"  support {s:.2f}: {len(fi):4d} itemsets, {len(r):4d} rules")
print("\ntop 10 rules by lift:")
for _, x in rules.sort_values(["lift", "confidence"], ascending=False).head(10).iterrows():
    a = " + ".join(sorted(i.strip() for i in x.antecedents)); c = " + ".join(sorted(i.strip() for i in x.consequents))
    print(f"  {a}  ->  {c}   sup {x.support:.3f}  conf {x.confidence:.3f}  lift {x.lift:.2f}")
(here / "results").mkdir(exist_ok=True)
rules.assign(antecedents=rules.antecedents.map(lambda s: " + ".join(sorted(i.strip() for i in s))),
             consequents=rules.consequents.map(lambda s: " + ".join(sorted(i.strip() for i in s)))) \
     [["antecedents", "consequents", "support", "confidence", "lift"]] \
     .sort_values("lift", ascending=False).round(4).to_csv(here / "results" / "rules_python.csv", index=False)

checks = [("raw rows", raw, 46431), ("clean rows", clean, 43754),
          ("transactions", basket.shape[0], 1872), ("distinct products", basket.shape[1], 2899),
          ("frequent itemsets", len(itemsets), 185), ("rules", len(rules), 45)]
bad = [n for n, got, want in checks if got != want]
for n, got, want in checks:
    print(f"check {n}: {got} == {want}  {'ok' if got == want else 'MISMATCH'}")
sys.exit(1 if bad else 0)

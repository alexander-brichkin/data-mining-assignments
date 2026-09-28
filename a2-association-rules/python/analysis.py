"""
Assignment 2 -- reference implementation of the association-rule pipeline.

This is the Python reference that the RapidMiner process and the KNIME workflow
were checked against. All three mine the same 9,835 baskets at min support 0.01
and min confidence 0.20 and return the same 234 rules.

Usage (from the a2-association-rules directory):
    python3 python/analysis.py
"""
from collections import Counter
from pathlib import Path

import pandas as pd
from mlxtend.frequent_patterns import association_rules, fpgrowth
from mlxtend.preprocessing import TransactionEncoder

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "groceries.csv"
OUT = ROOT / "results"

MIN_SUPPORT = 0.01
MIN_CONFIDENCE = 0.20


def load_baskets():
    """One basket per line, comma separated, variable length, no header row."""
    baskets = []
    for line in DATA.read_text(encoding="utf-8").splitlines():
        items = [i.strip() for i in line.split(",") if i.strip()]
        if items:
            baskets.append(items)
    return baskets


def main():
    baskets = load_baskets()
    counts = Counter(i for b in baskets for i in b)
    sizes = [len(b) for b in baskets]

    print(f"baskets                  : {len(baskets)}")
    print(f"distinct items           : {len(counts)}")
    print(f"item instances           : {sum(counts.values())}")
    print(f"basket size min/mean/max : {min(sizes)} / {sum(sizes)/len(sizes):.2f} / {max(sizes)}")
    top_item, top_n = counts.most_common(1)[0]
    print(f"most frequent item       : {top_item} ({top_n / len(baskets):.4f} of baskets)")

    encoder = TransactionEncoder()
    matrix = pd.DataFrame(encoder.fit(baskets).transform(baskets), columns=encoder.columns_)
    print(f"one-hot matrix           : {matrix.shape[0]} x {matrix.shape[1]}")

    itemsets = fpgrowth(matrix, min_support=MIN_SUPPORT, use_colnames=True)
    rules = association_rules(itemsets, metric="confidence", min_threshold=MIN_CONFIDENCE)
    rules["antecedent"] = rules.antecedents.map(lambda s: ", ".join(sorted(s)))
    rules["consequent"] = rules.consequents.map(lambda s: ", ".join(sorted(s)))

    sizes_found = itemsets.itemsets.map(len).value_counts().sort_index().to_dict()
    print(f"frequent itemsets        : {len(itemsets)} (sizes {sizes_found})")
    print(f"rules                    : {len(rules)}")
    print(f"lift range               : {rules.lift.min():.3f} .. {rules.lift.max():.3f}")

    OUT.mkdir(exist_ok=True)
    cols = ["antecedent", "consequent", "support", "confidence", "lift"]
    rules.sort_values("lift", ascending=False).to_csv(
        OUT / "rules_reference.csv", index=False, columns=cols)

    single = int((rules.consequents.map(len) == 1).sum())
    multi = len(rules) - single

    checks = [
        ("baskets", len(baskets), 9835),
        ("distinct items", len(counts), 169),
        ("frequent itemsets", len(itemsets), 333),
        ("rules", len(rules), 234),
        ("single-item consequent", single, 231),
        ("multi-item consequent", multi, 3),
    ]
    print("\ncheckpoints (actual vs expected):")
    ok = True
    for label, actual, expected in checks:
        flag = "ok" if actual == expected else "MISMATCH"
        ok &= flag == "ok"
        print(f"  {label:20s} {actual:>6} vs {expected:>6}  {flag}")

    named = [("beef", "root vegetables", 0.331, 3.040),
             ("soda", "whole milk", 0.230, 0.899),
             ("citrus fruit, root vegetables", "other vegetables", 0.586, 3.030)]
    print("\nnamed rules (confidence / lift):")
    for a, c, e_conf, e_lift in named:
        r = rules[(rules.antecedent == a) & (rules.consequent == c)].iloc[0]
        flag = "ok" if abs(r.confidence - e_conf) < 0.001 and abs(r.lift - e_lift) < 0.001 else "MISMATCH"
        ok &= flag == "ok"
        print(f"  {a} -> {c}: {r.confidence:.3f} / {r.lift:.3f}  {flag}")

    print("\nRapidMiner reports all 234 rules; KNIME's Association Rule Learner emits only")
    print("single-item consequents, so it reports 231. The 3 it leaves out are:")
    for _, r in rules[rules.consequents.map(len) > 1].iterrows():
        print(f"  {r.antecedent} -> {r.consequent}: "
              f"support {r.support:.4f}, confidence {r.confidence:.3f}, lift {r.lift:.3f}")

    print("\nwrote", OUT / "rules_reference.csv")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()

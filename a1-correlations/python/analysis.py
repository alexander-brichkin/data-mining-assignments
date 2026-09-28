"""
Assignment 1 -- reference implementation of the correlation pipeline.

This is the Python reference that the KNIME workflow and the RapidMiner process
were checked against. All three produce the same 324 x 15 table and the same
correlation coefficients to three decimals.

Usage (from the a1-correlations directory):
    python3 python/analysis.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "sp500.csv"
OUT = ROOT / "results"

BASE = [
    "Price", "Price/Earnings", "Dividend Yield", "Earnings/Share",
    "52 Week Low", "52 Week High", "Market Cap", "EBITDA",
    "Price/Sales", "Price/Book",
]
POSITIVE = ["Market Cap", "EBITDA", "Price/Sales", "Price/Book"]
DERIVED = ["Revenue", "Book Value", "EBITDA Margin", "Range 52W pct", "Price Pos 52W"]


def build() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    print(f"raw rows                 : {len(df)}")

    df = df.dropna(subset=BASE)
    print(f"after complete-case drop : {len(df)}")

    df = df[(df[POSITIVE] > 0).all(axis=1)].copy()
    print(f"after positivity filter  : {len(df)}")

    df["Revenue"] = df["Market Cap"] / df["Price/Sales"]
    df["Book Value"] = df["Market Cap"] / df["Price/Book"]
    df["EBITDA Margin"] = df["EBITDA"] / df["Revenue"]
    df["Range 52W pct"] = (df["52 Week High"] - df["52 Week Low"]) / df["52 Week Low"] * 100
    df["Price Pos 52W"] = (df["Price"] - df["52 Week Low"]) / (df["52 Week High"] - df["52 Week Low"])

    out = df[BASE + DERIVED]
    print(f"attributes into matrix   : {out.shape[1]}")
    return out


def main() -> None:
    table = build()
    OUT.mkdir(exist_ok=True)

    pearson = table.corr(method="pearson").round(6)
    spearman = table.corr(method="spearman").round(6)
    pearson.to_csv(OUT / "correlation_matrix_pearson.csv")
    spearman.to_csv(OUT / "correlation_matrix_spearman.csv")

    checks = [
        ("Price", "52 Week High", 0.982),
        ("Market Cap", "EBITDA", 0.958),
        ("Price/Sales", "EBITDA Margin", 0.651),
        ("Dividend Yield", "Price", -0.423),
    ]
    print("\ncheckpoints (expected -> actual):")
    ok = True
    for a, b, expected in checks:
        actual = round(float(pearson.loc[a, b]), 3)
        flag = "ok" if abs(actual - expected) < 0.0005 else "MISMATCH"
        ok &= flag == "ok"
        print(f"  {a} ~ {b}: {expected:+.3f} -> {actual:+.3f}  {flag}")

    print("\nPearson vs Spearman, where the rank version disagrees:")
    for a, b in [("Price/Earnings", "Dividend Yield"), ("Price/Earnings", "Price"),
                 ("Price/Book", "Market Cap")]:
        print(f"  {a} ~ {b}: {pearson.loc[a, b]:+.3f} -> {spearman.loc[a, b]:+.3f}")

    print("\nwrote", OUT / "correlation_matrix_pearson.csv")
    print("wrote", OUT / "correlation_matrix_spearman.csv")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()

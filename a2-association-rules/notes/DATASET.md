# A2 Association Rules — dataset

## Chosen: UCI Online Retail
- File: `online_retail_UCI.csv` (541,909 rows, 8 columns)
- Source: Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33
- Licence: CC BY 4.0 (redistribution allowed with attribution)
- Content: all transactions of a UK-based online gift retailer (many wholesale customers), 2010-12-01 to 2011-12-09.
  25,900 invoices, 4,372 customers, 38 countries.
- Columns: InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country
- Downloaded as CSV from the databricks/Spark-The-Definitive-Guide mirror (UCI host blocked from this network);
  row count, date range, invoice/customer/country counts match the UCI description.

## Proposed scope: non-UK customers
Cleaning: drop cancellations (InvoiceNo starting with "C"), Quantity <= 0, UnitPrice <= 0,
missing Description, and non-product codes (POST, DOT, M, BANK CHARGES ... — keep StockCode starting with 5 digits).
Non-UK subset: 43,754 rows, 1,872 invoices (transactions), ~2,900 distinct products, 37 countries.
Python check (FP-Growth, min confidence 0.5): support 0.05 -> 11 rules, 0.04 -> 21, 0.03 -> 45.
Strongest rules: matching colour/design variants bought together (red spotty paper cups/plates/napkins, lift ~16;
Dolly Girl / Spaceboy children's cutlery, lift ~15). Cross-category: Spaceboy lunch box -> Woodland snack boxes (lift 3.2).
For RapidMiner/KNIME: pivot invoice x product to binominal; drop rare products first to keep the matrix narrow.

## Backups in `alternatives/`
- `groceries_basket_format.csv` — 9,835 grocery baskets, 169 items, one basket per line (no header, variable length).
  From R package arules (Hahsler et al.). Rules have low lift (max ~3), "whole milk" everywhere. Licence of the data unclear.
- `breadbasket_DMS.csv` — "The Bread Basket" bakery, Edinburgh, 21,293 rows / 9,465 transactions, 2016-10 to 2017-04.
  Almost all rules end in Coffee, lift <= 1.5. Kaggle origin, licence unclear.

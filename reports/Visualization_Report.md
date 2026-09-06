# Visualization Report — Online Retail Dataset
**CodeAlpha Data Analytics Internship — Task 3: Data Visualization**
**Author:** Ali Rashid (Chaudhary)

---

## 1. Project Overview

This project transforms the real UCI Online Retail transactional dataset
into a set of clear, meaningful, and interactive visualizations, each
paired with a written interpretation grounded in the actual computed
statistics — no figure in this report is estimated or fabricated. It
reuses the same real dataset as Task 2 (EDA) but is built and documented
as a clean, standalone visualization project.

## 2. Dataset Description

| Field | Detail |
|---|---|
| Name | Online Retail Dataset |
| Source | UCI Machine Learning Repository (`archive.ics.uci.edu/dataset/352/online+retail`) |
| Period | 1 December 2010 – 9 December 2011 |
| Raw size | 541,909 rows × 8 columns |
| Columns | InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country |

## 3. Data Preparation

| Step | Extent | Action |
|---|---|---|
| Exact duplicate rows | 5,268 rows (0.97% of raw data) | Dropped (logging/export artifact) |
| Missing `Description` | 1,454 rows | Filled with `"UNKNOWN ITEM"` |
| Missing `CustomerID` | 135,037 rows (24.92%) | Flagged (`HasCustomerID`); kept for all non-customer-level charts |
| Cancelled invoices (`InvoiceNo` starts with "C") | 9,251 rows (1.72%) | Flagged (`IsCancelled`); analyzed separately (Section 5.8/Chart 08) |
| Non-positive `UnitPrice` | 2,512 rows | Excluded from `IsValidSale` revenue view |
| Negative `Quantity` | 10,587 rows | Excluded from `IsValidSale` revenue view unless part of a flagged cancellation |
| Revenue column | — | `Revenue = Quantity × UnitPrice` |
| Date parts extracted | — | `Year`, `Month`, `Day`, `DayOfWeek`, `Hour`, `InvoiceMonth` |
| Customer-level metrics | 4,338 customers | `Orders`, `Revenue`, `AvgOrderValue`, `Recency` computed per `CustomerID` |

No row was deleted without a documented reason; only exact duplicates were removed unconditionally. All other exclusions are implemented as boolean flag columns (`IsCancelled`, `HasCustomerID`, `IsValidSale`) in the saved processed dataset, preserving full transparency and reversibility.

## 4. Visualization Methodology

- **Static charts (matplotlib/seaborn):** used for the 10 required visualizations and 2 advanced visualizations, chosen per chart type appropriate to the data (bar charts for categorical comparisons, line charts for time trends, histograms for distributions, scatter for bivariate relationships, heatmaps for two-dimensional categorical/numeric relationships).
- **Interactive charts (Plotly):** two interactive visualizations (revenue by country, monthly revenue trend) were built with Plotly Express and exported as standalone, self-contained HTML files for hover/zoom exploration.
- **Dashboard:** a single static HTML dashboard combines 5 KPIs and 4 of the strongest charts using Plotly subplots; see Section 8 of the README for the design rationale (static file vs. running server).
- Every chart uses a percentile cap (typically 99th percentile) on extreme values purely for **visual readability** — the underlying statistics reported in text are computed from the full, uncapped data.

## 5. Major Findings

1. **Revenue is geographically concentrated:** the United Kingdom accounts for **84.59%** of total revenue (£10,642,110.80 total across 19,960 valid invoices, averaging **£533.17** per order).
2. **November 2011 is the clear seasonal peak** (£1,503,866.78) — consistent with pre-Christmas gift buying; the December figure reflects the dataset's cutoff date (9 Dec 2011), not a genuine decline.
3. **No Saturday trading occurs anywhere in the dataset** — a genuine operational pattern, not a data error.
4. **Thursday is the highest-revenue day of the week**; trading activity peaks at **10:00** and is minimal outside standard UK business hours.
5. **Invoice-level revenue is extremely right-skewed** (skew ≈ 51.08) — a small number of large invoices dominate total value; the median is a far more representative "typical order" measure than the mean.
6. **Quantity and UnitPrice are practically uncorrelated** (Pearson r = -0.0038, p = 0.0061) — statistically significant only due to sample size, not practically meaningful.
7. **Cancellation rate (1.72% overall) varies meaningfully by country** — Germany (4.78%) and EIRE (3.68%) cancel notably more often than the UK (1.60%) or Netherlands (0.34%).
8. **Customer value is highly unequal:** median customer revenue is £668.57 (mean £2,048.69, max £280,206.02) across a median of 2 orders (mean 4.27, max 209) — a small segment of high-value customers drives disproportionate revenue.
9. **Top-revenue products only partially overlap with top-quantity products** (5 of 10 in common) — some high "revenue" items are non-product administrative charges (e.g. postage) rather than genuine merchandise.
10. **RFM metrics show a customer base of mostly occasional buyers** alongside a smaller frequent, high-spend segment (75th-percentile order count is only 5, but the maximum is 209).

## 6. Business Insights

- Heavy UK revenue concentration is a **single-market dependency risk**; the next-largest markets (Netherlands, EIRE, Germany, France) represent a real but currently under-leveraged diversification opportunity.
- The sharp November peak means **inventory and staffing should be planned around a September–November ramp-up**, and the partial-December dip must not be mistaken for a genuine off-season in future forecasting.
- **Germany's disproportionate cancellation rate** is a concrete, actionable signal for investigating shipping cost, product fit, or checkout experience in that specific market.
- The **highly unequal customer value distribution** supports building a dedicated retention or account-management track for the small set of high-Monetary, high-Frequency customers identified in the RFM view.
- **Separating non-product charges (postage, adjustments) from merchandise revenue** would make "top product" reporting more actionable for inventory and marketing decisions.

## 7. Limitations

- The dataset covers a single retailer over roughly one year; seasonal and country-level patterns may not generalize beyond this business or period.
- ~24.92% of transaction rows have no `CustomerID`, so customer-level (Section 5.9, 5.10) analysis is necessarily based on the remaining ~75% of identifiable customers only.
- Distinguishing genuine merchandise from administrative line items (e.g., "DOTCOM POSTAGE") required manual judgment based on `Description` text, which introduces a small amount of interpretive (not statistical) uncertainty into product-level rankings.
- The interactive Plotly charts and dashboard require a modern browser with JavaScript enabled (loaded via CDN); they will not render offline without internet access to fetch `plotly.js`.

## 8. Conclusion

This visualization project delivers all 10 required charts, 2 advanced visualizations, and 2 interactive Plotly visualizations, each tied to a specific analytical question and interpreted using only statistics computed directly from the real dataset. Combined with the standalone KPI dashboard, it provides a complete, verifiable, and professional visual account of the Online Retail dataset suitable for the CodeAlpha Task 3 submission.

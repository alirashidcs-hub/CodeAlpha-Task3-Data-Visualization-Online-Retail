# CodeAlpha Task 3 — Data Visualization
### Online Retail Dataset (UCI Machine Learning Repository)

**Author:** Ali Rashid (Chaudhary) — BSCS, University of Engineering and Technology (UET) Taxila
**Internship:** CodeAlpha Data Analytics Internship
**Task:** Task 3 — Data Visualization

---

## Project Overview

This project transforms the real, 541,909-row **UCI Online Retail Dataset**
into a complete set of professional, meaningful visualizations: 10 required
charts, 2 advanced visualizations, 2 interactive Plotly visualizations, and
a standalone KPI dashboard — each grounded in statistics computed directly
from the actual data. It builds on the same dataset used in **Task 2
(Exploratory Data Analysis)** but is packaged as a clean, independent,
visualization-focused deliverable that does not require any Task 2 files
to run.

## Objectives

- Prepare the raw dataset with fully documented, non-destructive transformations.
- Produce at least 10 required visualizations, each answering a specific analytical question.
- Produce at least 2 advanced visualizations (heatmaps combining multiple variables).
- Produce at least 1 interactive visualization using Plotly (this project includes 2).
- Summarize project-level KPIs in a professional dashboard.
- Interpret every major visualization in plain, evidence-based language.
- Package everything as a clean, GitHub-ready, reproducible project.

## Dataset

| Field | Detail |
|---|---|
| **Name** | Online Retail Dataset |
| **Source** | [UCI Machine Learning Repository, ID 352](https://archive.ics.uci.edu/dataset/352/online+retail) (donor: Dr. Daqing Chen, London South Bank University) |
| **Size** | 541,909 rows × 8 columns (raw) |
| **Period** | 1 December 2010 – 9 December 2011 |
| **License** | CC BY 4.0 |
| **Columns** | `InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country` |

## Technologies Used

- Python 3.12
- pandas, numpy — data preparation
- matplotlib, seaborn — static visualizations
- plotly — interactive visualizations and dashboard
- scipy.stats — supporting correlation statistic
- Jupyter Notebook — analysis narrative and reproducible workflow
- openpyxl — Excel file I/O

## Project Structure

```
CodeAlpha_Task3_Data_Visualization_Online_Retail/
│
├── data/
│   ├── raw/
│   │   └── README.md              # Dataset download instructions
│   └── processed/
│       └── README.md              # Notes on the generated processed file
│
├── notebooks/
│   └── Data_Visualization.ipynb   # Full, executed, narrated notebook
│
├── src/
│   ├── visualization.py           # Main pipeline: load, prepare, visualize, save insights
│   └── build_dashboard.py         # Builds the standalone KPI dashboard HTML
│
├── visualizations/
│   ├── 01_revenue_by_country.png
│   ├── 02_top_products.png
│   ├── 03_monthly_revenue.png
│   ├── 04_daily_revenue.png
│   ├── 05_hourly_revenue.png
│   ├── 06_transaction_distribution.png
│   ├── 07_quantity_price_relationship.png
│   ├── 08_cancellation_analysis.png
│   ├── 09_customer_analysis.png
│   ├── 10_rfm_analysis.png
│   ├── 11_country_month_heatmap.png     # Advanced
│   ├── 12_correlation_heatmap.png       # Advanced
│   ├── interactive/
│   │   ├── interactive_revenue_by_country.html
│   │   └── interactive_monthly_revenue_trend.html
│   └── README.md                  # Chart index with analytical questions
│
├── dashboard/
│   └── dashboard.html             # Standalone KPI + chart dashboard
│
├── reports/
│   ├── Visualization_Report.md    # Full written findings report
│   └── key_insights.json          # Machine-readable export of every computed statistic
│
├── README.md
├── requirements.txt
└── .gitignore
```

## Installation

```bash
git clone <your-repo-url>
cd CodeAlpha_Task3_Data_Visualization_Online_Retail
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Dataset Download Instructions

> `data/raw/OnlineRetail.xlsx` is **not committed to GitHub** (excluded via
> `.gitignore`) because it is ~23.7 MB — too large for a lightweight
> portfolio repository.

Download it from the UCI Machine Learning Repository:
https://archive.ics.uci.edu/dataset/352/online+retail

Place the downloaded file at `data/raw/OnlineRetail.xlsx` before running anything below.

## How to Run the Python Script

```bash
python src/visualization.py
```

This will:
1. Load and prepare the raw dataset (cleaning steps documented in Section "Data Preparation" below).
2. Generate all 12 static visualizations into `visualizations/`.
3. Generate 2 interactive Plotly visualizations into `visualizations/interactive/`.
4. Save the prepared dataset to `data/processed/online_retail_prepared.csv`.
5. Save structured findings to `reports/key_insights.json`.
6. Print progress messages throughout and exit with code `0` on success.

## How to Run the Notebook

```bash
jupyter notebook notebooks/Data_Visualization.ipynb
```

The notebook is self-contained — it loads directly from `data/raw/OnlineRetail.xlsx` and re-derives everything shown in this README. It has already been executed end-to-end with **zero errors**; running it again will simply regenerate identical output.

## How to Launch the Dashboard

After running `src/visualization.py` at least once (so `reports/key_insights.json` and `data/processed/` exist), build the dashboard:

```bash
python src/build_dashboard.py
```

Then open it directly — no server required:

```bash
# Simplest: just open the file in any browser
open dashboard/dashboard.html        # macOS
xdg-open dashboard/dashboard.html    # Linux
start dashboard/dashboard.html       # Windows

# Or serve it locally:
python -m http.server --directory dashboard 8000
# then visit http://localhost:8000/dashboard.html
```

**Design decision:** a static, self-contained HTML dashboard (built with Plotly) was used instead of a running Dash/Streamlit server. This requires zero server setup, works directly from a downloaded ZIP with no extra `pip install dash` step, and still provides full interactive hover/zoom via Plotly.js — appropriate for a portfolio deliverable that needs to be reliably runnable on any reviewer's machine without a live server.

## Visualization Gallery

See [`visualizations/README.md`](visualizations/README.md) for the full index mapping each chart to the analytical question it answers. Summary:

**Required (10):** revenue by country · top products · monthly revenue trend · daily/weekly revenue pattern · hourly transaction pattern · transaction/revenue distribution · quantity vs. unit price · cancellation analysis · customer analysis · RFM analysis

**Advanced (2):** country × month revenue heatmap · correlation heatmap

**Interactive (2, Plotly):** interactive revenue by country · interactive monthly revenue trend

## Key Findings

- The UK generates **84.59%** of total revenue (£10,642,110.80 across 19,960 valid invoices from 4,338 identified customers), for an average order value of **£533.17**.
- **November 2011** is the clear seasonal peak (£1,503,866.78); no Saturday trading occurs at all.
- Trading activity peaks at **10:00** and Thursday is the highest-revenue weekday.
- Cancellation rate is **1.72% overall** but varies sharply by country — Germany (4.78%) and EIRE (3.68%) vs. UK (1.60%) and Netherlands (0.34%).
- Customer value is highly unequal: median customer revenue is £668.57 vs. a mean of £2,048.69 (max £280,206.02).
- Quantity and UnitPrice are practically uncorrelated (r = -0.0038).

Full findings and business insights are in [`reports/Visualization_Report.md`](reports/Visualization_Report.md).

## Limitations

- Single retailer, ~1-year window — patterns may not generalize to other businesses or periods.
- ~24.92% of rows lack a `CustomerID`, so customer-level charts reflect only the identifiable ~75% of transactions.
- Distinguishing genuine merchandise from administrative charges (e.g., postage) in "top products" required manual judgment based on product descriptions.
- The interactive charts and dashboard load `plotly.js` from a CDN and require internet access and a modern browser to render.

## Future Improvements

- Add a live Dash or Streamlit app for real-time filtering (by country/date range) if server-based interactivity becomes a requirement.
- Extend customer segmentation into explicit RFM tiers (e.g., via k-means) for a marketing-ready deliverable.
- Incorporate the newer "Online Retail II" dataset for a longer seasonal baseline.
- Add category-level tagging (via `StockCode`/`Description` parsing) for category-level trend visualizations.

## Author

**Ali Rashid (Chaudhary)** — BSCS Computer Science student, University of Engineering and Technology (UET) Taxila, Pakistan. AI and full-stack developer.

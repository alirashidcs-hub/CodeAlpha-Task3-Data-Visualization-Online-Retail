"""
CodeAlpha Task 3 - Data Visualization
Online Retail Dataset (UCI Machine Learning Repository)

Loads the real Online Retail dataset, performs the documented data
preparation steps, generates 10 required visualizations plus 2 advanced
visualizations and 2 interactive Plotly visualizations, and writes
structured key insights to reports/key_insights.json.

Run from the project root:
    python src/visualization.py

Author: Ali Rashid (Chaudhary)
"""

import json
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110
plt.rcParams["font.size"] = 11

# ---------------------------------------------------------------------------
# Paths (relative to project root; script works when run as `python src/visualization.py`)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "OnlineRetail.xlsx"
PROCESSED_PATH = ROOT / "data" / "processed" / "online_retail_prepared.csv"
VIZ_DIR = ROOT / "visualizations"
INTERACTIVE_DIR = VIZ_DIR / "interactive"
REPORTS_DIR = ROOT / "reports"
INSIGHTS_PATH = REPORTS_DIR / "key_insights.json"

for d in (VIZ_DIR, INTERACTIVE_DIR, REPORTS_DIR, PROCESSED_PATH.parent):
    d.mkdir(parents=True, exist_ok=True)

insights = {}


def log(msg):
    print(f"[Task3] {msg}")


def savefig(fig_or_name, name=None):
    """Save current matplotlib figure to visualizations/<name>."""
    filename = name if name is not None else fig_or_name
    path = VIZ_DIR / filename
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    log(f"Saved visualization -> {path.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------------------------

def load_data():
    log(f"Loading dataset from {RAW_PATH.relative_to(ROOT)} ...")
    if not RAW_PATH.exists():
        log("ERROR: raw dataset not found. See data/raw/README.md for download instructions.")
        sys.exit(1)
    df = pd.read_excel(RAW_PATH)
    log(f"Loaded {len(df):,} rows x {df.shape[1]} columns.")
    return df


# ---------------------------------------------------------------------------
# 2. DATA PREPARATION
# ---------------------------------------------------------------------------

def prepare_data(df):
    """
    Documented transformations (none destroy information without a flag):

    1. Flag cancellations (InvoiceNo starting with 'C') BEFORE any filtering.
    2. Drop exact duplicate rows (logging/export artifact - adds no information).
    3. Fill missing Description with 'UNKNOWN ITEM' (small, ~0.27% of rows).
    4. Flag rows missing CustomerID rather than dropping them - these are
       genuine guest-checkout sales and are only excluded from customer-level
       metrics, never from revenue/product/time visualizations.
    5. Flag valid sales (UnitPrice > 0, Quantity > 0, not cancelled) - used
       for revenue-based charts so administrative/return entries don't
       distort them. The full flagged dataset is still saved for transparency.
    6. Correct dtypes (InvoiceNo/StockCode/Country as string, CustomerID as
       nullable Int64, InvoiceDate as datetime).
    7. Create Revenue = Quantity * UnitPrice.
    8. Extract Year, Month, Day, DayOfWeek, Hour from InvoiceDate.
    9. Build customer-level metrics (orders, revenue, average order value)
       for customers with a valid CustomerID.
    """
    log("Preparing data (cleaning + feature engineering) ...")
    d = df.copy()
    before = len(d)

    # 1. Cancellation flag
    d["InvoiceNo"] = d["InvoiceNo"].astype(str)
    d["IsCancelled"] = d["InvoiceNo"].str.startswith("C")

    # 2. Duplicates
    dupes = int(d.duplicated().sum())
    d = d.drop_duplicates()
    log(f"Removed {dupes:,} exact duplicate rows ({dupes/before*100:.2f}% of raw data).")

    # 3. Missing Description
    n_missing_desc = int(d["Description"].isnull().sum())
    d["Description"] = d["Description"].fillna("UNKNOWN ITEM")

    # 4. Missing CustomerID flag
    n_missing_cust = int(d["CustomerID"].isnull().sum())
    d["HasCustomerID"] = d["CustomerID"].notnull()

    # 5. Valid sale flag (excludes cancellations and non-positive price/qty)
    d["IsValidSale"] = (d["UnitPrice"] > 0) & (d["Quantity"] > 0) & (~d["IsCancelled"])
    n_invalid_price = int((d["UnitPrice"] <= 0).sum())
    n_negative_qty = int((d["Quantity"] < 0).sum())

    # 6. Dtypes
    d["StockCode"] = d["StockCode"].astype(str)
    d["CustomerID"] = d["CustomerID"].astype("Int64")
    d["Country"] = d["Country"].astype(str).str.strip()
    d["InvoiceDate"] = pd.to_datetime(d["InvoiceDate"])

    # 7. Revenue
    d["Revenue"] = d["Quantity"] * d["UnitPrice"]

    # 8. Date parts
    d["Year"] = d["InvoiceDate"].dt.year
    d["Month"] = d["InvoiceDate"].dt.month
    d["Day"] = d["InvoiceDate"].dt.day
    d["DayOfWeek"] = d["InvoiceDate"].dt.day_name()
    d["Hour"] = d["InvoiceDate"].dt.hour
    d["InvoiceMonth"] = d["InvoiceDate"].dt.to_period("M").astype(str)

    after = len(d)
    summary = {
        "rows_before": before,
        "rows_after_dedup": after,
        "duplicate_rows_removed": dupes,
        "missing_description_filled": n_missing_desc,
        "missing_customer_id_rows": n_missing_cust,
        "missing_customer_id_pct": round(n_missing_cust / before * 100, 2),
        "cancelled_rows": int(d["IsCancelled"].sum()),
        "cancelled_pct": round(int(d["IsCancelled"].sum()) / after * 100, 2),
        "non_positive_price_rows": n_invalid_price,
        "negative_quantity_rows": n_negative_qty,
        "valid_sale_rows": int(d["IsValidSale"].sum()),
    }
    insights["data_preparation"] = summary
    log("Data preparation summary: " + json.dumps(summary))
    return d


def build_customer_metrics(d):
    """Customer-level metrics: number of orders, total revenue, average order value."""
    sales = d[d["IsValidSale"] & d["HasCustomerID"]]
    snapshot_date = sales["InvoiceDate"].max() + pd.Timedelta(days=1)

    cust = sales.groupby("CustomerID").agg(
        Orders=("InvoiceNo", "nunique"),
        Revenue=("Revenue", "sum"),
        LastPurchase=("InvoiceDate", "max"),
    ).reset_index()
    cust["AvgOrderValue"] = (cust["Revenue"] / cust["Orders"]).round(2)
    cust["Recency"] = (snapshot_date - cust["LastPurchase"]).dt.days

    return cust


# ---------------------------------------------------------------------------
# 3. REQUIRED VISUALIZATIONS (1-10)
# ---------------------------------------------------------------------------

def viz_01_revenue_by_country(sales):
    rev = sales.groupby("Country")["Revenue"].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(9, 5.5))
    sns.barplot(x=rev.values, y=rev.index, hue=rev.index, palette="mako", legend=False)
    plt.title("Total Revenue by Country (Top 10)", fontsize=14, fontweight="bold")
    plt.xlabel("Total Revenue (£)")
    plt.ylabel("Country")
    plt.gca().xaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    savefig("01_revenue_by_country.png")

    total_rev = sales["Revenue"].sum()
    insights["revenue_by_country_top10"] = rev.round(2).to_dict()
    insights["top_country"] = rev.index[0]
    insights["top_country_revenue"] = round(float(rev.iloc[0]), 2)
    insights["top_country_share_pct"] = round(float(rev.iloc[0] / total_rev * 100), 2)
    return rev


def viz_02_top_products(sales):
    top_rev = sales.groupby("Description")["Revenue"].sum().sort_values(ascending=False).head(10)
    top_qty = sales.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head(10)

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    sns.barplot(x=top_rev.values, y=[t[:30] for t in top_rev.index], ax=axes[0],
                hue=top_rev.index, palette="crest", legend=False)
    axes[0].set_title("Top 10 Products by Revenue", fontsize=13, fontweight="bold")
    axes[0].set_xlabel("Revenue (£)")
    axes[0].xaxis.set_major_locator(mticker.MaxNLocator(nbins=5))
    axes[0].xaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))

    sns.barplot(x=top_qty.values, y=[t[:30] for t in top_qty.index], ax=axes[1],
                hue=top_qty.index, palette="flare", legend=False)
    axes[1].set_title("Top 10 Products by Quantity Sold", fontsize=13, fontweight="bold")
    axes[1].set_xlabel("Units Sold")
    savefig("02_top_products.png")

    insights["top_products_by_revenue"] = top_rev.round(2).to_dict()
    insights["top_products_by_quantity"] = top_qty.to_dict()
    insights["top_products_overlap_count"] = len(set(top_rev.index) & set(top_qty.index))
    return top_rev, top_qty


def viz_03_monthly_revenue(sales):
    monthly = sales.groupby("InvoiceMonth")["Revenue"].sum().sort_index()
    plt.figure(figsize=(11, 5.5))
    monthly.plot(kind="line", marker="o", color="#C44E52", linewidth=2)
    plt.title("Monthly Revenue Trend (Dec 2010 - Dec 2011)", fontsize=14, fontweight="bold")
    plt.xlabel("Month")
    plt.ylabel("Revenue (£)")
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    plt.grid(axis="y", alpha=0.4)
    savefig("03_monthly_revenue.png")

    insights["monthly_revenue"] = monthly.round(2).to_dict()
    insights["peak_revenue_month"] = monthly.idxmax()
    insights["peak_revenue_month_value"] = round(float(monthly.max()), 2)
    insights["lowest_revenue_month"] = monthly.idxmin()
    insights["lowest_revenue_month_value"] = round(float(monthly.min()), 2)
    return monthly


def viz_04_daily_revenue(sales):
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    by_dow = sales.groupby("DayOfWeek")["Revenue"].sum().reindex(
        [d for d in dow_order if d in sales["DayOfWeek"].unique()]
    )
    plt.figure(figsize=(9, 5.5))
    sns.barplot(x=by_dow.index, y=by_dow.values, hue=by_dow.index, palette="rocket", legend=False)
    plt.title("Total Revenue by Day of Week", fontsize=14, fontweight="bold")
    plt.xlabel("Day of Week")
    plt.ylabel("Revenue (£)")
    plt.xticks(rotation=30)
    plt.gca().yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    savefig("04_daily_revenue.png")

    insights["revenue_by_day_of_week"] = by_dow.round(2).to_dict()
    insights["highest_revenue_day"] = by_dow.idxmax()
    insights["no_saturday_trading"] = "Saturday" not in sales["DayOfWeek"].unique()
    return by_dow


def viz_05_hourly_revenue(sales):
    by_hour = sales.groupby("Hour")["Revenue"].sum()
    plt.figure(figsize=(10, 5.5))
    sns.barplot(x=by_hour.index, y=by_hour.values, hue=by_hour.index, palette="flare", legend=False)
    plt.title("Total Revenue by Hour of Day", fontsize=14, fontweight="bold")
    plt.xlabel("Hour (24h)")
    plt.ylabel("Revenue (£)")
    plt.gca().yaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    savefig("05_hourly_revenue.png")

    insights["revenue_by_hour"] = by_hour.round(2).to_dict()
    insights["peak_hour"] = int(by_hour.idxmax())
    return by_hour


def viz_06_transaction_distribution(sales):
    invoice_totals = sales.groupby("InvoiceNo")["Revenue"].sum()
    plt.figure(figsize=(9, 5.5))
    sns.histplot(invoice_totals.clip(upper=invoice_totals.quantile(0.99)), bins=60, color="#4C72B0")
    plt.title("Distribution of Invoice Revenue (99th-pct capped)", fontsize=14, fontweight="bold")
    plt.xlabel("Invoice Revenue (£)")
    plt.ylabel("Number of Invoices")
    plt.gca().xaxis.set_major_formatter(mticker.StrMethodFormatter("£{x:,.0f}"))
    savefig("06_transaction_distribution.png")

    insights["invoice_revenue_describe"] = invoice_totals.describe().round(2).to_dict()
    insights["invoice_revenue_skew"] = round(float(invoice_totals.skew()), 3)
    return invoice_totals


def viz_07_quantity_price_relationship(sales):
    sample = sales.sample(min(20000, len(sales)), random_state=42)
    plt.figure(figsize=(8, 6))
    plt.scatter(
        sample["UnitPrice"].clip(upper=sample["UnitPrice"].quantile(0.99)),
        sample["Quantity"].clip(upper=sample["Quantity"].quantile(0.99)),
        alpha=0.15, s=12, color="#4C72B0", edgecolors="none",
    )
    plt.title("Quantity vs Unit Price (sampled, 99th-pct capped)", fontsize=14, fontweight="bold")
    plt.xlabel("Unit Price (£)")
    plt.ylabel("Quantity")
    savefig("07_quantity_price_relationship.png")

    r, p = stats.pearsonr(sales["Quantity"], sales["UnitPrice"])
    insights["quantity_price_correlation"] = {"pearson_r": round(float(r), 4), "p_value": float(p)}
    return r, p


def viz_08_cancellation_analysis(d):
    cancel_by_month = d.groupby("InvoiceMonth")["IsCancelled"].mean() * 100
    top6_countries = d["Country"].value_counts().head(6).index
    cancel_by_country = (
        d[d["Country"].isin(top6_countries)].groupby("Country")["IsCancelled"].mean() * 100
    ).sort_values(ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    cancel_by_month.plot(kind="line", marker="o", ax=axes[0], color="#8172B2", linewidth=2)
    axes[0].set_title("Cancellation Rate (%) by Month", fontsize=13, fontweight="bold")
    axes[0].set_ylabel("% of Transaction Lines Cancelled")
    axes[0].set_xlabel("Month")
    axes[0].tick_params(axis="x", rotation=45)

    sns.barplot(x=cancel_by_country.values, y=cancel_by_country.index, ax=axes[1],
                hue=cancel_by_country.index, palette="rocket", legend=False)
    axes[1].set_title("Cancellation Rate (%) by Country (Top 6 by Volume)", fontsize=13, fontweight="bold")
    axes[1].set_xlabel("Cancellation Rate (%)")
    savefig("08_cancellation_analysis.png")

    insights["cancellation_rate_by_month_pct"] = cancel_by_month.round(2).to_dict()
    insights["cancellation_rate_by_country_pct"] = cancel_by_country.round(2).to_dict()
    insights["overall_cancellation_rate_pct"] = round(float(d["IsCancelled"].mean() * 100), 2)
    return cancel_by_month, cancel_by_country


def viz_09_customer_analysis(cust):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    sns.histplot(cust["Orders"].clip(upper=cust["Orders"].quantile(0.99)), bins=30, ax=axes[0], color="#55A868")
    axes[0].set_title("Distribution of Orders per Customer\n(99th-pct capped)", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Number of Orders")

    sns.histplot(cust["Revenue"].clip(upper=cust["Revenue"].quantile(0.99)), bins=30, ax=axes[1], color="#4C72B0")
    axes[1].set_title("Distribution of Revenue per Customer\n(99th-pct capped)", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Total Revenue (£)")

    sns.histplot(cust["AvgOrderValue"].clip(upper=cust["AvgOrderValue"].quantile(0.99)), bins=30, ax=axes[2], color="#DD8452")
    axes[2].set_title("Distribution of Average Order Value\n(99th-pct capped)", fontsize=12, fontweight="bold")
    axes[2].set_xlabel("Average Order Value (£)")
    savefig("09_customer_analysis.png")

    insights["customer_metrics_summary"] = {
        "n_customers": int(len(cust)),
        "orders_describe": cust["Orders"].describe().round(2).to_dict(),
        "revenue_describe": cust["Revenue"].describe().round(2).to_dict(),
        "avg_order_value_describe": cust["AvgOrderValue"].describe().round(2).to_dict(),
    }
    top10 = cust.sort_values("Revenue", ascending=False).head(10)[["CustomerID", "Orders", "Revenue", "AvgOrderValue"]]
    insights["top10_customers_by_revenue"] = top10.round(2).to_dict(orient="records")
    return cust


def viz_10_rfm_analysis(cust):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    sns.histplot(cust["Recency"], bins=40, ax=axes[0], color="#4C72B0")
    axes[0].set_title("Recency (days since last purchase)", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Days")

    sns.histplot(cust["Orders"].clip(upper=cust["Orders"].quantile(0.99)), bins=40, ax=axes[1], color="#DD8452")
    axes[1].set_title("Frequency (distinct orders, 99th-pct capped)", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Number of Orders")

    sns.histplot(cust["Revenue"].clip(upper=cust["Revenue"].quantile(0.99)), bins=40, ax=axes[2], color="#55A868")
    axes[2].set_title("Monetary (£ spent, 99th-pct capped)", fontsize=12, fontweight="bold")
    axes[2].set_xlabel("Total Revenue (£)")
    savefig("10_rfm_analysis.png")

    insights["rfm_summary"] = {
        "recency_describe": cust["Recency"].describe().round(2).to_dict(),
        "frequency_describe": cust["Orders"].describe().round(2).to_dict(),
        "monetary_describe": cust["Revenue"].describe().round(2).to_dict(),
    }
    return cust


# ---------------------------------------------------------------------------
# 4. ADVANCED VISUALIZATIONS (2+)
# ---------------------------------------------------------------------------

def viz_11_country_month_heatmap(sales):
    top8 = sales.groupby("Country")["Revenue"].sum().sort_values(ascending=False).head(8).index
    pivot = sales[sales["Country"].isin(top8)].pivot_table(
        index="Country", columns="InvoiceMonth", values="Revenue", aggfunc="sum", fill_value=0
    ).loc[top8]

    plt.figure(figsize=(13, 5.5))
    sns.heatmap(pivot, cmap="YlGnBu", cbar_kws={"label": "Revenue (£)"})
    plt.title("Advanced: Revenue by Country (Top 8) x Month Heatmap", fontsize=14, fontweight="bold")
    plt.xlabel("Month")
    plt.ylabel("Country")
    plt.xticks(rotation=45)
    savefig("11_country_month_heatmap.png")

    insights["country_month_pivot_top8"] = pivot.round(2).to_dict()
    return pivot


def viz_12_correlation_heatmap(sales):
    corr = sales[["Quantity", "UnitPrice", "Revenue"]].corr(method="pearson")
    plt.figure(figsize=(5.5, 4.5))
    sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f")
    plt.title("Advanced: Correlation Heatmap", fontsize=13, fontweight="bold")
    savefig("12_correlation_heatmap.png")

    insights["correlation_matrix"] = corr.round(3).to_dict()
    return corr


# ---------------------------------------------------------------------------
# 5. INTERACTIVE VISUALIZATIONS (Plotly)
# ---------------------------------------------------------------------------

def interactive_revenue_by_country(sales):
    import plotly.express as px

    rev = sales.groupby("Country")["Revenue"].sum().sort_values(ascending=False).head(15).reset_index()
    fig = px.bar(
        rev, x="Revenue", y="Country", orientation="h",
        title="Interactive: Total Revenue by Country (Top 15)",
        labels={"Revenue": "Total Revenue (£)", "Country": "Country"},
        color="Revenue", color_continuous_scale="Blues",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, template="plotly_white", height=600)
    out_path = INTERACTIVE_DIR / "interactive_revenue_by_country.html"
    fig.write_html(out_path, include_plotlyjs="cdn")
    log(f"Saved interactive visualization -> {out_path.relative_to(ROOT)}")
    return out_path


def interactive_monthly_revenue_trend(sales):
    import plotly.express as px

    monthly = sales.groupby("InvoiceMonth")["Revenue"].sum().sort_index().reset_index()
    fig = px.line(
        monthly, x="InvoiceMonth", y="Revenue", markers=True,
        title="Interactive: Monthly Revenue Trend (Dec 2010 - Dec 2011)",
        labels={"InvoiceMonth": "Month", "Revenue": "Revenue (£)"},
    )
    fig.update_traces(line_color="#C44E52", line_width=3)
    fig.update_layout(template="plotly_white", height=550)
    out_path = INTERACTIVE_DIR / "interactive_monthly_revenue_trend.html"
    fig.write_html(out_path, include_plotlyjs="cdn")
    log(f"Saved interactive visualization -> {out_path.relative_to(ROOT)}")
    return out_path


# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------

def main():
    print("=" * 72)
    print("CodeAlpha Task 3 - Data Visualization: Online Retail Dataset")
    print("=" * 72)

    df = load_data()
    d = prepare_data(df)
    sales = d[d["IsValidSale"]].copy()
    log(f"Valid sales rows used for revenue-based charts: {len(sales):,}")

    cust = build_customer_metrics(d)
    log(f"Customer-level metrics computed for {len(cust):,} customers with a valid CustomerID.")

    # KPIs for the dashboard
    total_revenue = float(sales["Revenue"].sum())
    total_transactions = int(sales["InvoiceNo"].nunique())
    total_customers = int(cust["CustomerID"].nunique())
    avg_order_value = float(sales.groupby("InvoiceNo")["Revenue"].sum().mean())
    cancellation_rate = float(d["IsCancelled"].mean() * 100)

    insights["kpis"] = {
        "total_revenue": round(total_revenue, 2),
        "total_transactions": total_transactions,
        "total_customers": total_customers,
        "average_order_value": round(avg_order_value, 2),
        "cancellation_rate_pct": round(cancellation_rate, 2),
    }
    log("KPIs: " + json.dumps(insights["kpis"]))

    log("Generating required visualizations (1-10) ...")
    viz_01_revenue_by_country(sales)
    viz_02_top_products(sales)
    viz_03_monthly_revenue(sales)
    viz_04_daily_revenue(sales)
    viz_05_hourly_revenue(sales)
    viz_06_transaction_distribution(sales)
    viz_07_quantity_price_relationship(sales)
    viz_08_cancellation_analysis(d)
    viz_09_customer_analysis(cust)
    viz_10_rfm_analysis(cust)

    log("Generating advanced visualizations (11-12) ...")
    viz_11_country_month_heatmap(sales)
    viz_12_correlation_heatmap(sales)

    log("Generating interactive Plotly visualizations ...")
    interactive_revenue_by_country(sales)
    interactive_monthly_revenue_trend(sales)

    # Save prepared dataset
    d.to_csv(PROCESSED_PATH, index=False)
    log(f"Saved prepared dataset -> {PROCESSED_PATH.relative_to(ROOT)}")

    # Save key insights
    with open(INSIGHTS_PATH, "w") as f:
        json.dump(insights, f, indent=2, default=str)
    log(f"Saved key insights -> {INSIGHTS_PATH.relative_to(ROOT)}")

    n_pngs = len(list(VIZ_DIR.glob("*.png")))
    n_html = len(list(INTERACTIVE_DIR.glob("*.html")))
    log(f"Total static visualizations generated: {n_pngs}")
    log(f"Total interactive visualizations generated: {n_html}")
    log("Pipeline completed successfully. Exiting with code 0.")


if __name__ == "__main__":
    main()
    sys.exit(0)

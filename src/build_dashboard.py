"""
CodeAlpha Task 3 - Data Visualization
Builds a single, self-contained, static HTML dashboard (dashboard/dashboard.html)
summarizing the project's key KPIs and strongest visualizations using Plotly.

Design decision: a static, self-contained HTML file (rather than a running
Dash/Streamlit server) was chosen deliberately. It requires zero server setup,
opens in any browser, is fully portable (works from a downloaded ZIP with no
"pip install dash" step), and still provides interactive hover/zoom via
Plotly.js - covering the brief's interactivity requirement without the
added complexity and fragility of a long-running server process for a
static internship deliverable. This decision is documented in the README.

Run from the project root (after src/visualization.py has been run at least
once, so reports/key_insights.json and data/processed/ exist):
    python src/build_dashboard.py
"""

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = ROOT / "data" / "processed" / "online_retail_prepared.csv"
INSIGHTS_PATH = ROOT / "reports" / "key_insights.json"
DASHBOARD_DIR = ROOT / "dashboard"
DASHBOARD_PATH = DASHBOARD_DIR / "dashboard.html"

DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)


def main():
    if not INSIGHTS_PATH.exists() or not PROCESSED_PATH.exists():
        print("[Dashboard] ERROR: run `python src/visualization.py` first "
              "to generate reports/key_insights.json and the processed dataset.")
        sys.exit(1)

    with open(INSIGHTS_PATH) as f:
        insights = json.load(f)

    kpis = insights["kpis"]

    print("[Dashboard] Loading prepared dataset for chart rebuild ...")
    df = pd.read_csv(PROCESSED_PATH, parse_dates=["InvoiceDate"])
    sales = df[df["IsValidSale"]]

    monthly = sales.groupby("InvoiceMonth")["Revenue"].sum().sort_index()
    rev_by_country = sales.groupby("Country")["Revenue"].sum().sort_values(ascending=False).head(10)
    top_products = sales.groupby("Description")["Revenue"].sum().sort_values(ascending=False).head(10)
    cancel_by_month = df.groupby("InvoiceMonth")["IsCancelled"].mean() * 100

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Monthly Revenue Trend",
            "Top 10 Countries by Revenue",
            "Top 10 Products by Revenue",
            "Cancellation Rate (%) by Month",
        ),
        vertical_spacing=0.16,
        horizontal_spacing=0.12,
    )

    fig.add_trace(
        go.Scatter(x=monthly.index, y=monthly.values, mode="lines+markers",
                   line=dict(color="#C44E52", width=3), name="Revenue"),
        row=1, col=1,
    )
    fig.add_trace(
        go.Bar(x=rev_by_country.values, y=rev_by_country.index, orientation="h",
               marker_color="#4C72B0", name="Revenue by Country"),
        row=1, col=2,
    )
    fig.add_trace(
        go.Bar(x=top_products.values, y=[p[:28] for p in top_products.index], orientation="h",
               marker_color="#55A868", name="Top Products"),
        row=2, col=1,
    )
    fig.add_trace(
        go.Scatter(x=cancel_by_month.index, y=cancel_by_month.values, mode="lines+markers",
                   line=dict(color="#8172B2", width=3), name="Cancellation Rate"),
        row=2, col=2,
    )

    fig.update_yaxes(autorange="reversed", row=1, col=2)
    fig.update_yaxes(autorange="reversed", row=2, col=1)
    fig.update_xaxes(title_text="Month", row=1, col=1)
    fig.update_yaxes(title_text="Revenue (£)", row=1, col=1)
    fig.update_xaxes(title_text="Revenue (£)", row=1, col=2)
    fig.update_xaxes(title_text="Revenue (£)", row=2, col=1)
    fig.update_xaxes(title_text="Month", row=2, col=2)
    fig.update_yaxes(title_text="Cancellation Rate (%)", row=2, col=2)

    fig.update_layout(
        height=850, showlegend=False, template="plotly_white",
        title_text="CodeAlpha Task 3 — Online Retail Data Visualization Dashboard",
        title_font_size=20,
        margin=dict(t=110),
    )

    chart_html = fig.to_html(include_plotlyjs="cdn", full_html=False, div_id="main-dashboard-chart")

    kpi_html = f"""
    <div class="kpi-grid">
      <div class="kpi-card"><div class="kpi-label">Total Revenue</div><div class="kpi-value">£{kpis['total_revenue']:,.2f}</div></div>
      <div class="kpi-card"><div class="kpi-label">Total Transactions</div><div class="kpi-value">{kpis['total_transactions']:,}</div></div>
      <div class="kpi-card"><div class="kpi-label">Total Customers</div><div class="kpi-value">{kpis['total_customers']:,}</div></div>
      <div class="kpi-card"><div class="kpi-label">Average Order Value</div><div class="kpi-value">£{kpis['average_order_value']:,.2f}</div></div>
      <div class="kpi-card"><div class="kpi-label">Cancellation Rate</div><div class="kpi-value">{kpis['cancellation_rate_pct']}%</div></div>
    </div>
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CodeAlpha Task 3 — Online Retail Dashboard</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 24px; color: #1f2933; }}
  h1 {{ text-align: center; font-size: 26px; margin-bottom: 4px; }}
  p.subtitle {{ text-align: center; color: #6b7280; margin-top: 0; margin-bottom: 28px; }}
  .kpi-grid {{ display: flex; flex-wrap: wrap; gap: 16px; justify-content: center; margin-bottom: 32px; }}
  .kpi-card {{ background: white; border-radius: 12px; padding: 20px 28px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); min-width: 180px; text-align: center; }}
  .kpi-label {{ font-size: 13px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 6px; }}
  .kpi-value {{ font-size: 24px; font-weight: 700; color: #1f2933; }}
  .chart-container {{ background: white; border-radius: 12px; padding: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); max-width: 1200px; margin: 0 auto; }}
  footer {{ text-align: center; color: #9ca3af; font-size: 12px; margin-top: 24px; }}
</style>
</head>
<body>
  <h1>CodeAlpha Task 3 — Online Retail Data Visualization Dashboard</h1>
  <p class="subtitle">UCI Online Retail Dataset · Dec 2010 – Dec 2011 · Author: Ali Rashid (Chaudhary)</p>
  {kpi_html}
  <div class="chart-container">
    {chart_html}
  </div>
  <footer>All figures computed directly from the real dataset via src/visualization.py. Generated for CodeAlpha Task 3 submission.</footer>
</body>
</html>
"""

    with open(DASHBOARD_PATH, "w") as f:
        f.write(html)
    print(f"[Dashboard] Saved dashboard -> {DASHBOARD_PATH.relative_to(ROOT)}")
    print("[Dashboard] Open it directly in any browser (double-click the file), "
          "or serve it locally with: python -m http.server --directory dashboard 8000 "
          "then visit http://localhost:8000/dashboard.html")


if __name__ == "__main__":
    main()
    sys.exit(0)

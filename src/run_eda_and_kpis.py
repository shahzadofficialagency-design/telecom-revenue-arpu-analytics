"""
EDA + KPI computation on CLEANED data. Every number in
reports/business_insights.md comes from this script's output
(reports/_kpi_results.json) - nothing is hand-typed.
Charts are saved to screenshots/eda_*.png for the README / portfolio.
"""
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P, SHOTS = ROOT / "data" / "processed", ROOT / "screenshots"
SHOTS.mkdir(exist_ok=True)
sns.set_theme(style="whitegrid")

cust = pd.read_csv(P / "customers_clean.csv", parse_dates=["join_date", "churn_date"])
pkg = pd.read_csv(P / "packages_clean.csv")
rev = pd.read_csv(P / "revenue_clean.csv", parse_dates=["month"])
snap = pd.read_csv(P / "subscriber_snapshot_clean.csv", parse_dates=["month"])
rev = rev.merge(cust[["customer_id", "city", "region", "segment"]], on="customer_id", how="left")
rev = rev.merge(pkg[["package_id", "package_name", "package_type"]], on="package_id", how="left")

K = {}
K["total_revenue"] = float(rev.net_revenue.sum())
K["total_billed"] = float(rev.total_billed_amount.sum())
K["total_tax"] = float(rev.tax_amount.sum())
K["revenue_rows"] = int(len(rev)); K["customers"] = int(len(cust))

monthly_rev = rev.groupby("month").net_revenue.sum().sort_index()
monthly_subs = snap.groupby("month").agg(
    opening=("opening_subscribers", "sum"), new=("new_subscribers", "sum"),
    churned=("churned_subscribers", "sum"), closing=("closing_subscribers", "sum"),
    avg_active=("average_active_subscribers", "sum"))
monthly = monthly_subs.join(monthly_rev.rename("revenue"))
monthly["arpu"] = monthly.revenue / monthly.avg_active
monthly["churn_rate_pct"] = monthly.churned / monthly.opening * 100
monthly["growth_pct"] = monthly.revenue.pct_change() * 100
monthly["net_growth"] = monthly.new - monthly.churned
K["monthly"] = {str(k.date()): {c: (None if pd.isna(v) else round(float(v), 2)) for c, v in row.items()}
                for k, row in monthly.iterrows()}
K["best_month"] = str(monthly.revenue.idxmax().date()); K["best_month_revenue"] = float(monthly.revenue.max())
K["worst_month"] = str(monthly.revenue.idxmin().date()); K["worst_month_revenue"] = float(monthly.revenue.min())
K["avg_monthly_arpu"] = float(monthly.arpu.mean())
K["arpu_first_month"] = float(monthly.arpu.iloc[0]); K["arpu_last_month"] = float(monthly.arpu.iloc[-1])
K["highest_churn_month"] = str(monthly.churn_rate_pct.idxmax().date())
K["highest_churn_rate_pct"] = float(monthly.churn_rate_pct.max())
K["total_new"] = int(monthly.new.sum()); K["total_churned_events"] = int(monthly.churned.sum())

for svc, col in [("voice", "voice_revenue"), ("data", "data_revenue"), ("sms", "sms_revenue"), ("vas", "vas_revenue")]:
    K[f"{svc}_revenue"] = float(rev[col].sum())
    K[f"{svc}_share_pct"] = float(rev[col].sum() / rev.net_revenue.sum() * 100)
K["top_service"] = max(["voice", "data", "sms", "vas"], key=lambda s: K[f"{s}_revenue"])

city_rev = rev.groupby("city").net_revenue.sum().sort_values(ascending=False)
city_avg_subs = snap.groupby("city").average_active_subscribers.mean()
city_arpu_monthly_avg = (city_rev / 12) / city_avg_subs
K["city_revenue"] = {k: float(v) for k, v in city_rev.items()}
K["top_city"] = str(city_rev.index[0]); K["bottom_city"] = str(city_rev.index[-1])
K["city_arpu_avg_monthly"] = {k: float(v) for k, v in city_arpu_monthly_avg.items()}
K["top_arpu_city"] = str(city_arpu_monthly_avg.idxmax()); K["top_arpu_city_value"] = float(city_arpu_monthly_avg.max())

pkg_rev = rev.groupby("package_name").net_revenue.sum().sort_values(ascending=False)
pkg_arpu = rev.groupby("package_name").net_revenue.mean()
K["package_revenue"] = {k: float(v) for k, v in pkg_rev.items()}
K["top_package"] = str(pkg_rev.index[0]); K["top_package_revenue"] = float(pkg_rev.max())
K["package_arpu"] = {k: float(v) for k, v in pkg_arpu.items()}
K["top_package_arpu"] = str(pkg_arpu.idxmax())

seg = rev.groupby("segment").agg(revenue=("net_revenue", "sum"), customers=("customer_id", "nunique"))
seg["rev_per_customer"] = seg.revenue / seg.customers
K["segment_revenue"] = {k: float(v) for k, v in seg.revenue.items()}
K["segment_rev_per_customer"] = {k: float(v) for k, v in seg.rev_per_customer.items()}
K["top_segment_rev_per_customer"] = str(seg.rev_per_customer.idxmax())

K["subscriber_growth_jan_to_dec"] = int(monthly.closing.iloc[-1] - monthly.opening.iloc[0])
K["revenue_growth_jan_to_dec_pct"] = float((monthly.revenue.iloc[-1] / monthly.revenue.iloc[0] - 1) * 100)
K["outliers_net_revenue_over_3std"] = int((rev.net_revenue > rev.net_revenue.mean() + 3 * rev.net_revenue.std()).sum())
K["customer_by_city"] = {k: int(v) for k, v in cust.city.value_counts().items()}
K["customer_by_segment"] = {k: int(v) for k, v in cust.segment.value_counts().items()}
K["customer_by_type"] = {k: int(v) for k, v in cust.customer_type.value_counts().items()}

(ROOT / "reports" / "_kpi_results.json").write_text(json.dumps(K, indent=2), encoding="utf-8")

# ---------------------------------------------------------------- charts
def save(fig, name):
    fig.tight_layout(); fig.savefig(SHOTS / name, dpi=130); plt.close(fig); print("chart:", name)

fig, ax = plt.subplots(figsize=(9, 4)); monthly.revenue.plot(ax=ax, marker="o")
ax.set_title("Monthly Net Service Revenue (PKR) - Simulated Data"); ax.set_ylabel("PKR"); save(fig, "eda_01_monthly_revenue_trend.png")

fig, ax = plt.subplots(figsize=(9, 4)); monthly.arpu.plot(ax=ax, marker="o", color="darkorange")
ax.set_title("Monthly ARPU (PKR) = Net Revenue / Avg Active Subscribers"); ax.set_ylabel("PKR"); save(fig, "eda_02_monthly_arpu_trend.png")

fig, ax = plt.subplots(figsize=(8, 4)); city_rev.plot.bar(ax=ax)
ax.set_title("Revenue by City (PKR)"); ax.set_ylabel("PKR"); save(fig, "eda_03_revenue_by_city.png")

fig, ax = plt.subplots(figsize=(9, 4)); pkg_rev.plot.bar(ax=ax, color="seagreen")
ax.set_title("Revenue by Package (PKR)"); ax.set_ylabel("PKR"); save(fig, "eda_04_revenue_by_package.png")

mix = rev[["voice_revenue", "data_revenue", "sms_revenue", "vas_revenue"]].sum()
fig, ax = plt.subplots(figsize=(6, 6)); mix.plot.pie(ax=ax, autopct="%1.1f%%", ylabel="")
ax.set_title("Service Revenue Mix (share of net revenue)"); save(fig, "eda_05_service_mix.png")

fig, ax = plt.subplots(figsize=(9, 4)); monthly[["new", "churned"]].plot.bar(ax=ax)
ax.set_title("New vs Churned Subscribers by Month"); save(fig, "eda_06_new_vs_churned.png")

fig, ax = plt.subplots(figsize=(8, 5)); sns.histplot(rev.net_revenue, bins=50, ax=ax)
ax.set_title("Distribution of Monthly Net Revenue per Customer (PKR)"); save(fig, "eda_07_revenue_distribution.png")

fig, ax = plt.subplots(figsize=(8, 4)); city_arpu_monthly_avg.sort_values().plot.barh(ax=ax, color="purple")
ax.set_title("Average Monthly ARPU by City (PKR)"); ax.set_xlabel("PKR"); save(fig, "eda_08_arpu_by_city.png")

print(json.dumps({k: K[k] for k in ["total_revenue", "best_month", "worst_month", "avg_monthly_arpu",
      "top_service", "top_city", "top_arpu_city", "top_package", "highest_churn_month"]}, indent=2))

"""
SQL-logic reconciliation test.
The production SQL in sql/*.sql is PostgreSQL dialect. This harness
loads the SAME cleaned CSVs into SQLite and runs the SAME aggregation
logic (CTE pattern: aggregate each fact separately, then join) to
prove the SQL totals reconcile exactly with the Python KPI results
in reports/_kpi_results.json. It does not replace running the real
PostgreSQL scripts - see README 'Setup' for those steps.
"""
import json, sqlite3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
con = sqlite3.connect(":memory:")
for tbl, f in [("dim_customers", "customers_clean.csv"), ("dim_packages", "packages_clean.csv"),
               ("fact_revenue", "revenue_clean.csv"), ("fact_subscribers", "subscriber_snapshot_clean.csv")]:
    pd.read_csv(P / f).to_sql(tbl, con, index=False)
K = json.loads((ROOT / "reports" / "_kpi_results.json").read_text())

def q(sql):
    return con.execute(sql).fetchall()

total = q("SELECT SUM(net_revenue) FROM fact_revenue")[0][0]
print(f"SQL total revenue = {total:,.2f} | Python = {K['total_revenue']:,.2f} | match = {abs(total-K['total_revenue'])<0.5}")
assert abs(total - K["total_revenue"]) < 0.5

dec = q("""WITH rev AS (SELECT month, SUM(net_revenue) r FROM fact_revenue GROUP BY month),
           subs AS (SELECT month, SUM(average_active_subscribers) a FROM fact_subscribers GROUP BY month)
           SELECT rev.r/subs.a FROM rev JOIN subs ON subs.month=rev.month WHERE rev.month='2025-12-01'""")[0][0]
print(f"SQL Dec ARPU = {dec:,.2f} | Python = {K['monthly']['2025-12-01']['arpu']:,.2f} | match = {abs(dec-K['monthly']['2025-12-01']['arpu'])<0.5}")
assert abs(dec - K["monthly"]["2025-12-01"]["arpu"]) < 0.5

top_city = q("""SELECT c.city, SUM(r.net_revenue) FROM fact_revenue r
                JOIN dim_customers c ON c.customer_id=r.customer_id
                GROUP BY c.city ORDER BY 2 DESC LIMIT 1""")[0]
print(f"SQL top city = {top_city[0]} ({top_city[1]:,.0f}) | Python = {K['top_city']}")
assert top_city[0] == K["top_city"]
print("ALL SQL-vs-Python reconciliations PASSED")

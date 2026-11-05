"""
Validation / QA suite for the CLEANED PakConnect dataset.
Every test in the brief's Section 16 is implemented here.
Exit code 0 = all tests pass. Run: python src/validate_data.py
"""
import pandas as pd, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
c = pd.read_csv(P / "customers_clean.csv", dtype=str, keep_default_na=False)
# re-read with types where arithmetic is needed
cust = pd.read_csv(P / "customers_clean.csv", parse_dates=["join_date", "churn_date"])
pkg = pd.read_csv(P / "packages_clean.csv")
rev = pd.read_csv(P / "revenue_clean.csv", parse_dates=["month"])
snap = pd.read_csv(P / "subscriber_snapshot_clean.csv", parse_dates=["month"])
dim = pd.read_csv(P / "dim_date_clean.csv", parse_dates=["date"])

tests = []
def check(name, ok, detail=""):
    tests.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'} | {name} {detail}")

check("Duplicate customer IDs = 0", cust.customer_id.duplicated().sum() == 0,
      f"(found {cust.customer_id.duplicated().sum()})")
check("Duplicate package IDs = 0", pkg.package_id.duplicated().sum() == 0)
check("Duplicate customer-month revenue = 0", rev.duplicated(subset=['customer_id','month']).sum() == 0,
      f"(found {rev.duplicated(subset=['customer_id','month']).sum()})")
check("Missing required customer IDs = 0", rev.customer_id.isna().sum() == 0 and (rev.customer_id == '').sum() == 0)
check("Invalid package references = 0", (~rev.package_id.isin(pkg.package_id)).sum() == 0)
calc = (rev.voice_revenue + rev.data_revenue + rev.sms_revenue + rev.vas_revenue - rev.discount).round(2)
check("Revenue calculation mismatch = 0", (abs(calc - rev.net_revenue) >= 0.01).sum() == 0,
      f"(found {(abs(calc - rev.net_revenue) >= 0.01).sum()})")
check("Billed = Net + Tax mismatch = 0",
      (abs((rev.net_revenue + rev.tax_amount).round(2) - rev.total_billed_amount) >= 0.01).sum() == 0)
check("Invalid dates = 0", dim.date.isna().sum() == 0 and rev.month.isna().sum() == 0
      and cust.join_date.isna().sum() == 0)
check("Subscriber balance mismatch = 0",
      (snap.closing_subscribers != snap.opening_subscribers + snap.new_subscribers - snap.churned_subscribers).sum() == 0)
check("Snapshot rows = 84", len(snap) == 84, f"(found {len(snap)})")
check("Dim date rows = 365", len(dim) == 365, f"(found {len(dim)})")
check("Customers = 10,000", len(cust) == 10000, f"(found {len(cust)})")
check("Packages = 10", len(pkg) == 10, f"(found {len(pkg)})")
m = rev.merge(cust[["customer_id", "join_date", "churn_date"]], on="customer_id", how="left")
m["join_month"] = m.join_date.dt.to_period("M").dt.to_timestamp()
m["churn_month"] = m.churn_date.dt.to_period("M").dt.to_timestamp()
check("No revenue before join month", (m.month < m.join_month).sum() == 0,
      f"(found {(m.month < m.join_month).sum()})")
check("No revenue after churn month", ((m.churn_month.notna()) & (m.month > m.churn_month)).sum() == 0,
      f"(found {((m.churn_month.notna()) & (m.month > m.churn_month)).sum()})")
check("City consistency: every snapshot city exists in customers",
      set(snap.city) <= set(cust.city), f"(cities: {sorted(set(snap.city))})")
check("No negative revenue / discount / tax",
      (rev[["voice_revenue","data_revenue","sms_revenue","vas_revenue","discount","tax_amount"]] < 0).sum().sum() == 0)
check("Ages within 18-100", cust.age.between(18, 100).all() if 'age' in cust else cust['age'].astype(int).between(18,100).all())
# ARPU denominator sanity: monthly avg active subscribers must be > 0 for every month
monthly_subs = snap.groupby("month").average_active_subscribers.sum()
check("ARPU denominator > 0 for all 12 months", (monthly_subs > 0).all() and len(monthly_subs) == 12)

failed = [t for t in tests if not t[1]]
print(f"\n{len(tests) - len(failed)}/{len(tests)} tests passed")
(ROOT / "reports" / "_validation_log.txt").write_text(
    "\n".join(f"{'PASS' if ok else 'FAIL'} | {n} {d}" for n, ok, d in tests), encoding="utf-8")
sys.exit(1 if failed else 0)

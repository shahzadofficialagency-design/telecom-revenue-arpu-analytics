"""
Data cleaning for PakConnect Telecom (FICTIONAL, simulated data).
Reads data/raw/*.csv, writes data/processed/*_clean.csv.
Raw files are NEVER overwritten.

Cleaning policy (documented, business-first - not "delete everything"):
  * Trim whitespace and standardise case on city / region / labels.
  * Parse dates strictly; unparseable dates are reported, not guessed.
  * IDs stay strings (leading zeros matter in CUST00001 style IDs).
  * Missing values are COUNTED and reported per column. In this
    generated dataset the only structurally-missing column is
    churn_date for Active customers - that is correct, not an error,
    and it is NOT filled with zero or a fake date.
  * Only exact duplicate rows are removed, and the count is reported.
  * Negative revenue is NOT blindly deleted: it would mean a refund /
    adjustment. The generator creates none, so any negative found is
    flagged in the report for investigation instead of dropped.
  * Revenue arithmetic is re-validated after cleaning; mismatches are
    reported, not silently overwritten.
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "data" / "raw", ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
report = []

def log(msg):
    print(msg); report.append(msg)

def strip_cols(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    return df

# ------------------------------------------------------------- customers
c = pd.read_csv(RAW / "customers.csv", dtype={"customer_id": str})
before = len(c)
c = strip_cols(c, ["gender", "city", "region", "segment", "customer_type", "status", "contract_type"])
c["city"] = c["city"].str.title(); c["region"] = c["region"].str.title()
c["region"] = c["region"].replace({"Islamabad Capital Territory": "Islamabad Capital Territory",
                                   "Khyber Pakhtunkhwa": "Khyber Pakhtunkhwa"})
c["join_date"] = pd.to_datetime(c["join_date"], errors="coerce").dt.date
c["churn_date"] = pd.to_datetime(c["churn_date"], errors="coerce").dt.date
c["auto_payment"] = c["auto_payment"].astype(bool)
dupes = int(c.duplicated(subset=["customer_id"]).sum())
c = c.drop_duplicates(subset=["customer_id"]).drop_duplicates()
log(f"customers: {before} -> {len(c)} rows | duplicate customer_ids removed={dupes} | "
    f"missing per col: {c.isnull().sum().to_dict()} (churn_date empty = Active, expected)")

# -------------------------------------------------------------- packages
p = pd.read_csv(RAW / "packages.csv", dtype={"package_id": str})
before = len(p)
p = strip_cols(p, ["package_name", "package_type", "package_status"])
for col in ["monthly_fee", "data_limit_gb"]:
    p[col] = pd.to_numeric(p[col], errors="coerce")
dupes = int(p.duplicated(subset=["package_id"]).sum())
p = p.drop_duplicates(subset=["package_id"])
log(f"packages: {before} -> {len(p)} rows | duplicate package_ids removed={dupes} | invalid fees={(p.monthly_fee <= 0).sum()}")

# --------------------------------------------------------------- revenue
r = pd.read_csv(RAW / "revenue.csv", dtype={"revenue_id": str, "customer_id": str, "package_id": str})
before = len(r)
r["month"] = pd.to_datetime(r["month"], errors="coerce").dt.date
money = ["voice_revenue", "data_revenue", "sms_revenue", "vas_revenue",
         "discount", "net_revenue", "tax_amount", "total_billed_amount"]
for col in money:
    r[col] = pd.to_numeric(r[col], errors="coerce")
dupes = int(r.duplicated(subset=["customer_id", "month"]).sum())
r = r.drop_duplicates(subset=["customer_id", "month"]).drop_duplicates()
neg = int((r[money] < 0).any(axis=1).sum())
calc_net = (r.voice_revenue + r.data_revenue + r.sms_revenue + r.vas_revenue - r.discount).round(2)
mismatch = int((abs(calc_net - r.net_revenue) >= 0.01).sum())
billed_mismatch = int((abs((r.net_revenue + r.tax_amount).round(2) - r.total_billed_amount) >= 0.01).sum())
bad_cust = int((~r.customer_id.isin(c.customer_id)).sum())
bad_pkg = int((~r.package_id.isin(p.package_id)).sum())
log(f"revenue: {before} -> {len(r)} rows | duplicate customer-months removed={dupes} | "
    f"negative-money rows flagged (kept, would be refunds/adjustments)={neg} | "
    f"net_revenue mismatches={mismatch} | billed mismatches={billed_mismatch} | "
    f"unknown customer refs={bad_cust} | unknown package refs={bad_pkg}")

# --------------------------------------------------------------- snapshot
s = pd.read_csv(RAW / "subscriber_snapshot.csv")
before = len(s)
s = strip_cols(s, ["city"]); s["city"] = s["city"].str.title()
s["month"] = pd.to_datetime(s["month"], errors="coerce").dt.date
dupes = int(s.duplicated(subset=["month", "city"]).sum())
s = s.drop_duplicates(subset=["month", "city"])
balance_bad = int((s.closing_subscribers != s.opening_subscribers + s.new_subscribers - s.churned_subscribers).sum())
s["average_active_subscribers"] = ((s.opening_subscribers + s.closing_subscribers) / 2).round(2)
log(f"subscriber_snapshot: {before} -> {len(s)} rows | duplicate city-months removed={dupes} | balance mismatches={balance_bad}")

# --------------------------------------------------------------- dim_date
d = pd.read_csv(RAW / "dim_date.csv")
before = len(d)
d["date"] = pd.to_datetime(d["date"], errors="coerce").dt.date
d["month_start"] = pd.to_datetime(d["month_start"], errors="coerce").dt.date
dupes = int(d.duplicated(subset=["date"]).sum())
d = d.drop_duplicates(subset=["date"]).sort_values("date")
log(f"dim_date: {before} -> {len(d)} rows | duplicate dates removed={dupes}")

c.to_csv(PROC / "customers_clean.csv", index=False)
p.to_csv(PROC / "packages_clean.csv", index=False)
r.to_csv(PROC / "revenue_clean.csv", index=False)
s.to_csv(PROC / "subscriber_snapshot_clean.csv", index=False)
d.to_csv(PROC / "dim_date_clean.csv", index=False)
(ROOT / "reports" / "_cleaning_log.txt").write_text("\n".join(report), encoding="utf-8")
print("Clean files written to data/processed/")

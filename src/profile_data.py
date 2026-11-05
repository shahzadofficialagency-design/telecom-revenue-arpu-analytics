"""
Data profiling for every RAW csv (brief Section 8).
Run BEFORE cleaning: python src/profile_data.py
Writes reports/_profiling_log.txt and prints the same.
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
lines = []
def log(x=""):
    print(x); lines.append(str(x))

for name in ["customers", "packages", "revenue", "subscriber_snapshot", "dim_date"]:
    df = pd.read_csv(RAW / f"{name}.csv")
    log(f"\n===== {name}.csv =====")
    log(f"shape (rows, cols): {df.shape}")
    log(f"columns: {list(df.columns)}")
    log(f"dtypes:\n{df.dtypes.to_string()}")
    log(f"missing values per column:\n{df.isnull().sum().to_string()}")
    log(f"fully duplicated rows: {int(df.duplicated().sum())}")
    log(f"unique values per column:\n{df.nunique().to_string()}")
    num = df.select_dtypes("number")
    if len(num.columns):
        log(f"numeric describe:\n{num.describe().round(2).to_string()}")
    for col in df.columns:
        if df[col].dtype == object and df[col].nunique() <= 12:
            log(f"value counts [{col}]: {df[col].value_counts().to_dict()}")

# cross-dataset relationships
cust = pd.read_csv(RAW / "customers.csv"); rev = pd.read_csv(RAW / "revenue.csv")
pkg = pd.read_csv(RAW / "packages.csv"); snap = pd.read_csv(RAW / "subscriber_snapshot.csv")
log("\n===== relationships =====")
log(f"revenue customer_ids not in customers: {int((~rev.customer_id.isin(cust.customer_id)).sum())}")
log(f"revenue package_ids not in packages: {int((~rev.package_id.isin(pkg.package_id)).sum())}")
log(f"snapshot cities not in customers: {sorted(set(snap.city) - set(cust.city))}")
log(f"revenue months: {sorted(rev.month.unique())}")
(ROOT / "reports" / "_profiling_log.txt").write_text("\n".join(lines), encoding="utf-8")
print("\nProfiling log written to reports/_profiling_log.txt")

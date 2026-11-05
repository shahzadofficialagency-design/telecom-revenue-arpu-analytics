"""
PakConnect Telecom (FICTIONAL) - Synthetic Data Generation
============================================================
DISCLOSURE: PakConnect Telecom is a fictional operator. Every record in
this dataset is SIMULATED with a fixed random seed (42). Nothing here is
data from Jazz, Zong, Ufone, Telenor or any real operator, and package
prices are project assumptions, not real market tariffs.

Why synthetic? Public telecom datasets that were inspected
(Kaggle Telco Customer Churn - 7,043 rows x 21 cols, one customer
snapshot, no monthly revenue history; Maven Analytics Telecom Churn -
7,043 customers, Q2 2022 snapshot) cannot answer monthly revenue / ARPU
questions for Pakistan in PKR for Jan-Dec 2025. See
reports/project_documentation.md, section "Data Source Research".

Business rules enforced here:
  * No revenue before a customer's join_date.
  * No revenue after a customer's churn_date (churn month itself is the
    last billed month - the customer was present during part of it).
  * Revenue splits follow package type (Data packages earn mostly data
    revenue, Voice packages mostly voice revenue, etc.).
  * Business / Premium segments spend more than Student / Mass.
  * Discounts are 0-8% of gross service revenue, never more.
  * Tax is kept separate from service revenue. Blended assumed rate 16%
    (a modelling assumption, NOT a statutory Pakistan telecom tax rate).
  * Subscriber snapshots are DERIVED from the customer master
    (join / churn events per city-month), never invented separately, so
    Closing = Opening + New - Churned holds exactly by construction.
  * monthly_fee is the catalogue monthly-equivalent spend anchor.
    Daily/Weekly bundles renew several times a month; their total
    monthly outlay is modelled around that anchor (documented assumption).

Run:  python src/generate_data.py
Outputs: data/raw/*.csv  +  a printed generation summary.
"""
import numpy as np
import pandas as pd
from pathlib import Path

SEED = 42
rng = np.random.default_rng(SEED)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- config
CITY_REGION = {
    "Lahore": "Punjab", "Karachi": "Sindh", "Islamabad": "Islamabad Capital Territory",
    "Faisalabad": "Punjab", "Multan": "Punjab", "Peshawar": "Khyber Pakhtunkhwa",
    "Quetta": "Balochistan",
}
CITY_W = np.array([0.26, 0.24, 0.15, 0.11, 0.09, 0.08, 0.07])  # sums to 1.00
CITIES = list(CITY_REGION.keys())

PACKAGES = pd.DataFrame([
    # package_id, name, type, monthly_fee, voice_min, sms, data_gb, validity, status
    ("PKG01", "Super Data",     "Data",     800,  300,  1000, 30, 30, "Active"),
    ("PKG02", "Smart Plus",     "Hybrid",  1200, 1000,  2000, 20, 30, "Active"),
    ("PKG03", "Unlimited Voice","Voice",    600, 5000,  1000,  5, 30, "Active"),
    ("PKG04", "Premium Max",    "Hybrid",  2000, 3000,  5000, 60, 30, "Active"),
    ("PKG05", "Social Bundle",  "Data",     350,  100,   500, 10, 30, "Active"),
    ("PKG06", "Business Pro",   "Business",2500, 4000,  3000, 80, 30, "Active"),
    ("PKG07", "Daily Saver",    "Hybrid",   100,   50,   100,  1,  1, "Active"),
    ("PKG08", "Weekly Power",   "Hybrid",   300,  200,   300,  5,  7, "Active"),
    ("PKG09", "Student Package","Data",     500,  200,  1000, 15, 30, "Active"),
    ("PKG10", "Family Connect", "Hybrid",  1800, 2000,  3000, 40, 30, "Active"),
], columns=["package_id", "package_name", "package_type", "monthly_fee",
            "voice_minutes", "sms_limit", "data_limit_gb", "validity_days",
            "package_status"])

# package choice weights per segment (aligned to PACKAGES row order)
PKG_W = {
    "Mass":     [0.18, 0.14, 0.14, 0.02, 0.16, 0.00, 0.12, 0.12, 0.04, 0.08],
    "Premium":  [0.10, 0.20, 0.05, 0.35, 0.02, 0.05, 0.00, 0.03, 0.00, 0.20],
    "Business": [0.05, 0.10, 0.05, 0.20, 0.00, 0.45, 0.00, 0.00, 0.00, 0.15],
    "Student":  [0.15, 0.08, 0.05, 0.00, 0.25, 0.00, 0.10, 0.12, 0.25, 0.00],
    "Family":   [0.10, 0.18, 0.08, 0.10, 0.05, 0.02, 0.02, 0.05, 0.00, 0.40],
}
SEG_FACTOR = {  # spend multiplier range vs package fee anchor
    "Mass": (0.80, 1.30), "Premium": (1.20, 1.80), "Business": (1.30, 2.20),
    "Student": (0.60, 1.00), "Family": (1.10, 1.60),
}
SPLIT_CENTRE = {  # voice, data, sms, vas share centres by package type
    "Data":     (0.13, 0.70, 0.04, 0.13),
    "Voice":    (0.65, 0.15, 0.10, 0.10),
    "Hybrid":   (0.30, 0.47, 0.05, 0.18),
    "Business": (0.35, 0.40, 0.05, 0.20),
}
SEASON = {1:0.98, 2:0.97, 3:1.06, 4:1.05, 5:1.00, 6:1.03,
          7:0.99, 8:1.01, 9:1.00, 10:1.02, 11:1.03, 12:1.08}  # Ramadan/Eid/year-end pattern - assumption
TAX_RATE = 0.16
N = 10_000

# ------------------------------------------------------------- customers
cities = rng.choice(CITIES, size=N, p=CITY_W)
genders = rng.choice(["Male", "Female"], size=N, p=[0.57, 0.43])
ages = np.clip(rng.normal(33, 11, N), 18, 70).round().astype(int)

segments = []
for age in ages:
    r = rng.random()
    if age <= 25 and r < 0.35:
        segments.append("Student")
    elif r < 0.58:
        segments.append("Mass")
    elif r < 0.71:
        segments.append("Family")
    elif r < 0.84:
        segments.append("Business")
    else:
        segments.append("Premium")
segments = np.array(segments)

ctype = np.where(rng.random(N) < 0.78, "Prepaid", "Postpaid")
ctype = np.where(segments == "Business", np.where(rng.random(N) < 0.75, "Postpaid", "Prepaid"), ctype)
contract = rng.choice(["Month-to-Month", "One Year", "Two Year"], size=N, p=[0.60, 0.25, 0.15])
contract = np.where(ctype == "Prepaid", "Month-to-Month", contract)
auto_pay = np.where(ctype == "Postpaid", rng.random(N) < 0.65, rng.random(N) < 0.20)

# join dates: 88% existing base (2022-2024), 12% new joiners during 2025
join_dates = []
for _ in range(N):
    if rng.random() < 0.88:
        join_dates.append(pd.Timestamp("2022-01-01") + pd.Timedelta(days=int(rng.integers(0, 1096))))
    else:
        join_dates.append(pd.Timestamp("2025-01-01") + pd.Timedelta(days=int(rng.integers(0, 334))))
join_dates = pd.to_datetime(join_dates)

# churn: only during 2025, at least 30 days after joining, ~9% of the base
# plus a small share of 2025 joiners. Status derives from churn_date.
churn_dates = pd.Series([pd.NaT] * N, dtype="datetime64[ns]")
for i in range(N):
    base_prob = 0.085 if join_dates[i] < pd.Timestamp("2025-01-01") else 0.05
    if rng.random() < base_prob:
        earliest = max(join_dates[i] + pd.Timedelta(days=30), pd.Timestamp("2025-01-01"))
        latest = pd.Timestamp("2025-12-15")
        if earliest < latest:
            span = (latest - earliest).days
            churn_dates.iloc[i] = earliest + pd.Timedelta(days=int(rng.integers(0, span + 1)))
status = np.where(churn_dates.isna(), "Active", "Churned")

customers = pd.DataFrame({
    "customer_id": [f"CUST{ i+1:05d}" for i in range(N)],
    "gender": genders, "age": ages, "city": cities,
    "region": [CITY_REGION[c] for c in cities],
    "join_date": join_dates.date, "segment": segments,
    "customer_type": ctype, "status": status, "contract_type": contract,
    "auto_payment": auto_pay, "churn_date": churn_dates.dt.date,
})
# NOTE: churn_date is an EXTRA auditable column beyond the brief's minimum
# list - without it, "no revenue after churn" cannot be verified.

# ------------------------------------------- package history (with switches)
pkg_fee = dict(zip(PACKAGES.package_id, PACKAGES.monthly_fee))
pkg_type = dict(zip(PACKAGES.package_id, PACKAGES.package_type))
pkg_ids = list(PACKAGES.package_id)

history_rows, initial_pkg = [], {}
for i, cust in customers.iterrows():
    idx = i  # customers index is 0..N-1 in order
    p0 = rng.choice(pkg_ids, p=PKG_W[cust["segment"]])
    initial_pkg[cust["customer_id"]] = p0
    start = pd.Timestamp(cust["join_date"])
    end_limit = pd.Timestamp(cust["churn_date"]) if pd.notna(cust["churn_date"]) else pd.Timestamp("2025-12-31")
    # ~8% of customers with enough tenure switch package once during 2025
    switched = False
    if rng.random() < 0.08:
        sw_earliest = max(start + pd.Timedelta(days=60), pd.Timestamp("2025-02-01"))
        if sw_earliest < end_limit - pd.Timedelta(days=30):
            sw = sw_earliest + pd.Timedelta(days=int(rng.integers(0, (end_limit - pd.Timedelta(days=30) - sw_earliest).days + 1)))
            sw_month = pd.Timestamp(sw.year, sw.month, 1)
            p1 = rng.choice([p for p in pkg_ids if p != p0])
            history_rows.append((cust["customer_id"], p0, start.date(),
                                 (sw_month - pd.Timedelta(days=1)).date(), "Initial Activation"))
            history_rows.append((cust["customer_id"], p1, sw_month.date(),
                                 end_limit.date(), rng.choice(["Upgrade", "Downgrade", "Promotion"])))
            initial_pkg[cust["customer_id"] + "_switch"] = (sw_month, p1)
            switched = True
    if not switched:
        history_rows.append((cust["customer_id"], p0, start.date(), end_limit.date(), "Initial Activation"))
history = pd.DataFrame(history_rows, columns=["customer_id", "package_id",
                        "effective_start_date", "effective_end_date", "change_reason"])

def package_for(cid, month_start):
    sw = initial_pkg.get(cid + "_switch")
    if sw and month_start >= sw[0]:
        return sw[1]
    return initial_pkg[cid]

# ---------------------------------------------------------------- revenue
months = pd.date_range("2025-01-01", "2025-12-01", freq="MS")
rev_rows, rid = [], 0
cust_lookup = customers.set_index("customer_id")
for m in months:
    m_end = m + pd.offsets.MonthEnd(0)
    season = SEASON[m.month]
    for cid, cust in cust_lookup.iterrows():
        join = pd.Timestamp(cust["join_date"])
        if join > m_end:
            continue  # not yet a customer
        churn = pd.Timestamp(cust["churn_date"]) if pd.notna(cust["churn_date"]) else None
        if churn is not None and churn < m:
            continue  # already churned before this month (churn month itself bills)
        pid = package_for(cid, m)
        lo, hi = SEG_FACTOR[cust["segment"]]
        factor = rng.uniform(lo, hi) * rng.uniform(0.85, 1.15) * season
        if PACKAGES.loc[PACKAGES.package_id == pid, "validity_days"].iloc[0] < 30:
            factor *= rng.uniform(0.60, 1.00)  # daily/weekly bundles: partial-month renewals
        gross = pkg_fee[pid] * factor
        centre = np.array(SPLIT_CENTRE[pkg_type[pid]], dtype=float)
        shares = np.clip(rng.normal(centre, 0.03), 0.01, None)
        shares = shares / shares.sum()
        voice, data_r, sms, vas = (gross * shares).round(2)
        gross_r = round(voice + data_r + sms + vas, 2)
        disc = round(gross_r * rng.uniform(0, 0.08), 2) if rng.random() < 0.40 else 0.00
        net = round(gross_r - disc, 2)
        tax = round(net * TAX_RATE, 2)
        rid += 1
        rev_rows.append((f"REV{rid:06d}", cid, m.date(), pid, voice, data_r, sms, vas,
                         disc, net, tax, round(net + tax, 2)))
revenue = pd.DataFrame(rev_rows, columns=["revenue_id", "customer_id", "month", "package_id",
                       "voice_revenue", "data_revenue", "sms_revenue", "vas_revenue",
                       "discount", "net_revenue", "tax_amount", "total_billed_amount"])

# --------------------------------------- subscriber snapshot (DERIVED, not invented)
snap_rows = []
prev_closing = {}
for m in months:
    m_end = m + pd.offsets.MonthEnd(0)
    for city in CITIES:
        cc = customers[customers.city == city]
        if city not in prev_closing:  # January opening = base present on 1 Jan 2025
            prev_closing[city] = int(((pd.to_datetime(cc.join_date) < m) &
                                      (pd.to_datetime(cc.churn_date).isna() |
                                       (pd.to_datetime(cc.churn_date) >= m))).sum())
        opening = prev_closing[city]
        new = int(((pd.to_datetime(cc.join_date) >= m) & (pd.to_datetime(cc.join_date) <= m_end)).sum())
        churned = int(((pd.to_datetime(cc.churn_date) >= m) & (pd.to_datetime(cc.churn_date) <= m_end)).sum())
        closing = opening + new - churned
        snap_rows.append((m.date(), city, opening, new, churned, closing, (opening + closing) / 2))
        prev_closing[city] = closing
snapshot = pd.DataFrame(snap_rows, columns=["month", "city", "opening_subscribers",
                        "new_subscribers", "churned_subscribers", "closing_subscribers",
                        "average_active_subscribers"])

# ---------------------------------------------------------------- dim_date
dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
dim_date = pd.DataFrame({
    "date": dates.date, "day": dates.day, "month": dates.month,
    "month_name": dates.strftime("%B"), "month_start": dates.to_period("M").to_timestamp().date,
    "quarter": dates.quarter, "year": dates.year,
    "year_month": dates.strftime("%Y-%m"), "weekday": dates.weekday,
    "weekday_name": dates.strftime("%A"),
})

# ------------------------------------------------------------------- save
customers.to_csv(RAW / "customers.csv", index=False)
PACKAGES.to_csv(RAW / "packages.csv", index=False)
revenue.to_csv(RAW / "revenue.csv", index=False)
snapshot.to_csv(RAW / "subscriber_snapshot.csv", index=False)
dim_date.to_csv(RAW / "dim_date.csv", index=False)
history.to_csv(RAW / "customer_package_history.csv", index=False)

print("=== DATA GENERATION SUMMARY (seed=42, SIMULATED data) ===")
print(f"customers.csv               : {len(customers):,} rows | churned={int((customers.status=='Churned').sum()):,}")
print(f"packages.csv                : {len(PACKAGES)} rows")
print(f"revenue.csv                 : {len(revenue):,} rows | total net revenue PKR {revenue.net_revenue.sum():,.0f}")
print(f"subscriber_snapshot.csv     : {len(snapshot)} rows (7 cities x 12 months = 84 expected)")
print(f"dim_date.csv                : {len(dim_date)} rows (2025 is not a leap year = 365 expected)")
print(f"customer_package_history.csv: {len(history):,} rows")
print(f"Snapshot check Jan opening total={snapshot[snapshot.month.astype(str)=='2025-01-01'].opening_subscribers.sum():,} "
      f"Dec closing total={snapshot[snapshot.month.astype(str)=='2025-12-01'].closing_subscribers.sum():,}")

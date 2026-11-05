# Project Documentation — Telecom Revenue & ARPU Analytics

**Company:** PakConnect Telecom (**fictional**) · **Period:** Jan–Dec 2025 · **Currency:** PKR · **Status of data:** 100% simulated.

## 1. Business requirement analysis
Management questions (from the brief): monthly revenue; best services, cities, packages and segments; ARPU trend; active / new / churned subscribers; growth opportunities. These map one-to-one to the SQL files (`sql/03_business_analysis.sql` A–T) and the 4 dashboard pages specified in `powerbi/POWER_BI_BUILD_GUIDE.md`.

## 2. Data source research (done before any dataset was chosen)
Datasets actually inspected on 5 Nov 2026:

| Candidate | Source | What it really contains | Verdict |
|---|---|---|---|
| Telco Customer Churn (blastchar / IBM sample) | Kaggle — https://www.kaggle.com/datasets/blastchar/telco-customer-churn | 7,043 rows × 21 columns, one row per customer, a single snapshot (tenure + MonthlyCharges in USD, US-style services), file `WA_Fn-UseC_-Telco-Customer-Churn.csv`, license: data files © original authors | **Rejected as primary.** No month dimension, no monthly revenue history, no Pakistan cities, no PKR — it cannot produce monthly ARPU for 2025 no matter how it is cleaned. |
| Telecom Customer Churn | Maven Analytics Data Playground — https://mavenanalytics.io/data-playground/telecom-customer-churn | 7,043 fictional California customers, Q2 2022 snapshot, source IBM Cognos sample | **Rejected as primary**, same reason: one quarter, one snapshot, no monthly revenue series. |
| BigQuery public datasets | Google Cloud | No Pakistan telecom operator revenue dataset exists publicly | Not usable for this brief. |

**Decision — hybrid approach, synthetic primary:** a purpose-built simulated dataset for PakConnect (this project), designed exactly at the required grains (customer master, customer-month revenue, city-month subscribers, date dimension). The public churn sets remain documented here as the *optional secondary* reference for churn-modelling extensions; they are **not** merged in, because mixing a US snapshot with simulated PKR monthly revenue would create false precision. No public dataset file was downloaded into this repo, and no synthetic record is claimed to come from any operator.

## 3. Data generation (assumptions, all disclosed)
Script: `src/generate_data.py`, **seed 42**, pure NumPy/Pandas (Faker not needed, so the seed fully reproduces every value).
- Cities weighted Lahore 26%, Karachi 24%, Islamabad 15%, Faisalabad 11%, Multan 9%, Peshawar 8%, Quetta 7%; region mapped consistently.
- 88% of customers form the pre-2025 base (joined 2022–2024); 12% join during Jan–Nov 2025. Customer master therefore represents the 2025 cohort; pre-2025 churn is out of scope by design.
- Churn occurs only in 2025, at least 30 days after joining (~809 customers, 8.1%); churn month is the last billed month.
- Segment spend multipliers vs the package fee anchor: Business 1.3–2.2×, Premium 1.2–1.8×, Family 1.1–1.6×, Mass 0.8–1.3×, Student 0.6–1.0×; Daily/Weekly bundles get a further 0.6–1.0× partial-renewal factor. `monthly_fee` is the monthly-equivalent anchor (documented modelling choice).
- Revenue split centres follow package type (e.g. Data packages ≈70% data revenue; Voice ≈65% voice) with ±3pt noise, renormalised.
- Seasonality factors by month (0.97–1.08) model Ramadan/Eid/year-end uplift — an **assumption**, flagged as circular if "found" later in EDA.
- Discounts: 40% of bills get 0–8% of gross. Tax: flat assumed blended **16%** of net revenue — a modelling assumption, **not** a statutory Pakistan telecom tax rate.
- ~8% of eligible customers switch package once in 2025; `customer_package_history.csv` (10,760 rows) records every assignment, and each revenue row takes the package active in that month.
- Subscriber snapshots are **derived** from join/churn events in the customer master, so the balance identity holds exactly by construction.

## 4. Profiling → Cleaning → Validation
Profiling (`src/profile_data.py`) ran before cleaning; cleaning rules and results are in `data_quality_report.md`; the 19-test QA suite (`src/validate_data.py`) passes 19/19, and SQL results reconcile exactly with Python KPIs (`src/test_sql_logic_sqlite.py`).

## 5. Database design
PostgreSQL star schema in `sql/01_database_schema.sql`: dimensions `dim_customers`, `dim_packages`, `dim_date`; facts `fact_revenue` (grain: 1 row per customer-month, enforced by `UNIQUE(customer_id, month)`) and `fact_subscribers` (grain: 1 row per city-month, composite PK). CHECK constraints encode the revenue and subscriber-balance identities in the database itself. **The two facts are never joined row-to-row** — KPI queries aggregate each fact in its own CTE first (`sql/04_kpi_analysis.sql`).

*Environment note (honest):* this build workspace is Linux with no PostgreSQL server available, so the `.sql` files were logic-tested by running the identical aggregation logic against the same cleaned CSVs in SQLite with exact reconciliation, rather than executed on a live PostgreSQL instance. The DDL is standard PostgreSQL; run steps are in the README and in the Power BI guide, and `02_import_validation.sql` is the on-Postgres proof step.

## 6. Power BI
`.pbix` files can only be authored in Power BI Desktop on Windows, so no finished `.pbix` is shipped from this Linux build. `powerbi/DAX_measures.dax` contains all measures and `powerbi/POWER_BI_BUILD_GUIDE.md` contains the exact model, 4-page layout, slicers, formatting and the reconciliation numbers the finished dashboard must match (Total Revenue PKR 158,009,345; December ARPU PKR 1,527).

## 7. Limitations
1. All findings describe simulated data — they demonstrate method, not market facts.
2. December 2025 new subscribers = 0 is a generator artifact (join window ended 30 Nov).
3. Average active subscribers is a snapshot estimate ((opening+closing)/2), not a daily average.
4. One package per customer per month; multi-SIM / multi-package customers are not modelled.
5. Churn has no reason codes; refunds/adjustments are modelled only as the discount field.
6. GitHub publication: this package is ready to push as repo `telecom-revenue-arpu-analytics` (commands in README) but was not pushed, because no GitHub account is connected in this workspace.

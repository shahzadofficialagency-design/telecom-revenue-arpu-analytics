# Telecom Revenue & ARPU Analytics — PakConnect Telecom

> ⚠️ **Data disclosure:** PakConnect Telecom is a **fictional** operator. **Every record in this project is simulated** (Python/NumPy, fixed seed 42) for portfolio and learning purposes. Nothing here is data from Jazz, Zong, Ufone, Telenor or any real operator, and package prices are project assumptions, not real tariffs.

An end-to-end Data Analytics / BI project: synthetic data generation → profiling → cleaning → EDA → PostgreSQL star schema → SQL KPI analysis → Power BI (DAX + 4-page dashboard build guide) → validated business insights.

## Business problem
Management of a Pakistani telecom operator needs to know: monthly revenue, which services / cities / packages / segments earn most, how ARPU is moving, and how the subscriber base (new, active, churned) is evolving — from one trusted, reconciled reporting pipeline.

## Headline results (simulated data, computed — not hand-typed)
- Total net service revenue 2025: **PKR 158,009,345** (billed incl. tax: PKR 183,290,839)
- Average monthly ARPU: **PKR 1,458** (Jan PKR 1,421 → Dec PKR 1,527)
- Top city by revenue: **Lahore** · Top city by ARPU: **Islamabad** · Top service: **Data (≈47% of gross revenue)**
- Subscribers: 8,762 (Jan opening) → 9,191 (Dec closing); 1,238 new, 809 churn events
- Full findings: [`reports/business_insights.md`](reports/business_insights.md)

## Dataset
| File | Rows | Grain |
|---|---:|---|
| customers.csv | 10,000 | 1 row per customer |
| packages.csv | 10 | 1 row per package |
| revenue.csv | 109,369 | 1 row per customer per month |
| subscriber_snapshot.csv | 84 | 1 row per city per month (7 × 12) |
| dim_date.csv | 365 | 1 row per day, 2025 |
| customer_package_history.csv | 10,760 | 1 row per package assignment period |

Public datasets (Kaggle Telco Churn, Maven Analytics) were researched first and **rejected as the primary source** — they are single snapshots with no monthly revenue history. Full research table and rationale: [`reports/project_documentation.md`](reports/project_documentation.md). Data dictionary: [`reports/data_dictionary.xlsx`](reports/data_dictionary.xlsx) (55 columns + KPI sheet).

## Tech stack
Python (Pandas, NumPy, Matplotlib, Seaborn) · PostgreSQL + SQL (CTEs, window functions) · Power BI + DAX · Excel · Git/GitHub

## KPI definitions (single source of truth)
- **Total Service Revenue** = SUM(net_revenue) — tax excluded, always.
- **Monthly ARPU** = Monthly Net Service Revenue / Average Active Subscribers, where Average Active = (Opening + Closing) / 2 (snapshot estimate, disclosed).
- **City ARPU** = City Monthly Net Revenue / City Average Active Subscribers (same city, same month, both sides).
- **Churn Rate %** = Churned / Opening Subscribers × 100.
- **Revenue Growth %** = (This Month − Last Month) / Last Month × 100.
- **Net Subscriber Growth** = New − Churned.
- **Package Contribution %** = Package Revenue / Total Revenue × 100.
- Never calculate ARPU from `total_billed_amount` — that includes tax.

## Setup (reproduce everything)
```bash
pip install -r requirements.txt
python src/generate_data.py        # recreates data/raw/*.csv exactly (seed 42)
python src/profile_data.py         # profiling -> reports/_profiling_log.txt
python src/clean_data.py           # -> data/processed/*_clean.csv
python src/validate_data.py        # 19 QA tests, must print 19/19
python src/run_eda_and_kpis.py     # charts -> screenshots/, KPIs -> reports/_kpi_results.json
python src/test_sql_logic_sqlite.py  # SQL vs Python reconciliation
```
PostgreSQL: create the DB and tables with `sql/01_database_schema.sql`, import the cleaned CSVs (commands in that file), then run `sql/02_import_validation.sql`, `sql/03_business_analysis.sql`, `sql/04_kpi_analysis.sql`.
Power BI: **the dashboard is in English only** (page names, titles, KPI labels, slicers, tooltips — full list in the guide, §0). Open `powerbi/dashboard_preview_english.html` in any browser to see the finished 4-page English dashboard preview built from the real KPIs. To build the `.pbix`, follow `powerbi/POWER_BI_BUILD_GUIDE.md` (star schema, all DAX in `powerbi/DAX_measures.dax`, 4 pages, reconciliation numbers included). *Note: a `.pbix` can only be authored in Power BI Desktop on Windows, so this repo ships the complete build guide + DAX instead of an untested binary.*
GitHub: `git init && git add . && git commit -m "Telecom Revenue & ARPU Analytics" && git remote add origin https://github.com/<your-username>/telecom-revenue-arpu-analytics.git && git push -u origin main`

## Project structure
```
data/raw/ + data/processed/   notebooks/ (01-04)   src/ (generate, profile, clean, validate, EDA/KPI, SQL test)
sql/ (schema, import validation, business analysis, KPI analysis)
powerbi/ (DAX measures + build guide)   reports/ (dictionary, quality, insights, documentation)   screenshots/ (EDA charts)
```

## Limitations
Simulated data only; December new-subscriber count is a known generator artifact (join window ended 30 Nov); average-active-subscribers is a snapshot estimate; one package per customer-month; seasonality was a modelling assumption, so it cannot be "discovered" as a finding. Details: `reports/project_documentation.md` §7.

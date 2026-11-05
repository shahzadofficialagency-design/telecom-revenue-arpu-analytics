# Power BI Build Guide — Telecom Revenue & ARPU Dashboard

## 0. Language rule (user decision, 5 Nov 2026): ENGLISH ONLY
The entire dashboard is in **English** — page names, KPI card labels, visual titles, axis titles, legends, slicer labels, tooltips and the footer disclosure. Do not use Urdu or Roman Urdu anywhere on the canvas. Use exactly these English titles:
- Pages: **Executive Overview** · **Revenue Analysis** · **Subscriber & ARPU Analysis** · **Package Performance**
- KPI cards: **Total Revenue** · **Monthly ARPU** · **Active Subscribers** · **Revenue Growth %** · **Total Billed Amount** · **Churn Rate**
- Visual titles: **Monthly Revenue Trend** · **Monthly ARPU Trend** · **Revenue by City** · **Revenue by Package** · **Revenue Contribution by Service** · **Voice Revenue** · **Data Revenue** · **SMS Revenue** · **VAS Revenue** · **City Revenue Ranking** · **Package Revenue Ranking** · **New Subscribers vs Churned Subscribers** · **Monthly Subscriber Growth** · **ARPU by City** · **ARPU by Package** · **Package Revenue** · **Package Subscribers** · **Package ARPU** · **Package Ranking**
- Slicers: **Year** · **Month** · **City** · **Region** · **Package Type** · **Customer Segment**
- Footer (still English): *"PakConnect Telecom is fictional. All data is simulated for portfolio purposes (Jan–Dec 2025, PKR)."*
- In Power BI Desktop, also set File → Options → Regional Settings → **English (United States)** so numbers/dates render in English: PKR 158,009,345 · Dec 2025.
An English preview of all 4 pages, built from the real computed KPIs, is in `powerbi/dashboard_preview_english.html` — open it in any browser to see exactly how the finished dashboard should look and read.

> **Why there is no finished .pbix in this package — read first.**
> A `.pbix` file can only be authored in **Power BI Desktop, which runs on Windows**. This project was built in a Linux workspace, so a genuine `.pbix` cannot be produced or verified here, and shipping an untested binary would be dishonest. Instead this guide + `DAX_measures.dax` give you everything needed to build the exact dashboard in about 30–45 minutes on a Windows PC, step by step. When you save it, place it at `powerbi/telecom_revenue_arpu_dashboard.pbix`.
> All data is **simulated** (fictional PakConnect Telecom) — add the disclosure text in step 6 to the report itself.

## 1. Load the data (PostgreSQL)
1. Start PostgreSQL, run `sql/01_database_schema.sql`, then import the 5 cleaned CSVs (import order and `\copy` commands are at the bottom of that file), then run `sql/02_import_validation.sql` — all counts must match.
2. Power BI Desktop → **Get Data → PostgreSQL database** → server `localhost`, database `telecom_analytics` → load all 5 tables.
   *(Simpler alternative for a first build: Get Data → Text/CSV and load the 5 files from `data/processed/` directly. The model below is identical.)*

## 2. Build the star schema (Model view)
Create these one-to-many, single-direction relationships:
- `dim_customers[customer_id]` (1) → `fact_revenue[customer_id]` (*)
- `dim_packages[package_id]` (1) → `fact_revenue[package_id]` (*)
- `dim_date[date]` (1) → `fact_revenue[month]` (*)  *(month is month-start, so it matches a date row)*
- `dim_date[date]` (1) → `fact_subscribers[month]` (*)
- Mark `dim_date` as the **date table** (right-click → Mark as date table → `date`).
- Hide the key columns on the fact (many) side. **Never** create a relationship between `fact_revenue` and `fact_subscribers` — different grains (customer-month vs city-month); ARPU works through the shared dimensions + the DAX measure.

## 3. Add the measures
Modelling → New Measure, paste each measure from `DAX_measures.dax`. Format: Total Revenue / Billed = Currency `PKR #,0`; ARPU = `PKR #,0.00`; Churn Rate and Growth % = Percentage.

## 4. Build the 4 pages
**Page 1 — Executive Overview.** Cards: Total Revenue, Monthly ARPU (with Month slicer set to latest month), Active Subscribers, Revenue Growth %. Charts: line = Monthly Revenue Trend (`dim_date[year_month]` × Total Revenue); line = Monthly ARPU Trend; bar = Revenue by City (`dim_customers[city]`); bar = Revenue by Package (`dim_packages[package_name]`); pie/donut = service mix (Voice/Data/SMS/VAS Revenue measures as values).
**Page 2 — Revenue Analysis.** Four cards (Voice, Data, SMS, VAS Revenue), clustered column = monthly revenue by service, sorted bar = City Revenue Ranking, sorted bar = Package Revenue Ranking, 100% stacked bar = monthly contribution.
**Page 3 — Subscriber & ARPU Analysis.** Line = closing subscribers by month; clustered column = New vs Churned Subscribers; line = Churn Rate; bar = ARPU by City (City ARPU measure × `dim_customers[city]`); bar = ARPU by Package (Avg Revenue per Customer Month × package).
**Page 4 — Package Performance.** Bar = Package Revenue; bar = Billed Customers by package; bar = Package ARPU; table = Package Ranking (name, type, revenue, contribution %, ARPU); line = package revenue trend with package legend.

## 5. Slicers (every page, synced where sensible)
Year (`dim_date[year]`), Month (`dim_date[month_name]`), City (`dim_customers[city]`), Region (`dim_customers[region]`), Package Type (`dim_packages[package_type]`), Customer Segment (`dim_customers[segment]`). Add page-navigation buttons between the 4 pages.

## 6. Formatting & honesty label
Theme: one accent colour (e.g. deep teal #0F766E) + greys; titles in Segoe UI Semibold; KPI numbers `PKR #,0`. Add a small text box in the footer of Page 1: *"PakConnect Telecom is fictional. All data is simulated for portfolio purposes (Jan–Dec 2025, PKR)."* — this disclosure must stay on the dashboard.
Export each finished page as PNG into `screenshots/` (File → Export, or screenshot the canvas) as `dashboard_page1_executive.png`, etc.

## 7. Reconciliation check before publishing
Set all slicers to "All": the Total Revenue card must read **PKR 158,009,345** and December ARPU **PKR 1,527** — the same numbers Python and SQL produced. If they differ, a relationship is wrong (usually a fact-to-fact join or a bi-directional filter).

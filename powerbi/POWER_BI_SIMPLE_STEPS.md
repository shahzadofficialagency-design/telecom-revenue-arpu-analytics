# Power BI — Bilkul Simple Steps (Roman Urdu)

> Ye guide 5th class simple hai: **ek step mein ek chhota kaam.**
> Dashboard **English mein** hoga — page, card aur chart ke naam English mein likhne hain (neeche exact naam diye hain).
> Data **simulated** hai (fictional PakConnect Telecom) — ye baat dashboard par likhni hai, aur isay asli Jazz/Zong/Ufone/Telenor data kabhi na kehna.

## Pehle ye tayyar rakhein

1. Apna **Windows PC** kholein. (Power BI Desktop sirf Windows par chalta hai.)
2. **Power BI Desktop** install karein — ye Microsoft ka free program hai. Microsoft Store mein ja kar "Power BI Desktop" likh kar install karein.
3. Project wali ZIP file ko kholein (unzip karein). Us ke andar `telecom-revenue-arpu-analytics` folder hoga.
4. Us folder ke andar `data/processed/` folder dhoondhein. Us mein ye **5 files** honi chahiye:
   - `customers_clean.csv`
   - `packages_clean.csv`
   - `revenue_clean.csv`
   - `subscriber_snapshot_clean.csv`
   - `dim_date_clean.csv`

---

## Hissa 1 — 5 files load karein (PostgreSQL ki zaroorat nahi)

1. Power BI Desktop kholein.
2. Upar **Get Data** par click karein.
3. **Text/CSV** chunein.
4. `data/processed/` folder mein ja kar `customers_clean.csv` chunein, phir **Load** dabayein.
5. Yehi kaam baaki 4 files ke liye bhi karein — ek ek kar ke:
   - `packages_clean.csv` → Load
   - `revenue_clean.csv` → Load (ye sab se bari file hai, thora waqt le gi — ghabrayein nahi)
   - `subscriber_snapshot_clean.csv` → Load
   - `dim_date_clean.csv` → Load
6. Daayein taraf **Fields** mein 5 tables nazar aani chahiye. Agar 5 dikh rahi hain, to Hissa 1 mukammal hai.

> Note: Is guide mein PostgreSQL use nahi ho raha. CSV se seedha load karna sab se asaan tareeqa hai, aur result bilkul waisa hi banta hai.

## Hissa 2 — Tables ko jorein (Model view)

"Jorna" ka matlab hai: Power BI ko batana ke kaunsi table kis se milti hai.

1. Baayein taraf **Model view** (teesra icon, do table wala) par click karein.
2. Tables ko kheench kar (drag kar ke) saaf saaf laga lein.
3. Ab ye **4 jor** banayein — pehli table ke column ko pakar kar doosri table ke column par chhorein:
   - `customers_clean[customer_id]` → `revenue_clean[customer_id]`
   - `packages_clean[package_id]` → `revenue_clean[package_id]`
   - `dim_date_clean[date]` → `revenue_clean[month]`
   - `dim_date_clean[date]` → `subscriber_snapshot_clean[month]`
4. Har jor par line ban jaye gi. Line par click kar ke dekhein: **1** wali taraf dim table ho, **\*** (star) wali taraf revenue/snapshot table ho.
5. **Ye jor kabhi na banayein:** `revenue_clean` ko seedha `subscriber_snapshot_clean` se na jorein. Ye dono alag hisaab ki tables hain — in ko jorne se number ghalat ho jayein ge.
6. `dim_date_clean` table par right-click karein → **Mark as date table** → `date` chunein.

## Hissa 3 — 4 measures banayein (copy-paste)

"Measure" ka matlab hai: ek formula jo number nikaal kar deta hai. Aap ko likhna nahi, sirf copy-paste karna hai.

1. Upar **Modeling** tab par click karein, phir **New Measure** dabayein.
2. Jo khaali jagah khule, wahan neeche wala pehla formula paste karein, phir **Enter** dabayein.
3. Yehi kaam baaki 3 formulas ke liye bhi karein — ek ek kar ke.

**1. Total Revenue** (tax ke baghair asli service revenue):
```
Total Revenue = SUM ( revenue_clean[net_revenue] )
```

**2. Total Billed Amount** (tax ke saath kul bill):
```
Total Billed Amount = SUM ( revenue_clean[total_billed_amount] )
```

**3. Active Subscribers** (ausat active subscribers):
```
Active Subscribers = AVERAGE ( subscriber_snapshot_clean[average_active_subscribers] )
```

**4. Monthly ARPU** (har user se ausat mahana revenue):
```
Monthly ARPU = DIVIDE ( [Total Revenue], [Active Subscribers], 0 )
```

> Baaki measures (Voice/Data/SMS/VAS Revenue, Churn Rate, Revenue Growth %, waghera) `powerbi/DAX_measures.dax` file mein likhe hain — jab Page 2 aur 3 banayein ge, wahan se copy-paste kar lein. Pehle Page 1 mukammal karein.

## Hissa 4 — Page 1 banayein: Executive Overview

1. Neeche page ka naam par double-click karein aur naam badal kar **Executive Overview** likhein.
2. **4 Cards** banayein (Insert → Card, ya Visualizations mein Card chunein):
   - Card 1: **Total Revenue** — Field mein `Total Revenue` measure daalein.
   - Card 2: **Monthly ARPU** — Field mein `Monthly ARPU` measure daalein.
   - Card 3: **Active Subscribers** — Field mein `Active Subscribers` measure daalein.
   - Card 4: **Total Billed Amount** — Field mein `Total Billed Amount` measure daalein.
3. **Monthly Revenue Trend** (line chart): X-axis mein `dim_date_clean[year_month]`, Values mein `Total Revenue`.
4. **Monthly ARPU Trend** (line chart): X-axis mein `dim_date_clean[year_month]`, Values mein `Monthly ARPU`.
5. **Revenue by City** (bar chart): Y-axis mein `customers_clean[city]`, Values mein `Total Revenue`.
6. **Revenue by Package** (bar chart): Y-axis mein `packages_clean[package_name]`, Values mein `Total Revenue`.
7. Page 1 ke neeche chhota sa text box banayein aur ye line likhein (English mein, yehi lafz):
   - *"PakConnect Telecom is fictional. All data is simulated for portfolio purposes (Jan–Dec 2025, PKR)."*
8. Upar **File → Options → Regional Settings** mein ja kar **English (United States)** chunein, taake number English mein dikhein.

## Hissa 5 — Check karein: number sahi hai ya nahi?

Ye sab se zaroori check hai. Saare slicer "All" par rakhein, phir dekhein:

- **Total Revenue card par PKR 158,009,345 aana chahiye.**
- Month ko **December 2025** par rakhein to **Monthly ARPU PKR 1,527** aana chahiye.

Agar number yehi hai, to sab sahi hai — mubarak ho, Page 1 tayyar hai!

Agar number mukhtalif hai, to sab se pehle Hissa 2 ke jor (relationships) dobara dekhein — aksar ghalti wahan hoti hai (khaas tor par revenue aur subscriber tables ko aapas mein jorna).

## Hissa 6 — File save karein

1. **File → Save As** karein.
2. File ko is jagah save karein: `powerbi/telecom_revenue_arpu_dashboard.pbix`
3. Naam bilkul yehi rakhein: `telecom_revenue_arpu_dashboard.pbix`

## Baaki 3 pages (jab Page 1 tayyar ho jaye)

Page 1 ke baad ye 3 pages banayein — har page ka naam aur charts `powerbi/POWER_BI_BUILD_GUIDE.md` (Hissa 4) mein likhe hain, aur preview `powerbi/dashboard_preview_english.html` ko browser mein khol kar dekh sakte hain ke har page kaisa lagna chahiye:

- **Page 2 — Revenue Analysis:** Voice, Data, SMS, VAS Revenue ke 4 cards; City aur Package ranking.
- **Page 3 — Subscriber & ARPU Analysis:** New vs Churned Subscribers, Churn Rate, ARPU by City, ARPU by Package.
- **Page 4 — Package Performance:** Package Revenue, Package Subscribers, Package ARPU, Package Ranking table.

Har page par ye **slicers** lagayein: Year, Month, City, Region, Package Type, Customer Segment.

Har page ka screenshot `screenshots/` folder mein `dashboard_page1_executive.png` jaisi naming se save karein.

---

*Source: `powerbi/POWER_BI_BUILD_GUIDE.md` aur `powerbi/DAX_measures.dax` — ye simple guide unhi ki asaan Roman Urdu shakal hai. Reconciliation numbers: Total Revenue PKR 158,009,345; December 2025 ARPU PKR 1,527 (Python aur SQL dono se tasdeeq shuda).*

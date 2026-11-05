# Data Dictionary — PakConnect Telecom (FICTIONAL, simulated data)

> This Markdown version mirrors `data_dictionary.xlsx` (same content, text form). All data is simulated.


## Data Dictionary

| File | Column | Data Type | Description / Business Rule |
|---|---|---|---|
| customers.csv | customer_id | String | Unique customer identifier, format CUST00001 |
| customers.csv | gender | String | Male / Female |
| customers.csv | age | Integer | Customer age, 18-70 in simulated data |
| customers.csv | city | String | One of 7 cities: Lahore, Karachi, Islamabad, Faisalabad, Multan, Peshawar, Quetta |
| customers.csv | region | String | Province/territory consistent with city |
| customers.csv | join_date | Date | Registration date; 88% in 2022-2024, 12% during Jan-Nov 2025 |
| customers.csv | segment | String | Mass / Premium / Business / Student / Family |
| customers.csv | customer_type | String | Prepaid / Postpaid |
| customers.csv | status | String | Active / Churned (derived from churn_date) |
| customers.csv | contract_type | String | Month-to-Month / One Year / Two Year |
| customers.csv | auto_payment | Boolean | Auto-payment enabled |
| customers.csv | churn_date | Date | EXTRA audit column beyond the brief minimum: churn date in 2025, empty for Active. Without it 'no revenue after churn' cannot be verified. |
| packages.csv | package_id | String | PKG01-PKG10 |
| packages.csv | package_name | String | Fictional package name (project assumption, not a real tariff) |
| packages.csv | package_type | String | Data / Voice / Hybrid / Business |
| packages.csv | monthly_fee | Decimal (PKR) | Catalogue monthly-equivalent spend anchor |
| packages.csv | voice_minutes | Integer | Included voice minutes |
| packages.csv | sms_limit | Integer | Included SMS |
| packages.csv | data_limit_gb | Decimal | Included data (GB) |
| packages.csv | validity_days | Integer | Bundle validity in days |
| packages.csv | package_status | String | Active |
| revenue.csv | revenue_id | String | REV000001... unique |
| revenue.csv | customer_id | String | FK to customers |
| revenue.csv | month | Date | Month-start date (YYYY-MM-01) - the single date convention used everywhere |
| revenue.csv | package_id | String | FK to packages; package active for that customer in that month per customer_package_history |
| revenue.csv | voice_revenue | Decimal (PKR) | Voice service revenue for the month |
| revenue.csv | data_revenue | Decimal (PKR) | Data service revenue |
| revenue.csv | sms_revenue | Decimal (PKR) | SMS service revenue |
| revenue.csv | vas_revenue | Decimal (PKR) | Value-added services revenue |
| revenue.csv | discount | Decimal (PKR) | Discount, 0-8% of gross, never exceeds gross |
| revenue.csv | net_revenue | Decimal (PKR) | nan |
| revenue.csv | tax_amount | Decimal (PKR) | Tax at assumed blended 16% of net (modelling assumption, not a statutory rate). Kept separate from service revenue. |
| revenue.csv | total_billed_amount | Decimal (PKR) | nan |
| subscriber_snapshot.csv | month | Date | Month-start date |
| subscriber_snapshot.csv | city | String | City (7 per month, 84 rows total) |
| subscriber_snapshot.csv | opening_subscribers | Integer | Active subscribers at month start |
| subscriber_snapshot.csv | new_subscribers | Integer | Customers whose join_date falls in the month |
| subscriber_snapshot.csv | churned_subscribers | Integer | Customers whose churn_date falls in the month |
| subscriber_snapshot.csv | closing_subscribers | Integer | nan |
| subscriber_snapshot.csv | average_active_subscribers | Decimal | nan |
| dim_date.csv | date | Date | Calendar date, 2025-01-01 to 2025-12-31 (365 rows) |
| dim_date.csv | day | Integer | Day of month |
| dim_date.csv | month | Integer | Month number 1-12 |
| dim_date.csv | month_name | String | January-December |
| dim_date.csv | month_start | Date | First day of the month (join key for monthly facts) |
| dim_date.csv | quarter | Integer | 1-4 |
| dim_date.csv | year | Integer | 2025 |
| dim_date.csv | year_month | String | YYYY-MM |
| dim_date.csv | weekday | Integer | 0=Monday ... 6=Sunday |
| dim_date.csv | weekday_name | String | Monday-Sunday |
| customer_package_history.csv | customer_id | String | FK to customers |
| customer_package_history.csv | package_id | String | Package held in the effective period |
| customer_package_history.csv | effective_start_date | Date | Start of package assignment |
| customer_package_history.csv | effective_end_date | Date | End of package assignment (churn date or 2025-12-31) |
| customer_package_history.csv | change_reason | String | Initial Activation / Upgrade / Downgrade / Promotion |

## KPI Definitions

| KPI | Formula | Notes |
|---|---|---|
| Total Service Revenue | SUM(net_revenue) | Tax EXCLUDED. Never use total_billed_amount. |
| Monthly ARPU | Monthly net service revenue / average active subscribers | Average active = (opening+closing)/2 from snapshots - an estimate, disclosed. |
| City ARPU | City monthly net revenue / city average active subscribers | Numerator and denominator must be the SAME city and month. |
| Revenue Growth % | (This month revenue - last month revenue)/last month revenue x 100 | January has no previous month in-period: blank/NULL. |
| Churn Rate % | Churned subscribers / opening subscribers x 100 | Not churned/closing, not inactive customers. |
| Net Subscriber Growth | New subscribers - churned subscribers | nan |
| Package Contribution % | Package revenue / total revenue x 100 | Window total as denominator in SQL/DAX. |
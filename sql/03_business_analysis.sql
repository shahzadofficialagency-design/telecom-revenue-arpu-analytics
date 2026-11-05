-- ============================================================
-- 03_business_analysis.sql - PakConnect Telecom (FICTIONAL, simulated data)
-- All revenue figures are NET SERVICE revenue (PKR, tax excluded)
-- unless a query explicitly says billed. ARPU lives in 04_kpi_analysis.sql.
-- ============================================================

-- A. Total Revenue -------------------------------------------------
-- Business Q: How much service revenue did we earn in 2025?
SELECT SUM(net_revenue) AS total_service_revenue_pkr,
       SUM(total_billed_amount) AS total_billed_pkr,
       SUM(tax_amount) AS total_tax_pkr
FROM fact_revenue;

-- B. Monthly Revenue ----------------------------------------------
SELECT month, SUM(net_revenue) AS revenue,
       COUNT(DISTINCT customer_id) AS billed_customers
FROM fact_revenue GROUP BY month ORDER BY month;

-- C. Month-over-Month Revenue Growth (window function) -------------
WITH m AS (SELECT month, SUM(net_revenue) AS revenue FROM fact_revenue GROUP BY month)
SELECT month, revenue,
       LAG(revenue) OVER (ORDER BY month) AS prev_month_revenue,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY month))
             / NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100, 2) AS growth_pct
FROM m ORDER BY month;

-- D. Revenue by City ----------------------------------------------
SELECT c.city, c.region, SUM(r.net_revenue) AS revenue,
       ROUND(SUM(r.net_revenue) * 100.0 / SUM(SUM(r.net_revenue)) OVER (), 2) AS contribution_pct
FROM fact_revenue r JOIN dim_customers c ON c.customer_id = r.customer_id
GROUP BY c.city, c.region ORDER BY revenue DESC;

-- E. Revenue by Package --------------------------------------------
SELECT p.package_name, p.package_type, SUM(r.net_revenue) AS revenue,
       COUNT(DISTINCT r.customer_id) AS customers
FROM fact_revenue r JOIN dim_packages p ON p.package_id = r.package_id
GROUP BY p.package_name, p.package_type ORDER BY revenue DESC;

-- F. Revenue by Customer Segment -----------------------------------
SELECT c.segment, SUM(r.net_revenue) AS revenue,
       COUNT(DISTINCT r.customer_id) AS customers,
       ROUND(SUM(r.net_revenue) / COUNT(DISTINCT r.customer_id), 2) AS revenue_per_customer
FROM fact_revenue r JOIN dim_customers c ON c.customer_id = r.customer_id
GROUP BY c.segment ORDER BY revenue DESC;

-- G-J. Service Mix (Voice / Data / SMS / VAS) -----------------------
SELECT SUM(voice_revenue) AS voice, SUM(data_revenue) AS data_rev,
       SUM(sms_revenue) AS sms, SUM(vas_revenue) AS vas,
       SUM(net_revenue) AS net_revenue,
       ROUND(SUM(data_revenue) * 100.0 / SUM(net_revenue), 2) AS data_share_pct
FROM fact_revenue;

-- Monthly service mix (long format for stacked charts)
SELECT month, 'Voice' AS service, SUM(voice_revenue) AS revenue FROM fact_revenue GROUP BY month
UNION ALL SELECT month, 'Data', SUM(data_revenue) FROM fact_revenue GROUP BY month
UNION ALL SELECT month, 'SMS', SUM(sms_revenue) FROM fact_revenue GROUP BY month
UNION ALL SELECT month, 'VAS', SUM(vas_revenue) FROM fact_revenue GROUP BY month
ORDER BY month, service;

-- K-M. Subscribers: Active / New / Churned --------------------------
SELECT month,
       SUM(opening_subscribers) AS opening_subs,
       SUM(new_subscribers) AS new_subs,
       SUM(churned_subscribers) AS churned_subs,
       SUM(closing_subscribers) AS closing_subs,
       SUM(average_active_subscribers) AS avg_active_subs
FROM fact_subscribers GROUP BY month ORDER BY month;

-- N. Churn Rate -----------------------------------------------------
-- Definition: churned / opening subscribers x 100 (see KPI doc).
SELECT month,
       ROUND(SUM(churned_subscribers) * 100.0 / NULLIF(SUM(opening_subscribers), 0), 2) AS churn_rate_pct
FROM fact_subscribers GROUP BY month ORDER BY month;

-- Q. Package Performance (revenue + share + avg revenue per user-month)
SELECT p.package_name,
       SUM(r.net_revenue) AS revenue,
       ROUND(SUM(r.net_revenue) * 100.0 / SUM(SUM(r.net_revenue)) OVER (), 2) AS contribution_pct,
       ROUND(AVG(r.net_revenue), 2) AS avg_revenue_per_customer_month
FROM fact_revenue r JOIN dim_packages p ON p.package_id = r.package_id
GROUP BY p.package_name ORDER BY revenue DESC;

-- R. Customer Revenue Distribution ---------------------------------
SELECT CASE WHEN rev < 500 THEN '< 500' WHEN rev < 1000 THEN '500-999'
            WHEN rev < 2000 THEN '1,000-1,999' WHEN rev < 3500 THEN '2,000-3,499'
            ELSE '3,500+' END AS monthly_spend_band,
       COUNT(*) AS customer_months
FROM (SELECT customer_id, month, SUM(net_revenue) AS rev
      FROM fact_revenue GROUP BY customer_id, month) x
GROUP BY 1 ORDER BY MIN(rev);

-- S. Revenue Contribution % by City (same pattern works for package/segment)
-- See D and Q - contribution uses a window total, not a hard-coded denominator.

-- T. Best and Worst Performing Months -------------------------------
(SELECT month, SUM(net_revenue) AS revenue, 'Best' AS label
 FROM fact_revenue GROUP BY month ORDER BY revenue DESC LIMIT 3)
UNION ALL
(SELECT month, SUM(net_revenue) AS revenue, 'Worst'
 FROM fact_revenue GROUP BY month ORDER BY revenue ASC LIMIT 3)
ORDER BY revenue DESC;

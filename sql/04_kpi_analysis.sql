-- ============================================================
-- 04_kpi_analysis.sql - KPI layer. Definitions (also in README):
--   Total Service Revenue = SUM(net_revenue)  [tax EXCLUDED]
--   Monthly ARPU   = Monthly Net Service Revenue / Average Active Subscribers
--   City ARPU      = City Monthly Net Revenue / City Average Active Subscribers
--   Churn Rate %   = Churned Subscribers / Opening Subscribers x 100
--   Net Growth     = New Subscribers - Churned Subscribers
--   Revenue Growth % = (This Month - Last Month) / Last Month x 100
--
-- CORRECT JOIN PATTERN: fact_revenue (customer-month grain) and
-- fact_subscribers (city-month grain) are aggregated SEPARATELY in
-- CTEs, then joined on the shared key (month, or month+city).
-- Joining the raw facts would multiply rows and double-count.
-- Average Active Subscribers = (Opening + Closing)/2 - an estimate
-- from monthly snapshots, disclosed in the documentation.
-- ============================================================

-- O. Monthly ARPU ---------------------------------------------------
WITH rev AS (
    SELECT month, SUM(net_revenue) AS revenue FROM fact_revenue GROUP BY month
),
subs AS (
    SELECT month, SUM(average_active_subscribers) AS avg_active,
           SUM(opening_subscribers) AS opening, SUM(new_subscribers) AS new_subs,
           SUM(churned_subscribers) AS churned
    FROM fact_subscribers GROUP BY month
)
SELECT r.month, r.revenue, s.avg_active,
       ROUND(r.revenue / NULLIF(s.avg_active, 0), 2) AS monthly_arpu_pkr,
       ROUND(s.churned * 100.0 / NULLIF(s.opening, 0), 2) AS churn_rate_pct,
       (s.new_subs - s.churned) AS net_subscriber_growth,
       ROUND((r.revenue - LAG(r.revenue) OVER (ORDER BY r.month))
             / NULLIF(LAG(r.revenue) OVER (ORDER BY r.month), 0) * 100, 2) AS revenue_growth_pct
FROM rev r JOIN subs s ON s.month = r.month
ORDER BY r.month;

-- P. City-wise ARPU --------------------------------------------------
WITH rev AS (
    SELECT r.month, c.city, SUM(r.net_revenue) AS revenue
    FROM fact_revenue r JOIN dim_customers c ON c.customer_id = r.customer_id
    GROUP BY r.month, c.city
)
SELECT rev.month, rev.city, rev.revenue, s.average_active_subscribers,
       ROUND(rev.revenue / NULLIF(s.average_active_subscribers, 0), 2) AS city_arpu_pkr
FROM rev JOIN fact_subscribers s ON s.month = rev.month AND s.city = rev.city
ORDER BY rev.month, city_arpu_pkr DESC;

-- City ARPU - full year ranking
WITH rev AS (
    SELECT c.city, SUM(r.net_revenue) AS revenue
    FROM fact_revenue r JOIN dim_customers c ON c.customer_id = r.customer_id
    GROUP BY c.city
),
subs AS (
    SELECT city, AVG(average_active_subscribers) AS avg_active
    FROM fact_subscribers GROUP BY city
)
SELECT rev.city, rev.revenue,
       ROUND(rev.revenue / 12 / NULLIF(subs.avg_active, 0), 2) AS avg_monthly_arpu_pkr
FROM rev JOIN subs ON subs.city = rev.city
ORDER BY avg_monthly_arpu_pkr DESC;

-- Package ARPU (average net revenue per customer-month on the package)
SELECT p.package_name, p.package_type,
       COUNT(*) AS customer_months,
       ROUND(SUM(r.net_revenue) / COUNT(*), 2) AS package_arpu_pkr
FROM fact_revenue r JOIN dim_packages p ON p.package_id = r.package_id
GROUP BY p.package_name, p.package_type ORDER BY package_arpu_pkr DESC;

-- KPI summary card values (whole period)
SELECT
  (SELECT SUM(net_revenue) FROM fact_revenue) AS total_service_revenue_pkr,
  (SELECT SUM(net_revenue) FROM fact_revenue) / 12 AS avg_monthly_revenue_pkr,
  (SELECT ROUND(SUM(churned_subscribers) * 100.0 / SUM(opening_subscribers), 2)
   FROM (SELECT DISTINCT month, opening_subscribers, churned_subscribers
         FROM fact_subscribers) s) AS note_see_monthly_churn_above;

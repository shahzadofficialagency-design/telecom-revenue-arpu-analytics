-- ============================================================
-- 02_import_validation.sql - run right after importing CSVs.
-- Every query should return 0 (or the stated expected value).
-- ============================================================

-- Row counts (expected: 10000 / 10 / ~110000 / 84 / 365)
SELECT 'dim_customers' AS tbl, COUNT(*) AS rows FROM dim_customers
UNION ALL SELECT 'dim_packages', COUNT(*) FROM dim_packages
UNION ALL SELECT 'fact_revenue', COUNT(*) FROM fact_revenue
UNION ALL SELECT 'fact_subscribers', COUNT(*) FROM fact_subscribers
UNION ALL SELECT 'dim_date', COUNT(*) FROM dim_date;

-- Duplicate customer-month revenue records (expected 0)
SELECT COUNT(*) AS duplicate_customer_months FROM (
    SELECT customer_id, month FROM fact_revenue
    GROUP BY customer_id, month HAVING COUNT(*) > 1
) d;

-- Orphan revenue rows (expected 0 / 0 - FKs should already guarantee this)
SELECT (SELECT COUNT(*) FROM fact_revenue r LEFT JOIN dim_customers c
        ON c.customer_id = r.customer_id WHERE c.customer_id IS NULL) AS bad_customer_refs,
       (SELECT COUNT(*) FROM fact_revenue r LEFT JOIN dim_packages p
        ON p.package_id = r.package_id WHERE p.package_id IS NULL) AS bad_package_refs;

-- Revenue arithmetic mismatches (expected 0 / 0)
SELECT
  SUM(CASE WHEN ABS(net_revenue - (voice_revenue+data_revenue+sms_revenue+vas_revenue-discount)) >= 0.01 THEN 1 ELSE 0 END) AS net_mismatch,
  SUM(CASE WHEN ABS(total_billed_amount - (net_revenue + tax_amount)) >= 0.01 THEN 1 ELSE 0 END) AS billed_mismatch
FROM fact_revenue;

-- Subscriber balance mismatches (expected 0)
SELECT COUNT(*) AS balance_mismatch FROM fact_subscribers
WHERE closing_subscribers <> opening_subscribers + new_subscribers - churned_subscribers;

-- Revenue before join or after churn month (expected 0 / 0)
SELECT
  SUM(CASE WHEN r.month < DATE_TRUNC('month', c.join_date)::date THEN 1 ELSE 0 END) AS before_join,
  SUM(CASE WHEN c.churn_date IS NOT NULL
            AND r.month > DATE_TRUNC('month', c.churn_date)::date THEN 1 ELSE 0 END) AS after_churn
FROM fact_revenue r JOIN dim_customers c ON c.customer_id = r.customer_id;

-- Negative money or counts anywhere (expected 0)
SELECT COUNT(*) AS negatives FROM fact_revenue
WHERE LEAST(voice_revenue, data_revenue, sms_revenue, vas_revenue, discount, tax_amount) < 0;

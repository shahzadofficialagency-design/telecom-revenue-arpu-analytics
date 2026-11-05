-- ============================================================
-- PakConnect Telecom (FICTIONAL) - PostgreSQL Schema
-- Database: telecom_analytics
-- Data is SIMULATED (synthetic, seed 42). Not real operator data.
--
-- TABLE GRAINS (read before joining anything):
--   dim_customers        : 1 row per customer
--   dim_packages         : 1 row per package
--   dim_date             : 1 row per calendar day
--   fact_revenue         : 1 row per customer per month (one package
--                          per customer-month; package comes from
--                          customer_package_history for that month)
--   fact_subscribers     : 1 row per city per month
-- WARNING: fact_revenue and fact_subscribers have DIFFERENT grains.
-- Never join them row-to-row. Combine them only after aggregating
-- each to the same level (e.g. month, or city-month) - see
-- 04_kpi_analysis.sql for the correct pattern.
-- ============================================================

CREATE DATABASE telecom_analytics;
-- \c telecom_analytics

CREATE TABLE dim_customers (
    customer_id    VARCHAR(10) PRIMARY KEY,
    gender         VARCHAR(10)  NOT NULL,
    age            INTEGER      NOT NULL CHECK (age BETWEEN 18 AND 100),
    city           VARCHAR(50)  NOT NULL,
    region         VARCHAR(60)  NOT NULL,
    join_date      DATE         NOT NULL,
    segment        VARCHAR(20)  NOT NULL,
    customer_type  VARCHAR(10)  NOT NULL CHECK (customer_type IN ('Prepaid','Postpaid')),
    status         VARCHAR(10)  NOT NULL CHECK (status IN ('Active','Churned')),
    contract_type  VARCHAR(20)  NOT NULL,
    auto_payment   BOOLEAN      NOT NULL,
    churn_date     DATE,
    CHECK (churn_date IS NULL OR churn_date > join_date),
    CHECK ((status = 'Churned') = (churn_date IS NOT NULL))
);

CREATE TABLE dim_packages (
    package_id     VARCHAR(10) PRIMARY KEY,
    package_name   VARCHAR(50)  NOT NULL UNIQUE,
    package_type   VARCHAR(20)  NOT NULL,
    monthly_fee    NUMERIC(10,2) NOT NULL CHECK (monthly_fee > 0),
    voice_minutes  INTEGER      NOT NULL CHECK (voice_minutes >= 0),
    sms_limit      INTEGER      NOT NULL CHECK (sms_limit >= 0),
    data_limit_gb  NUMERIC(8,2) NOT NULL CHECK (data_limit_gb >= 0),
    validity_days  INTEGER      NOT NULL CHECK (validity_days > 0),
    package_status VARCHAR(10)  NOT NULL
);

CREATE TABLE dim_date (
    date          DATE PRIMARY KEY,
    day           INTEGER NOT NULL,
    month         INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_name    VARCHAR(12) NOT NULL,
    month_start   DATE    NOT NULL,
    quarter       INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    year          INTEGER NOT NULL,
    year_month    CHAR(7) NOT NULL,
    weekday       INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),  -- 0 = Monday
    weekday_name  VARCHAR(10) NOT NULL
);

CREATE TABLE fact_revenue (
    revenue_id          VARCHAR(12) PRIMARY KEY,
    customer_id         VARCHAR(10) NOT NULL REFERENCES dim_customers(customer_id),
    month               DATE        NOT NULL,  -- always month-start (YYYY-MM-01)
    package_id          VARCHAR(10) NOT NULL REFERENCES dim_packages(package_id),
    voice_revenue       NUMERIC(12,2) NOT NULL CHECK (voice_revenue >= 0),
    data_revenue        NUMERIC(12,2) NOT NULL CHECK (data_revenue >= 0),
    sms_revenue         NUMERIC(12,2) NOT NULL CHECK (sms_revenue >= 0),
    vas_revenue         NUMERIC(12,2) NOT NULL CHECK (vas_revenue >= 0),
    discount            NUMERIC(12,2) NOT NULL CHECK (discount >= 0),
    net_revenue         NUMERIC(12,2) NOT NULL,
    tax_amount          NUMERIC(12,2) NOT NULL CHECK (tax_amount >= 0),
    total_billed_amount NUMERIC(12,2) NOT NULL,
    UNIQUE (customer_id, month),  -- enforces the grain: 1 package per customer-month
    CHECK (ABS(net_revenue - (voice_revenue + data_revenue + sms_revenue + vas_revenue - discount)) < 0.01),
    CHECK (ABS(total_billed_amount - (net_revenue + tax_amount)) < 0.01)
);

CREATE TABLE fact_subscribers (
    month                     DATE        NOT NULL,  -- month-start
    city                      VARCHAR(50) NOT NULL,
    opening_subscribers       INTEGER NOT NULL CHECK (opening_subscribers >= 0),
    new_subscribers           INTEGER NOT NULL CHECK (new_subscribers >= 0),
    churned_subscribers       INTEGER NOT NULL CHECK (churned_subscribers >= 0),
    closing_subscribers       INTEGER NOT NULL CHECK (closing_subscribers >= 0),
    average_active_subscribers NUMERIC(12,2) NOT NULL,
    PRIMARY KEY (month, city),
    CHECK (closing_subscribers = opening_subscribers + new_subscribers - churned_subscribers),
    CHECK (ABS(average_active_subscribers - (opening_subscribers + closing_subscribers) / 2.0) < 0.01)
);

CREATE INDEX idx_fact_revenue_month    ON fact_revenue(month);
CREATE INDEX idx_fact_revenue_package  ON fact_revenue(package_id);
CREATE INDEX idx_dim_customers_city    ON dim_customers(city);
CREATE INDEX idx_dim_customers_segment ON dim_customers(segment);
CREATE INDEX idx_dim_date_month_start  ON dim_date(month_start);

-- ---------------------------------------------------------------
-- IMPORT (run from psql, after schema, paths relative to project root)
-- \copy dim_customers        FROM 'data/processed/customers_clean.csv'          CSV HEADER
-- \copy dim_packages         FROM 'data/processed/packages_clean.csv'           CSV HEADER
-- \copy dim_date             FROM 'data/processed/dim_date_clean.csv'           CSV HEADER
-- \copy fact_revenue         FROM 'data/processed/revenue_clean.csv'            CSV HEADER
-- \copy fact_subscribers     FROM 'data/processed/subscriber_snapshot_clean.csv' CSV HEADER
-- Import dimensions BEFORE facts or foreign keys will fail.

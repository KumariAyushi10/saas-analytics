/* ============================================================
   SaaS METRICS - SQL ANALYSIS QUERIES (MySQL / MySQL Workbench version)
   Database: saas  (created by running saas_mysql_dump.sql first)
   Tables:
     customers     (customer_id, company_name, industry, country,
                     employee_size, acquisition_channel, signup_date, initial_plan)
     subscriptions (subscription_id, customer_id, plan, mrr,
                     start_date, end_date, status)
     usage_data    (id, customer_id, month, logins, active_seats,
                     support_tickets, nps_score, plan_at_time)
     payments      (payment_id, customer_id, month, amount, status)

   HOW TO RUN:
   1. In MySQL Workbench, run saas_mysql_dump.sql FIRST (File > Open SQL
      Script > saas_mysql_dump.sql > lightning-bolt "Execute" icon). This
      creates the `saas` database and loads all the data.
   2. Open this file the same way.
   3. Run: USE saas;  then highlight any single query below and press
      Ctrl+Enter (Cmd+Return on Mac) to run just that one, or the
      lightning-bolt icon to run everything selected.
   ============================================================ */

USE saas;


-- 1. TOTAL CUSTOMERS, ACTIVE vs CHURNED
SELECT
    status,
    COUNT(*) AS customer_count
FROM subscriptions
GROUP BY status;


-- 2. MONTHLY RECURRING REVENUE (MRR) BY MONTH
SELECT
    month,
    ROUND(SUM(amount), 2) AS mrr,
    COUNT(DISTINCT customer_id) AS paying_customers
FROM payments
WHERE status = 'paid'
GROUP BY month
ORDER BY month;


-- 3. MONTH-OVER-MONTH MRR GROWTH RATE
WITH monthly AS (
    SELECT month, SUM(amount) AS mrr
    FROM payments
    WHERE status = 'paid'
    GROUP BY month
)
SELECT
    month,
    mrr,
    ROUND(
        100.0 * (mrr - LAG(mrr) OVER (ORDER BY month)) / LAG(mrr) OVER (ORDER BY month),
        2
    ) AS mom_growth_pct
FROM monthly
ORDER BY month;


-- 4. CUSTOMER CHURN RATE BY MONTH
WITH active_start_of_month AS (
    SELECT month, COUNT(DISTINCT customer_id) AS active_customers
    FROM usage_data
    GROUP BY month
),
churned_in_month AS (
    SELECT end_date AS month, COUNT(*) AS churned_customers
    FROM subscriptions
    WHERE end_date IS NOT NULL
    GROUP BY end_date
)
SELECT
    a.month,
    a.active_customers,
    COALESCE(c.churned_customers, 0) AS churned_customers,
    ROUND(100.0 * COALESCE(c.churned_customers, 0) / a.active_customers, 2) AS churn_rate_pct
FROM active_start_of_month a
LEFT JOIN churned_in_month c ON a.month = c.month
ORDER BY a.month;


-- 5. REVENUE / CUSTOMERS BY PLAN
SELECT
    plan,
    COUNT(*) AS total_subscriptions,
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_now,
    ROUND(AVG(mrr), 2) AS avg_mrr
FROM subscriptions
GROUP BY plan
ORDER BY avg_mrr DESC;


-- 6. CUSTOMER LIFETIME VALUE (LTV) - simple estimate
-- LTV = average MRR of the plan / churn rate of the plan
WITH plan_churn AS (
    SELECT
        plan,
        COUNT(*) AS total,
        SUM(CASE WHEN status = 'churned' THEN 1 ELSE 0 END) AS churned,
        ROUND(1.0 * SUM(CASE WHEN status = 'churned' THEN 1 ELSE 0 END) / COUNT(*), 4) AS churn_rate
    FROM subscriptions
    GROUP BY plan
)
SELECT
    pc.plan,
    pc.churn_rate,
    (SELECT ROUND(AVG(mrr), 2) FROM subscriptions s WHERE s.plan = pc.plan) AS avg_mrr,
    ROUND(
        (SELECT AVG(mrr) FROM subscriptions s WHERE s.plan = pc.plan) / NULLIF(pc.churn_rate, 0),
        2
    ) AS estimated_ltv
FROM plan_churn pc;


-- 7. COHORT RETENTION - % of each signup-month cohort still active N months later
WITH cohort AS (
    SELECT
        customer_id,
        DATE_FORMAT(signup_date, '%Y-%m') AS cohort_month
    FROM customers
),
activity AS (
    SELECT customer_id, month FROM usage_data
)
SELECT
    c.cohort_month,
    TIMESTAMPDIFF(
        MONTH,
        STR_TO_DATE(CONCAT(c.cohort_month, '-01'), '%Y-%m-%d'),
        a.month
    ) AS months_since_signup,
    COUNT(DISTINCT a.customer_id) AS active_customers
FROM cohort c
JOIN activity a ON c.customer_id = a.customer_id
GROUP BY c.cohort_month, months_since_signup
ORDER BY c.cohort_month, months_since_signup;


-- 8. TOP 10 CUSTOMERS BY TOTAL REVENUE PAID
SELECT
    p.customer_id,
    c.company_name,
    c.industry,
    ROUND(SUM(p.amount), 2) AS total_paid
FROM payments p
JOIN customers c ON c.customer_id = p.customer_id
WHERE p.status = 'paid'
GROUP BY p.customer_id, c.company_name, c.industry
ORDER BY total_paid DESC
LIMIT 10;


-- 9. REVENUE BY ACQUISITION CHANNEL
SELECT
    c.acquisition_channel,
    COUNT(DISTINCT c.customer_id) AS customers,
    ROUND(SUM(p.amount), 2) AS total_revenue,
    ROUND(SUM(p.amount) * 1.0 / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM customers c
JOIN payments p ON p.customer_id = c.customer_id AND p.status = 'paid'
GROUP BY c.acquisition_channel
ORDER BY total_revenue DESC;


-- 10. AT-RISK CUSTOMERS (low engagement, still active) - for a retention team
SELECT
    u.customer_id,
    c.company_name,
    u.month,
    u.logins,
    u.nps_score,
    s.plan,
    s.mrr
FROM usage_data u
JOIN customers c ON c.customer_id = u.customer_id
JOIN subscriptions s ON s.customer_id = u.customer_id AND s.status = 'active'
WHERE u.month = (SELECT MAX(month) FROM usage_data)
  AND u.logins < 5
  AND u.nps_score < 0
ORDER BY s.mrr DESC;


-- 11. AVERAGE REVENUE PER ACCOUNT (ARPA) BY INDUSTRY
SELECT
    c.industry,
    COUNT(DISTINCT c.customer_id) AS customers,
    ROUND(AVG(s.mrr), 2) AS avg_mrr
FROM customers c
JOIN subscriptions s ON s.customer_id = c.customer_id
GROUP BY c.industry
ORDER BY avg_mrr DESC;

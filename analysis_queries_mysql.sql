USE saas;



SELECT
    status,
    COUNT(*) AS customer_count
FROM subscriptions
GROUP BY status;



SELECT
    month,
    ROUND(SUM(amount), 2) AS mrr,
    COUNT(DISTINCT customer_id) AS paying_customers
FROM payments
WHERE status = 'paid'
GROUP BY month
ORDER BY month;



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



SELECT
    plan,
    COUNT(*) AS total_subscriptions,
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_now,
    ROUND(AVG(mrr), 2) AS avg_mrr
FROM subscriptions
GROUP BY plan
ORDER BY avg_mrr DESC;



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



SELECT
    c.acquisition_channel,
    COUNT(DISTINCT c.customer_id) AS customers,
    ROUND(SUM(p.amount), 2) AS total_revenue,
    ROUND(SUM(p.amount) * 1.0 / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM customers c
JOIN payments p ON p.customer_id = c.customer_id AND p.status = 'paid'
GROUP BY c.acquisition_channel
ORDER BY total_revenue DESC;



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



SELECT
    c.industry,
    COUNT(DISTINCT c.customer_id) AS customers,
    ROUND(AVG(s.mrr), 2) AS avg_mrr
FROM customers c
JOIN subscriptions s ON s.customer_id = c.customer_id
GROUP BY c.industry
ORDER BY avg_mrr DESC;

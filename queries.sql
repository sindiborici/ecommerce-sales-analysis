-- =====================================================================
-- E-Commerce Sales Analysis: SQL Queries
-- =====================================================================
-- Eight analytical queries against a 4-table relational schema.
-- Demonstrates JOINs, GROUP BY, conditional aggregation (CASE),
-- subqueries, CTEs, and window functions.
-- =====================================================================


-- ---------------------------------------------------------------------
-- Q1. Top 10 best-selling products by revenue
-- ---------------------------------------------------------------------
SELECT
    p.product_name,
    p.category,
    SUM(oi.quantity)                          AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders   o ON oi.order_id   = o.order_id
WHERE o.status = 'Delivered'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY revenue DESC
LIMIT 10;


-- ---------------------------------------------------------------------
-- Q2. Monthly revenue trend
-- ---------------------------------------------------------------------
SELECT
    strftime('%Y-%m', o.order_date)            AS month,
    COUNT(DISTINCT o.order_id)                 AS num_orders,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY strftime('%Y-%m', o.order_date)
ORDER BY month;


-- ---------------------------------------------------------------------
-- Q3. Revenue by country and customer segment
-- ---------------------------------------------------------------------
SELECT
    c.country,
    c.segment,
    COUNT(DISTINCT o.order_id)                 AS orders,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM customers   c
JOIN orders      o  ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id    = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY c.country, c.segment
ORDER BY revenue DESC;


-- ---------------------------------------------------------------------
-- Q4. Top 20 customers by lifetime value
-- ---------------------------------------------------------------------
SELECT
    c.customer_id,
    c.customer_name,
    c.country,
    c.segment,
    COUNT(DISTINCT o.order_id)                  AS total_orders,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)  AS lifetime_value,
    ROUND(AVG(oi.quantity * oi.unit_price), 2)  AS avg_line_value
FROM customers   c
JOIN orders      o  ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id    = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY c.customer_id
ORDER BY lifetime_value DESC
LIMIT 20;


-- ---------------------------------------------------------------------
-- Q5. Category performance with profit margin
-- ---------------------------------------------------------------------
SELECT
    p.category,
    COUNT(DISTINCT oi.order_id)                                   AS orders,
    SUM(oi.quantity)                                              AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2)                    AS revenue,
    ROUND(SUM(oi.quantity * p.cost), 2)                           AS cost,
    ROUND(SUM(oi.quantity * (oi.unit_price - p.cost)), 2)         AS profit,
    ROUND(100.0 * SUM(oi.quantity * (oi.unit_price - p.cost))
                / SUM(oi.quantity * oi.unit_price), 2)            AS profit_margin_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders   o ON oi.order_id   = o.order_id
WHERE o.status = 'Delivered'
GROUP BY p.category
ORDER BY profit DESC;


-- ---------------------------------------------------------------------
-- Q6. Cancellation and return rate by category (conditional aggregation)
-- ---------------------------------------------------------------------
SELECT
    p.category,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(CASE WHEN o.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled,
    SUM(CASE WHEN o.status = 'Returned'  THEN 1 ELSE 0 END) AS returned,
    ROUND(100.0 * SUM(CASE WHEN o.status = 'Cancelled' THEN 1 ELSE 0 END)
                / COUNT(DISTINCT o.order_id), 2) AS cancellation_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN o.status = 'Returned'  THEN 1 ELSE 0 END)
                / COUNT(DISTINCT o.order_id), 2) AS return_rate_pct
FROM orders       o
JOIN order_items  oi ON o.order_id    = oi.order_id
JOIN products     p  ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY return_rate_pct DESC;


-- ---------------------------------------------------------------------
-- Q7. Top 3 customers per country (window function: RANK)
-- ---------------------------------------------------------------------
WITH customer_spend AS (
    SELECT
        c.customer_id,
        c.customer_name,
        c.country,
        SUM(oi.quantity * oi.unit_price) AS total_spent
    FROM customers   c
    JOIN orders      o  ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id    = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY c.customer_id
),
ranked AS (
    SELECT
        country,
        customer_name,
        ROUND(total_spent, 2) AS total_spent,
        RANK() OVER (PARTITION BY country ORDER BY total_spent DESC) AS rank_in_country
    FROM customer_spend
)
SELECT *
FROM ranked
WHERE rank_in_country <= 3
ORDER BY country, rank_in_country;


-- ---------------------------------------------------------------------
-- Q8. Customer loyalty buckets (subquery + CASE classification)
-- ---------------------------------------------------------------------
SELECT
    CASE
        WHEN order_count = 1              THEN '1. One-time'
        WHEN order_count BETWEEN 2 AND 4  THEN '2. Occasional (2-4)'
        WHEN order_count BETWEEN 5 AND 9  THEN '3. Regular (5-9)'
        ELSE                                   '4. Loyal (10+)'
    END                              AS customer_type,
    COUNT(*)                         AS num_customers,
    ROUND(AVG(total_spent), 2)       AS avg_lifetime_value
FROM (
    SELECT
        c.customer_id,
        COUNT(DISTINCT o.order_id)        AS order_count,
        SUM(oi.quantity * oi.unit_price)  AS total_spent
    FROM customers   c
    JOIN orders      o  ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id    = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY c.customer_id
) customer_stats
GROUP BY customer_type
ORDER BY customer_type;

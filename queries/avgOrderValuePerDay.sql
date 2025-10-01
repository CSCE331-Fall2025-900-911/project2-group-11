SELECT order_date::date AS order_day, AVG(total_amount) AS avg_order_value
FROM orders
GROUP BY order_day
ORDER BY order_day;
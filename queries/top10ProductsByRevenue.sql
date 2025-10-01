SELECT p.product_id, p.product_name, SUM(oi.quantity * oi.unit_price_at_sale) AS product_revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name
ORDER BY product_revenue DESC
LIMIT 10;
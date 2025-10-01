SELECT e.employee_id, e.role, COUNT(o.order_id) AS orders_handled, SUM(o.total_amount) AS revenue_processed
FROM orders o
JOIN employees e ON e.employee_id = o.employee_id
WHERE e.role = 'Cashier'
GROUP BY e.employee_id, e.role
HAVING SUM(o.total_amount) < 240000
ORDER BY revenue_processed DESC;
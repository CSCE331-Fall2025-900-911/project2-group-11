SELECT EXTRACT(ISODOW FROM order_date) AS iso_dow, TO_CHAR(order_date, 'Dy') AS weekday,
       COUNT(*) AS orders_count, SUM(total_amount) AS revenue
FROM orders
GROUP BY iso_dow, weekday
ORDER BY iso_dow;
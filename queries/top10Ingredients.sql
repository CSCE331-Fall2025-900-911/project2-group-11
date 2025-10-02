SELECT 
    i.ingredient_name,
    SUM(oi.quantity * pr.quantity_per_unit) AS total_quantity_used
FROM inventory i
JOIN product_recipe pr ON i.ingredient_id = pr.ingredient_id
JOIN order_items oi ON pr.product_id = oi.product_id
GROUP BY i.ingredient_id, i.ingredient_name
ORDER BY total_quantity_used DESC
LIMIT 10;

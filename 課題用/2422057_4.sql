SELECT 
    SUM(p.price * o.quantity) AS total_sales
FROM 
    orders o
JOIN 
    customers c ON o.customer_id = c.customer_id
JOIN 
    products p ON o.product_id = p.product_id
WHERE 
    c.gender = 'Female' 
    AND c.age >= 20
    AND o.order_date BETWEEN '2024-01-01' AND '2024-03-31';

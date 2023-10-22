
{{ config(materialized='table', sort='MONTH') }}

SELECT 
product_name,   
DATE_TRUNC('MONTH', order_date) AS MONTH,
count(id)
FROM orders
GROUP BY product_name, MONTH
--WHERE order_amount > 1000

SELECT
    block,
    COUNT(*) AS num_establishments
FROM
    minato_restaurant
WHERE
    business_type <> '飲食店営業'
GROUP BY
    block
ORDER BY
    block;
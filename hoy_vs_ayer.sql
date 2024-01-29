SELECT 
    today.producto,
    today.avg_precio AS precio_promedio_hoy,
    yesterday.avg_precio AS precio_promedio_ayer
FROM
    (SELECT 
        producto, 
        AVG(precio) as avg_precio 
     FROM `slowpoke-v1`.precios 
     WHERE date = CURRENT_DATE
     GROUP BY producto) AS today
JOIN
    (SELECT 
        producto, 
        AVG(precio) as avg_precio 
     FROM `slowpoke-v1`.precios 
     WHERE date = CURRENT_DATE - INTERVAL 1 DAY
     GROUP BY producto) AS yesterday
ON
    today.producto = yesterday.producto
WHERE
    today.avg_precio > yesterday.avg_precio;
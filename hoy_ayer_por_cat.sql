SELECT
    p.date,
    p.categoria,
    ROUND(p.avg_precio, 2) AS avg_precio,
    ROUND(CASE
        WHEN LAG(p.avg_precio) OVER (PARTITION BY p.categoria ORDER BY p.date) IS NULL THEN NULL
        ELSE (p.avg_precio - LAG(p.avg_precio) OVER (PARTITION BY p.categoria ORDER BY p.date)) / LAG(p.avg_precio) OVER (PARTITION BY p.categoria ORDER BY p.date) * 100
    END, 2) AS cambio_porcentual
FROM (
    SELECT
        precios.date,
        categorias_productos.categoria,
        AVG(precios.precio) AS avg_precio
    FROM `slowpoke-v1`.precios
    INNER JOIN `slowpoke-v1`.categorias_productos ON precios.producto = categorias_productos.productos
    GROUP BY precios.date, categorias_productos.categoria
) p
ORDER BY p.categoria, p.date;
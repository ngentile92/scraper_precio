SELECT
    p.date,
    ROUND(p.avg_precio, 2) as avg_precio,
    ROUND(CASE 
        WHEN LAG(p.avg_precio) OVER (ORDER BY p.date) IS NULL THEN NULL
        ELSE (p.avg_precio - LAG(p.avg_precio) OVER (ORDER BY p.date)) / LAG(p.avg_precio) OVER (ORDER BY p.date) * 100 
    END, 2) AS cambio_porcentual
FROM (
    SELECT 
        date, 
        AVG(precio) AS avg_precio
    FROM `slowpoke-v1`.precios
    INNER JOIN (
        SELECT producto
        FROM `slowpoke-v1`.precios
        GROUP BY producto
        HAVING COUNT(DISTINCT date) = (SELECT COUNT(DISTINCT date) FROM `slowpoke-v1`.precios)
    ) prod_presente_todas_fechas ON `slowpoke-v1`.precios.producto = prod_presente_todas_fechas.producto
    GROUP BY date
) p
ORDER BY p.date;
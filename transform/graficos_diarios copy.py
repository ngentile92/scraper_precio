import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from extract.db import fetch_data
query_today = """
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
    WHERE precios.date >= CURRENT_DATE - INTERVAL 7 DAY
    GROUP BY precios.date, categorias_productos.categoria
) p
ORDER BY p.categoria, p.date;

"""
# Suponiendo que 'fetch_data' ya ha sido definido y que 'query_today' y 'query_7_dias' son tus consultas SQL



def limpiar_data(data_hoy):
    # Asegurar que 'date' es de tipo datetime y 'cambio_porcentual' es flotante
    data_hoy['date'] = pd.to_datetime(data_hoy['date'])
    data_hoy['cambio_porcentual'] = data_hoy['cambio_porcentual'].astype(float)

    # Ordenar los datos por categoría y fecha
    data_hoy.sort_values(by=['categoria', 'date'], inplace=True)

    # Marcar los registros donde 'cambio_porcentual' es NULL
    data_hoy['es_null'] = data_hoy['cambio_porcentual'].isnull()

    # Crear una columna que identifique el primer valor no-NULL después de un NULL
    data_hoy['primer_post_null'] = data_hoy['es_null'].shift().fillna(False) & ~data_hoy['es_null']

    # Filtrar para excluir los registros marcados como 'primer_post_null'
    data_filtrado = data_hoy[~data_hoy['primer_post_null']].copy()

    # Ajustar las categorías según las especificaciones
    categorias_a_ajustar = data_filtrado['categoria'].unique().tolist()
    # Remover las categorías que no necesitan ajuste
    for categoria_no_ajustar in ['alimentos', 'bebidas', 'limpieza']:
        if categoria_no_ajustar in categorias_a_ajustar:
            categorias_a_ajustar.remove(categoria_no_ajustar)

    # Fecha de ajuste
    fecha_base = pd.Timestamp('2024-02-17')

    # Ajustar categorías a base 100
    for categoria in categorias_a_ajustar:
        # Encontrar el índice del primer registro después de la fecha base para cada categoría
        indice_base = data_filtrado[(data_filtrado['categoria'] == categoria) & (data_filtrado['date'] > fecha_base)].index.min()
        
        # Si no hay datos después de la fecha base, continuar con la siguiente categoría
        if pd.isna(indice_base):
            continue
        
        # Calcular el cambio porcentual como si el valor en 'indice_base' fuera 100
        valor_base = data_filtrado.at[indice_base, 'avg_precio']
        data_filtrado.loc[data_filtrado['categoria'] == categoria, 'avg_precio'] = data_filtrado.loc[data_filtrado['categoria'] == categoria, 'avg_precio'] / valor_base * 100

        # Recalcular el cambio porcentual para esta categoría
        data_filtrado.loc[data_filtrado['categoria'] == categoria, 'cambio_porcentual'] = data_filtrado.loc[data_filtrado['categoria'] == categoria, 'avg_precio'].pct_change() * 100

    return data_filtrado

# Ejecuta las consultas y obtén los DataFrames
data_hoy = fetch_data(query_today)
data_filtrado = limpiar_data(data_hoy)
data_filtrado['impacto_porcentual'] = data_filtrado.groupby('date')['avg_precio'].transform(lambda x: x / x.sum())
data_filtrado['cambio_porcentual_relativo'] = data_filtrado['impacto_porcentual'] * data_filtrado['cambio_porcentual']
inflacion_por_fecha = data_filtrado.groupby('date')['cambio_porcentual_relativo'].sum()

import ipywidgets as widgets
from IPython.display import display, clear_output
import seaborn as sns
import matplotlib.pyplot as plt

# Supongamos que data_filtrado es tu DataFrame

# Convertir los valores únicos de la columna 'categoria' a una tupla
categorias_unicas = tuple(data_filtrado['categoria'].unique())

# Widget para seleccionar categorías
categoria_selector = widgets.SelectMultiple(
    options=categorias_unicas,
    value=categorias_unicas,  # Ahora pasamos una tupla
    description='Categorías',
    disabled=False
)

# Botón para actualizar el gráfico
update_button = widgets.Button(description="Actualizar Gráfico")

# Función para generar el gráfico (asegúrate de que esta función esté definida)
def update_grafico(b):
    with output:
        clear_output(wait=True)  # Limpiar el gráfico anterior
        categorias_seleccionadas = categoria_selector.value
        # Asegúrate de adaptar esta función para usar las categorías seleccionadas
        # plot_inflacion_acumulada(...)

# Vincular el botón al evento
update_button.on_click(update_grafico)

# Área de salida
output = widgets.Output()

# Mostrar los widgets y el área de salida
display(categoria_selector, update_button, output)

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from extract.db import fetch_data
query_today = """
-- Precios promedio para hoy
SELECT producto, AVG(precio) AS promedio_hoy
FROM `slowpoke-v1`.precios
WHERE date = CURDATE()
GROUP BY producto;
"""

query_7_dias = """

-- Precios promedio para hace 7 días
SELECT producto, AVG(precio) AS promedio_7_dias
FROM `slowpoke-v1`.precios
WHERE date = DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY producto;
"""
# Suponiendo que 'fetch_data' ya ha sido definido y que 'query_today' y 'query_7_dias' son tus consultas SQL

# Ejecuta las consultas y obtén los DataFrames
data_hoy = fetch_data(query_today)
data_7_dias = fetch_data(query_7_dias)
# Combina y encuentra todos los productos únicos
productos_hoy = set(data_hoy['producto'].unique())
productos_7_dias = set(data_7_dias['producto'].unique())
todos_productos = productos_hoy.union(productos_7_dias)

import pandas as pd
import numpy as np

# Asegúrate de que todos_productos sea una lista
todos_productos_lista = list(todos_productos)

# Preparar DataFrames para facilitar la búsqueda de precios
data_hoy_indexed = data_hoy.set_index('producto')
data_7_dias_indexed = data_7_dias.set_index('producto')

# Inicializa las matrices vacías utilizando la lista en lugar de un conjunto
matriz_hoy = pd.DataFrame(index=todos_productos_lista, columns=todos_productos_lista)
matriz_7_dias = pd.DataFrame(index=todos_productos_lista, columns=todos_productos_lista)

# Rellenar las matrices con las relaciones de precios
for prod_i in todos_productos_lista:
    for prod_j in todos_productos_lista:
        precio_i_hoy = data_hoy_indexed.at[prod_i, 'promedio_hoy'] if prod_i in data_hoy_indexed.index else np.nan
        precio_j_hoy = data_hoy_indexed.at[prod_j, 'promedio_hoy'] if prod_j in data_hoy_indexed.index else np.nan
        precio_i_7_dias = data_7_dias_indexed.at[prod_i, 'promedio_7_dias'] if prod_i in data_7_dias_indexed.index else np.nan
        precio_j_7_dias = data_7_dias_indexed.at[prod_j, 'promedio_7_dias'] if prod_j in data_7_dias_indexed.index else np.nan
        
        # Calcula la relación de precios para hoy y hace 7 días
        matriz_hoy.at[prod_i, prod_j] = precio_i_hoy / precio_j_hoy if precio_j_hoy else np.nan
        matriz_7_dias.at[prod_i, prod_j] = precio_i_7_dias / precio_j_7_dias if precio_j_7_dias else np.nan

# Asegúrate de manejar valores NaN según sea necesario, por ejemplo, reemplazándolos con 0 o dejándolos como NaN

import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 8))
sns.heatmap(matriz_hoy.replace([np.inf, -np.inf], np.nan).fillna(0), cmap='coolwarm', cbar=True)
plt.title('Relación de Precios entre Productos para Hoy')
plt.show()

plt.figure(figsize=(10, 8))
sns.heatmap(matriz_7_dias.replace([np.inf, -np.inf], np.nan).fillna(0), cmap='coolwarm', cbar=True)
plt.title('Relación de Precios entre Productos para Hoy')
plt.show()

# Asegúrate de que ambas matrices contengan números flotantes para evitar errores de tipo
matriz_hoy = matriz_hoy.astype(float)
matriz_7_dias = matriz_7_dias.astype(float)

# Calcular la nueva matriz de comparación como la relación entre los dos momentos
matriz_comparacion = matriz_7_dias / matriz_hoy

# Antes de eliminar, reemplaza [np.inf, -np.inf] con NaN
matriz_comparacion.replace([np.inf, -np.inf], np.nan, inplace=True)

# Elimina filas y columnas donde todos los valores son NaN
matriz_comparacion.dropna(axis=0, how='all', inplace=True)  # Elimina filas completamente NaN
matriz_comparacion.dropna(axis=1, how='all', inplace=True)  # Elimina columnas completamente NaN

# Visualizar la matriz de comparación con un heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(matriz_comparacion, cmap='coolwarm', cbar=True, annot=False)  # 'annot=False' para una visualización más limpia
plt.title('Cambio en la Relación de Precios entre Productos (7 días vs Hoy)')
plt.show()


import numpy as np

# Aplanar la matriz y convertirla en una Serie para manejar los valores más fácilmente
valores_aplanados = matriz_comparacion.stack()

# Separar los valores mayores que 1 y menores que 1
mayores_que_1 = valores_aplanados[valores_aplanados > 1].nlargest(5)
menores_que_1 = valores_aplanados[valores_aplanados < 1].nsmallest(5)

# Combinar los valores para obtener los 5 más grandes de cada lado
valores_destacados = pd.concat([mayores_que_1, menores_que_1])
matriz_destacados = pd.DataFrame(np.nan, index=matriz_comparacion.index, columns=matriz_comparacion.columns)

# Rellenar la matriz de destacados solo con los valores seleccionados (top 5 mayores que 1 y menores que 1)
for (prod_i, prod_j) in mayores_que_1.index:
    matriz_destacados.at[prod_i, prod_j] = matriz_comparacion.at[prod_i, prod_j]

for (prod_i, prod_j) in menores_que_1.index:
    matriz_destacados.at[prod_i, prod_j] = matriz_comparacion.at[prod_i, prod_j]
# Visualizar la matriz de comparación con un heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(matriz_destacados, cmap='coolwarm', cbar=True, annot=True, fmt=".2f")

# Agregar nombres a los ejes
plt.xlabel('Productos hace 7 días')
plt.ylabel('Productos hoy')

# Configurar el título del heatmap
plt.title('Top 5 Aumentos y Disminuciones en Relación de Precios (Hoy vs Hace 7 Días)')

# Mostrar el heatmap
plt.show()


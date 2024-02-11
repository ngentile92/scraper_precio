import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
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
    return data_filtrado

def plot_inflacion_diaria(data_hoy):

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

    # Configuración básica de Seaborn
    sns.set(style="whitegrid")

    # Crear el gráfico
    plt.figure(figsize=(12, 6))  # Ajustar el tamaño según necesites

    # Dibujar el gráfico de líneas para la variación porcentual diaria, excluyendo el primer valor post-NULL
    ax = sns.lineplot(x='date', y='cambio_porcentual', hue='categoria', data=data_filtrado, marker="o")

    # Añadir título y etiquetas a los ejes
    plt.title('Variación Porcentual Diaria de Precios por Categoría')
    plt.xlabel('Fecha')
    plt.ylabel('Cambio Porcentual (%)')

    # Remarcar el eje y=0
    plt.axhline(0, color='black', linewidth=1.5)  # Puedes ajustar el color y el grosor según necesites

    # Mejorar la legibilidad de las fechas en el eje x
    plt.xticks(rotation=45)

    # Ajustar leyenda
    plt.legend(title='Categoría', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Ajustar los límites del eje x para una mejor visualización
    plt.xlim(data_filtrado['date'].min(), data_filtrado['date'].max())

    # Mostrar el gráfico
    plt.tight_layout()
    plt.savefig('inflacion_diaria_por_categoria.png')  # Guarda el gráfico como un archivo PNG

    plt.show()


def plot_inflacion_acumulada(data_filtrado):
    # Calcular la inflación acumulada por categoría
    # Inicializar una columna para la inflación acumulada
    data_filtrado['inflacion_acumulada'] = 100  # Iniciar de 100 para simular un índice

    # Calcular la inflación acumulada iterando por categoría
    for categoria in data_filtrado['categoria'].unique():
        # Filtrar por categoría
        data_categoria = data_filtrado[data_filtrado['categoria'] == categoria]
        
        # Calcular la inflación acumulada
        inflacion_acum = data_categoria['cambio_porcentual'].fillna(0).cumsum()
        
        # Aplicar la inflación acumulada al DataFrame principal
        data_filtrado.loc[data_categoria.index, 'inflacion_acumulada'] = 100 + inflacion_acum

    # Configuración básica de Seaborn
    sns.set(style="whitegrid")

    # Crear el gráfico de la inflación acumulada por categoría
    plt.figure(figsize=(12, 6))

    # Dibujar el gráfico de líneas para la inflación acumulada
    ax = sns.lineplot(x='date', y='inflacion_acumulada', hue='categoria', data=data_filtrado, marker="o")

    # Añadir título y etiquetas a los ejes
    plt.title('Inflación Acumulada por Categoría')
    plt.xlabel('Fecha')
    plt.ylabel('Inflación Acumulada (%)')

    # Mejorar la legibilidad de las fechas en el eje x
    plt.xticks(rotation=45)

    # Ajustar leyenda
    plt.legend(title='Categoría', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Remarcar el eje y=100
    plt.axhline(100, color='red', linewidth=2, linestyle='--')  # Puedes ajustar el color, el grosor y el estilo

    # Guardar el gráfico en un archivo
    plt.tight_layout()
    plt.savefig('inflacion_acumulada_por_categoria.png')  # Guarda el gráfico como un archivo PNG

    # Mostrar el gráfico
    plt.show()
def plot_inflacion_acumulada_total_excluyendo_libreria(data_filtrado):
    # Excluir la categoría "librería" antes de cualquier cálculo
    data_sin_libreria = data_filtrado[data_filtrado['categoria'] != 'librería']

    # Asegurar que 'date' es de tipo datetime
    data_sin_libreria['date'] = pd.to_datetime(data_sin_libreria['date'])
    
    # Asegurar que 'cambio_porcentual' es flotante y ajustar para cálculo de interés compuesto
    data_sin_libreria['cambio_porcentual'] = data_sin_libreria['cambio_porcentual'].astype(float) / 100 + 1

    # Calcular la inflación acumulada total como un producto acumulado de los cambios porcentuales
    data_sin_libreria['inflacion_acumulada_total'] = data_sin_libreria['cambio_porcentual'].cumprod() * 100

    # Asegúrate de reiniciar el índice de inflación a 100 para el primer punto de datos si es necesario
    primer_indice = data_sin_libreria.index.min()
    data_sin_libreria.loc[primer_indice, 'inflacion_acumulada_total'] = 100

    # Configuración básica de Seaborn
    sns.set(style="whitegrid")

    # Crear el gráfico de la inflación acumulada total para todas las categorías, excluyendo librería
    plt.figure(figsize=(12, 6))

    # Dibujar el gráfico de líneas para la inflación acumulada total
    ax = sns.lineplot(x='date', y='inflacion_acumulada_total', data=data_sin_libreria, marker="o", color='blue')

    # Añadir título y etiquetas a los ejes
    plt.title('Inflación Acumulada Total (Excluyendo Librería)')
    plt.xlabel('Fecha')
    plt.ylabel('Inflación Acumulada Total (%)')

    # Mejorar la legibilidad de las fechas en el eje x
    plt.xticks(rotation=45)

    # Ajustar leyenda
    plt.legend(title='Inflación Total', loc='upper left', labels=['Inflación Acumulada'])

    # Remarcar el eje y=100 (punto de inicio para la inflación acumulada)
    plt.axhline(100, color='red', linewidth=2, linestyle='--')

    # Guardar el gráfico en un archivo
    plt.tight_layout()
    plt.savefig('inflacion_acumulada_total_excluyendo_libreria.png')  # Guarda el gráfico como un archivo PNG

    # Mostrar el gráfico
    plt.show()
def calcular_inflacion_acumulada_total(data_filtrado):
    # Excluir la categoría "librería"
    data_sin_libreria = data_filtrado[data_filtrado['categoria'] != 'librería'].copy()

    # Asegurar que 'date' es de tipo datetime y 'cambio_porcentual' es flotante
    data_sin_libreria['date'] = pd.to_datetime(data_sin_libreria['date'])
    data_sin_libreria['cambio_porcentual'] = data_sin_libreria['cambio_porcentual'].astype(float)

    # Calcular la inflación acumulada total como un producto acumulado de los cambios porcentuales ajustados
    data_sin_libreria['inflacion_acumulada_total'] = (data_sin_libreria['cambio_porcentual'] / 100 + 1).cumprod() * 100

    return data_sin_libreria
def plot_cambio_porcentual_diario(data_filtrado):
    # Excluir la categoría "librería"
    data_sin_libreria = data_filtrado[data_filtrado['categoria'] != 'librería']

    # Asegurar que 'date' es de tipo datetime
    data_sin_libreria['date'] = pd.to_datetime(data_sin_libreria['date'])
    
    # Asegurar que 'cambio_porcentual' es flotante
    data_sin_libreria['cambio_porcentual'] = data_sin_libreria['cambio_porcentual'].astype(float)

    # Calcular la inflación acumulada total como se describió previamente
    # (Asegúrate de haber realizado este paso antes de continuar)

    # Calcular el cambio porcentual diario de la inflación acumulada
    data_sin_libreria['cambio_porcentual_inflacion'] = data_sin_libreria['inflacion_acumulada_total'].pct_change() * 100

    # Configuración básica de Seaborn
    sns.set(style="whitegrid")

    # Crear el gráfico del cambio porcentual diario en la inflación
    plt.figure(figsize=(12, 6))

    # Dibujar el gráfico de líneas para el cambio porcentual diario
    ax = sns.lineplot(x='date', y='cambio_porcentual_inflacion', data=data_sin_libreria, marker="o", color='blue')

    # Añadir título y etiquetas a los ejes
    plt.title('Cambio Porcentual Diario en la Inflación (Excluyendo Librería)')
    plt.xlabel('Fecha')
    plt.ylabel('Cambio Porcentual Diario en la Inflación (%)')

    # Mejorar la legibilidad de las fechas en el eje x
    plt.xticks(rotation=45)

    # Remarcar el eje y=0 para destacar los aumentos y disminuciones
    plt.axhline(0, color='red', linewidth=1, linestyle='--')

    # Guardar el gráfico en un archivo
    plt.tight_layout()
    plt.savefig('cambio_porcentual_diario_inflacion.png')  # Guarda el gráfico como un archivo PNG

    # Mostrar el gráfico
    plt.show()

if __name__ == '__main__':
    # Ejecuta las consultas y obtén los DataFrames
    data_hoy = fetch_data(query_today)
    data_filtrado = limpiar_data(data_hoy)
    plot_inflacion_diaria(data_filtrado)
    plot_inflacion_acumulada(data_filtrado)
    plot_inflacion_acumulada_total_excluyendo_libreria(data_filtrado)
    data_filtrado = calcular_inflacion_acumulada_total(data_filtrado)  # Calcula la inflación acumulada total

    plot_cambio_porcentual_diario(data_filtrado)
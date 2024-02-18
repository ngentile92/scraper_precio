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


def calcular_promedio_ponderado(df):
    # Asegurarse de que el DataFrame no está vacío
    if df.empty:
        return None

    # Calcular el peso de cada categoría por su precio promedio
    total_precio = df['avg_precio'].sum()
    df['peso'] = df['avg_precio'] / total_precio

    # Calcular el promedio ponderado del cambio porcentual
    promedio_ponderado = (df['cambio_porcentual'] * df['peso']).sum()

    # Calcular el promedio de cada categoría y su ponderador
    promedios = {}
    ponderadores = {}
    for categoria in df['categoria'].unique():
        categoria_df = df[df['categoria'] == categoria]
        promedio_categoria = (categoria_df['cambio_porcentual'] * categoria_df['peso']).sum()
        promedios[categoria] = promedio_categoria
        ponderadores[categoria] = categoria_df['peso'].iloc[0]  # Se asume que el ponderador es el mismo para todas las filas de una categoría

    # Agregar los promedios y ponderadores al DataFrame original
    for categoria, promedio in promedios.items():
        df['promedio_' + categoria] = promedio
        df['ponderador_' + categoria] = ponderadores[categoria]

    return df


def plot_price_change(data):
    # Extraer las fechas y los cambios porcentuales ponderados
    dates = data['date']
    price_changes = data['cambio_porcentual_ponderado']
    
    # Crear el gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(dates, price_changes, marker='o', linestyle='-', label='Cambio Porcentual Ponderado')
    
    # Agregar línea horizontal en y=0 para marcar el punto sin cambio de precios
    plt.axhline(y=0, color='r', linestyle='--', linewidth=1, label='Sin cambio de precios')
    
    # Configurar el título y las etiquetas de los ejes
    plt.title('Evolución del Cambio de Precios')
    plt.xlabel('Fecha')
    plt.ylabel('Cambio Porcentual Ponderado')
    
    # Rotar las etiquetas del eje x para una mejor visualización
    plt.xticks(rotation=45)
    
    # Añadir una leyenda
    plt.legend()
    
    # Mostrar el gráfico
    plt.grid(True)
    plt.tight_layout()
    plt.show()
def plot_inflacion_diaria_ponderada(inflacion_por_fecha):
    # Plotear la inflación por fecha
    plt.figure(figsize=(10, 6))
    plt.plot(inflacion_por_fecha.index, inflacion_por_fecha.values, marker='o', linestyle='-')

    # Marcar el punto donde la inflación es 0
    plt.axhline(y=0, color='r', linestyle='--')

    # Configurar el título y las etiquetas de los ejes
    plt.title('Inflación por Fecha ponderada')
    plt.xlabel('Fecha')
    plt.ylabel('Inflación')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    # Mostrar el gráfico
    plt.show()

if __name__ == '__main__':
    # Ejecuta las consultas y obtén los DataFrames
    data_hoy = fetch_data(query_today)
    data_filtrado = limpiar_data(data_hoy)
    data_filtrado['impacto_porcentual'] = data_filtrado.groupby('date')['avg_precio'].transform(lambda x: x / x.sum())
    data_filtrado['cambio_porcentual_relativo'] = data_filtrado['impacto_porcentual'] * data_filtrado['cambio_porcentual']
    inflacion_por_fecha = data_filtrado.groupby('date')['cambio_porcentual_relativo'].sum()
    plot_inflacion_diaria_ponderada(inflacion_por_fecha)
    plot_inflacion_diaria(data_filtrado)
    plot_inflacion_acumulada(data_filtrado)
    plot_inflacion_acumulada_total_excluyendo_libreria(data_filtrado)
    # Visualizar el resultado
    #data_filtrado = calcular_inflacion_acumulada_total(data_filtrado)  # Calcula la inflación acumulada total
#
    #plot_cambio_porcentual_diario(data_filtrado)
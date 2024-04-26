import datetime
# add pathfile
import sys
sys.path.append('../')
import re

from extract.precios import get_store_name_from_url, extract_multiple_prices_and_names_selenium, get_type_store
import pandas as pd
from extract.db import fetch_data
from playwright_scripts.async_playwright import StorePage
import asyncio
from playwright.async_api import async_playwright
from transform.mappings_categorias import CATEGORIA_MAPPING, SUBCATEGORIA_MAPPING, INDICE_MAPPING, PRODUCTO_A_CATEGORIA

# Función de búsqueda en diccionario
def extract_from_mapping(url_lower, mapping):
    for pattern, category in mapping.items():
        if re.search(pattern, url_lower):
            return category
    return 'otro'

def extract_category(url):
    url_lower = url.lower()
    return extract_from_mapping(url_lower, CATEGORIA_MAPPING)

def extract_subcategory(url):
    url_lower = url.lower()
    return extract_from_mapping(url_lower, SUBCATEGORIA_MAPPING)


async def get_category(urls: list):
    all_data = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox','--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"'])
        for url in urls:
            print(f"Procesando URL: {url}")
            page = await browser.new_page()
            store_name = get_store_name_from_url(url)
            type_url = get_type_store(url)
            category = extract_category(url)
            subcategory = extract_subcategory(url)

            if type_url == 'all':
                store_page = StorePage(page, max_pages=3)
                products_data = await store_page.navigate_and_extract(url)
                if products_data:
                    for date, stores in products_data.items():
                        for store, products in stores.items():
                            for product_name, price in products.items():
                                # Añadir datos al DataFrame
                                all_data.append({
                                    'producto_unificado': product_name,
                                    'categorias': category,
                                    'sub-categoria': subcategory
                                })
            await page.close()
        await browser.close()

    df = pd.DataFrame(all_data)
    return df

def get_index(category, subcategory):
    """
    Función que busca la tercera categoría 'Índice' basado en la categoría y subcategoría.
    """
    return INDICE_MAPPING.get(category, {}).get(subcategory, 'otro')

def add_index_column(df):
    """
    Función que agrega la columna 'Índice' al DataFrame existente.
    """
    # Asumiendo que 'categorias' y 'sub-categoria' son las columnas de tu DataFrame existente
    df['Indice'] = df.apply(lambda row: get_index(row['categorias'], row['sub-categoria']), axis=1)
    return df


def mapear_categoria_por_palabra(nombre_producto, categoria_actual):
    nombre_producto = nombre_producto.lower()
    # Verificar si la categoría actual contiene palabras clave específicas
    if 'otro' in categoria_actual.lower() or 'otros alimentos' in categoria_actual.lower() or 'congelados' in categoria_actual.lower() or 'conservas' in categoria_actual.lower():
        # Verificar si alguna de las palabras clave está presente en el nombre del producto
        for palabra_clave, nueva_categoria in CATEGORIA_MAPPING.items():
            if palabra_clave in nombre_producto:
                print(f"Producto: {nombre_producto} - Nueva categoría: {nueva_categoria}")
                return nueva_categoria
    # Si la categoría actual no contiene las palabras clave, devolver la categoría actual
    return categoria_actual


# Función para actualizar la categoría basada en palabras clave dentro del nombre del producto
def actualizar_categoria_con_palabra(df, columna_nombre_producto, columna_categoria):
    # Usar `apply` para mapear la nueva categoría usando la función `mapear_categoria_por_palabra`
    # Se consideran las filas donde columna_categoria contiene 'otro', 'congelados' o 'conservas'
    condicion = df[columna_categoria].str.lower().str.contains('otro|congelados|conservas', na=False)
    # print todos los que cumplen la condición
    print(df[condicion])
    # ver quienes complen la condición y usar mapear_categoria_por_palabra y actualizar la columna
    df.loc[condicion, columna_categoria] = df[condicion].apply(lambda row: mapear_categoria_por_palabra(row[columna_nombre_producto], row[columna_categoria]), axis=1)
    return df


async def main():
    with open('url_productos.csv', 'r') as f:
        datos = pd.read_csv(f, encoding='ISO-8859-1')
        url_list = datos['URL'].tolist()
#
    df = await get_category(url_list)
    # abrir productos_categorias.csv
    datos = pd.read_csv('producto_categorias.csv', encoding='ISO-8859-1')
    datos = pd.concat([datos, df], axis=0)
    datos = add_index_column(datos)
    # drop duplicates
    datos = datos.drop_duplicates(subset='producto_unificado', keep='last')
    datos_actualizados = actualizar_categoria_con_palabra(datos, 'producto_unificado', 'Indice')

    #save datos
    print("Guardando datos actualizados...")
    datos_actualizados.to_csv('producto_categorias.csv', index=False, encoding='ISO-8859-1')
    print("Datos guardados")

if __name__ == "__main__":
    asyncio.run(main())
import datetime
# add pathfile
import sys
sys.path.append('../')
import re

from extract.precios import get_store_name_from_url, extract_multiple_prices_and_names_selenium, get_type_store
import pandas as pd
from extract.db import fetch_data
from playright.async_playwright_trial import StorePage
import asyncio
from playwright.async_api import async_playwright
from transform.mappings import CATEGORIA_MAPPING, SUBCATEGORIA_MAPPING, INDICE_MAPPING, PRODUCTO_A_CATEGORIA

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
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        for url in urls:
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
                                print(f"de {url} esta el Producto: {product_name}, Categoría: {category}, Subcategoría: {subcategory}")
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
    # Solo actualizamos si la categoría actual contiene la palabra "otro"
    if 'otro' in categoria_actual.lower() or 'otros alimentos' in categoria_actual.lower() or 'congelados' in categoria_actual.lower() or 'conservas' in categoria_actual.lower():
        for palabra_clave, nueva_categoria in PRODUCTO_A_CATEGORIA.items():
            if palabra_clave in nombre_producto:
                return nueva_categoria
    return categoria_actual  # Devuelve la categoría actual si no hay coincidencia

# Función para actualizar la categoría basada en palabras clave dentro del nombre del producto
def actualizar_categoria_con_palabra(df, columna_nombre_producto, columna_categoria):
    # Usar `apply` para mapear la nueva categoría usando la función `mapear_categoria_por_palabra`
    # Se consideran las filas donde columna_categoria contiene 'otro', 'congelados' o 'conservas'
    condicion = df[columna_categoria].str.lower().str.contains('otro|congelados|conservas', na=False)
    df.loc[condicion, columna_categoria] = df.loc[condicion].apply(
        lambda row: mapear_categoria_por_palabra(row[columna_nombre_producto], row[columna_categoria]), axis=1
    )
    return df





async def main():
    with open('url_productos_pruebas.csv', 'r') as f:
        datos = pd.read_csv(f, encoding='ISO-8859-1')
        url_list = datos['URL'].tolist()

    df = await get_category(url_list)

    with open('producto_categorias.csv', 'r') as f:
        datos = pd.read_csv(f, encoding='ISO-8859-1')

    datos = pd.concat([datos, df], axis=0)
    datos = add_index_column(datos)
    print("Datos actualizados: ", datos)
    # drop duplicates
    datos = datos.drop_duplicates(subset='producto_unificado', keep='last')
    datos_actualizados = actualizar_categoria_con_palabra(datos, 'producto_unificado', 'Indice')
    print("Datos actualizados con palabras clave: ", datos_actualizados)

    #save datos
    print("Guardando datos actualizados...")
    datos_actualizados.to_csv('producto_categoriasPRUEBA.csv', index=False, encoding='ISO-8859-1')
    print("Datos guardados")

if __name__ == "__main__":
    asyncio.run(main())
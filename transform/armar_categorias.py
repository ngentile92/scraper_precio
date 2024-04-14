import datetime
# add pathfile
import sys
sys.path.append('../')

from extract.precios import get_store_name_from_url, extract_multiple_prices_and_names_selenium, get_type_store
import pandas as pd
from extract.db import fetch_data
from playright.async_playwright_trial import StorePage
import asyncio
from playwright.async_api import async_playwright


indice_mapping = {
    'electrodomesticos y tecnologia': {
        'celulares': 'celulares y pequenos electrodomesticos',
        'pequenos electrodomesticos': 'celulares y pequenos electrodomesticos',
        'informatica': 'informatica'
    },
    'fiambres y quesos': {
        'quesos': 'Leche/ productos lacteos/ huevos y alimentos vegetales'
    },
    'perfumeria': {
        'farmacia': 'farmacia',
        'cuidado oral': 'cuidado oral'
    },
    'lacteos': {
        'yogures': 'Leche/ productos lacteos/ huevos y alimentos vegetales',
        'leches': 'Leche/ productos lacteos/ huevos y alimentos vegetales'
    },
    'desayuno': {
        'infusiones': 'Bebidas no alcoholicas'
    },
    'prendas y calzado': {
        'camisas': 'Prendas de vestir',
        'jeans': 'Prendas de vestir',
        'sweaters y buzos': 'Prendas de vestir',
        'remeras': 'Prendas de vestir',
        'calzado': 'Calzado',
        'pantalon': 'Prendas de vestir',
        'medias': 'Calzado'
    },
    'sin TACC': {
        'sin TACC': 'sin TACC'
    },
    'carnes': {
        'cerdo': 'Carnes y derivados',
        'vaca': 'Carnes y derivados'
    },
    'almacen': {
        'pastas': 'Pan / pastas y cereales',
        'aceites': 'Aceites/ aderezos/ grasas y manteca',
        'conservas': 'Otros alimentos'
    },
    'frutas y verduras': {
        'frutas': 'Frutas',
        'verduras': 'Verduras/ tuberculos y legumbres'
    },
    'libreria': {
        'cuadernos': 'libreria',
        'lapiceras': 'libreria',
        'lapices': 'libreria',
        'marcadores': 'libreria',
        'gomas': 'libreria',
        'mochilas': 'libreria',
        'otro': 'libreria'
    },
    'bazar y textil': {
        'indumentaria': 'Prendas de vestir',
        'libreria': 'libreria'
    },
    'congelados': {
        'congelados': 'Otros alimentos'
    },
    'bebidas': {
        'alcoholica': 'Bebidas alcoholicas y tabaco',
        'no alcoholica': 'Bebidas no alcoholicas'
    },
    'alimentos': {
        'pan y lacteos': 'Pan / pastas y cereales',
        'aderezos': 'Aceites/ aderezos/ grasas y manteca',
        'carnes y huevo': 'Carnes y derivados',
        'otros': 'Otros alimentos'
    },
    'limpieza': {
        'casa': 'limpieza',
        'personal': 'limpieza'
    }
}

# pequenos electrodomesticos deberia ser celulares y pequenos electrodomesticos junto a celulares
producto_a_categoria = {
    'tomate': 'Verduras/ tuberculos y legumbres',
    'papas': 'Verduras/ tuberculos y legumbres',
    'arvejas': 'Verduras/ tuberculos y legumbres',
    'lentejas': 'Verduras/ tuberculos y legumbres',
    'jardinera': 'Verduras/ tuberculos y legumbres',
    'garbanzos': 'Verduras/ tuberculos y legumbres',
    'atun': 'Pescados y mariscos',
    'arroz': 'Pan / pastas y cereales',
    'zucaritas': 'Pan / pastas y cereales',
    'maiz': 'Pan / pastas y cereales',
    'soja': 'Leche/ productos lacteos/ huevos y alimentos vegetales',
    'duraznos': 'Frutas',
    'hamburguesa': 'Carnes y derivados',
    'carne': 'Carnes y derivados',
    'pollo': 'Carnes y derivados',
    'salmon': 'Pescados y mariscos',
    'dolca': 'Bebidas no alcoholicas',
    'sonrisas': 'Azucar/ dulces/ chocolate/golosinas/ etc.',
    'bombon': 'Azucar/ dulces/ chocolate/golosinas/ etc.',
    'alfajor': 'Azucar/ dulces/ chocolate/golosinas/ etc.',
    'chocolate': 'Azucar/ dulces/ chocolate/golosinas/ etc.',
}

def extract_category(url):
    url_lower = url.lower()  # Convierte la URL a minúsculas
    if 'electro' in url_lower:
        return 'electrodomesticos y tecnologia'
    elif 'perfumeria' in url_lower:
        return 'perfumeria'
    elif 'sweaters' in url_lower or 'jeans' in url_lower or 'camisas' in url_lower:
        return 'prendas y calzado'
    elif '/Bazar-y-textil/Libreria' in url_lower:
        return 'libreria'
    elif 'lacteos' in url_lower:
        return 'lacteos'
    elif 'desayuno' in url_lower:
        return 'desayuno'
    elif 'map=productclusterids' in url_lower and '163' in url_lower:
        return 'sin TACC'
    elif 'quesos' in url_lower or 'fiambres' in url_lower:
        return 'fiambres y quesos'
    elif 'carnes' in url_lower:
        return 'carnes'
    elif 'depart' in url_lower:
        return 'departamentos'
    elif 'frutas' in url_lower or 'verduras' in url_lower:
        return 'frutas y verduras'
    elif 'almacen' in url_lower:
        return 'almacen'
    elif 'congelados' in url_lower:
        return 'congelados'
    elif 'bazar' in url_lower or 'textil' in url_lower:
        return 'bazar y textil'
    else:
        return 'otro'

def extract_subcategory(url):
    url_lower = url.lower()  # Convierte la URL a minúsculas
    if 'electros' in url_lower:
        return 'pequenos electrodomesticos'
    elif '/frutas-y-verduras/frutas' in url_lower:
        return 'frutas'
    elif '/frutas-y-verduras/verduras' in url_lower:
        return 'verduras'
    elif '/indumentaria' in url_lower:
        return 'indumentaria'
    elif '/aceites' in url_lower:
        return 'aceites'
    elif '/congelados' in url_lower:
        return 'congelados'
    elif '/quesos' in url_lower:
        return 'quesos'
    elif '/fiambres' in url_lower:
        return 'fiambres'
    elif 'cerdo' in url_lower:
        return 'cerdo'
    elif 'vacuna' in url_lower:
        return 'vaca'
    elif 'cuidado-oral' in url_lower:
        return 'cuidado oral'
    elif 'farmacia' in url_lower:
        return 'farmacia'
    elif 'sweaters' in url_lower or 'buzos' in url_lower:
        return 'sweaters y buzos'
    elif 'jeans' in url_lower:
        return 'jeans'
    elif 'camisas' in url_lower:
        return 'camisas'
    elif 'libreria' in url_lower:
        return 'libreria'
    elif 'celulares' in url_lower:
        return 'celulares'
    elif 'informatica' in url_lower:
        return 'informatica'
    elif 'yogures' in url_lower:
        return 'yogures'
    elif 'leches' in url_lower:
        return 'leches'
    elif 'infusiones' in url_lower:
        return 'infusiones'
    elif 'galletitas' in url_lower:
        return 'galletitas'
    elif 'map=productclusterids' in url_lower and '163' in url_lower:
        return 'sin TACC'
    elif 'federal' in url_lower:
        return 'capital federal'
    elif '/conservas' in url_lower:
        return 'conservas'
    elif 'pastas' in url_lower:
        return 'pastas'
    else:
        return 'otro'


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
    return indice_mapping.get(category, {}).get(subcategory, 'otro')

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
        for palabra_clave, nueva_categoria in producto_a_categoria.items():
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
    datos_actualizados.to_csv('producto_categorias.csv', index=False, encoding='ISO-8859-1')
    print("Datos guardados")

if __name__ == "__main__":
    asyncio.run(main())
import datetime
from extract.precios import get_store_name_from_url, extract_multiple_prices_and_names_selenium, get_type_store
import pandas as pd

https://www.zonaprop.com.ar/departamentos-alquiler-capital-federal-mas-de-1-bano-1-habitacion-2-ambientes-sin-garages-40-50-m2-cubiertos.html
def extract_category(url):
    url_lower = url.lower()  # Convierte la URL a minúsculas
    if 'electro' in url_lower:
        return 'electrodomesticos y tecnologia'
    elif 'perfumeria' in url_lower:
        return 'perfumeria'
    elif 'sweaters' in url_lower or 'jeans' in url_lower or 'camisas' in url_lower:
        return 'prendas y calzado'
    elif 'bazar' in url_lower:
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
    else:
        return 'otro'

def extract_subcategory(url):
    url_lower = url.lower()  # Convierte la URL a minúsculas
    if 'electros' in url_lower:
        return 'pequenos electrodomesticos'
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
    else:
        return 'otro'


def get_category(urls: list):
    """
    Función que devuelve un dataframe con el producto, categoría y subcategoría.
    """
    all_data = []
    for url in urls:
        store_name = get_store_name_from_url(url)
        type_url = get_type_store(url)
        category = extract_category(url)  # Asume que esta función devuelve la categoría del producto
        subcategory = extract_subcategory(url)  # Asume que esta función devuelve la subcategoría del producto
        if type_url == 'all':
            products_data = extract_multiple_prices_and_names_selenium(url, store_name)
            if products_data:
                for product in products_data:
                    product_name = product['name']
                    # Poblamos all_data con nombre del producto, categoría y subcategoría
                    all_data.append({
                        'producto_unificado': product_name,
                        'categorias': category,
                        'sub-categoria': subcategory
                    })
                    print(f"de {url} esta el Producto: {product_name}, Categoría: {category}, Subcategoría: {subcategory}")
        else:
            continue
    # Convertimos all_data a un DataFrame
    df = pd.DataFrame(all_data)
    return df

if __name__ == "__main__":
    with open('../url_productos.csv', 'r') as f:
        datos = datos = pd.read_csv(f, encoding='ISO-8859-1')
        # Convertir a listas
        url_list = datos['URL'].tolist()

    df = get_category(url_list)
    with open('../producto_categorias.csv', 'r') as f:
        datos = pd.read_csv(f, encoding='ISO-8859-1')
    # update datos with the new columns
    datos = pd.concat([datos, df], axis=0)
    # drop duplicates
    datos = datos.drop_duplicates(subset='producto_unificado', keep='last')
    #save datos
    datos.to_csv('../producto_categoriass.csv', index=False, encoding='ISO-8859-1')

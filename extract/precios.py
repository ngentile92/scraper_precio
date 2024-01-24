import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import json
import os
import datetime


def get_store_name_from_url(url):
    if 'disco.com.ar' in url:
        return 'disco'
    elif 'mercadolibre.com.ar' in url:
        return 'MELI'
    else:
        return 'unknown'

def extract_product_name_disco(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        product_span = soup.find('span', class_='vtex-store-components-3-x-productBrand')
        return product_span.get_text().strip() if product_span else 'Nombre del producto no encontrado'
    return 'Solicitud fallida'

def extract_product_name_meli(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        product_h1 = soup.find('h1', class_='ui-pdp-title')
        return product_h1.get_text().strip() if product_h1 else 'Nombre del producto no encontrado'
    return 'Solicitud fallida'

def extract_price_selenium(url):
    options = Options()
    options.headless = True
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        time.sleep(1)
        try:
            # Intentar primero con la estructura de Disco
            price_div = driver.find_element(By.CLASS_NAME, 'discoargentina-store-theme-1dCOMij_MzTzZOCohX1K7w')
        except:
            # Si falla, intentar con la estructura de MercadoLibre
            price_div = driver.find_element(By.CLASS_NAME, 'andes-money-amount__fraction')
        return price_div.text.strip() if price_div else 'Precio no encontrado'
    finally:
        driver.quit()

def process_urls(url_list):
    products = {}
    today = datetime.datetime.now().strftime("%d/%m/%Y") 

    for url in url_list:
        store_name = get_store_name_from_url(url)
        if store_name == 'disco':
            product_name = extract_product_name_disco(url)
        elif store_name == 'MELI':
            product_name = extract_product_name_meli(url)
        else:
            print(f"URL no reconocida: {url}")
            continue

        price = extract_price_selenium(url)
        price_number = float(price.replace('$', '').replace('.', '').replace(',', '.')) if price != 'Precio no encontrado' else None
        products[product_name] = price_number

        print(f"URL: {url}")
        print(f"Nombre del Producto: {product_name}")
        print(f"Precio: {price}")
        print("-" * 50)

    return {today: {store_name: products}}

urls = [
    'https://www.disco.com.ar/gaseosa-coca-cola-sabor-original-1-5-lt/p',
    'https://www.disco.com.ar/yerba-mate-suave-playadito-500-gr/p',
    'https://www.disco.com.ar/fernet-branca-750-ml-2/p',
    'https://www.mercadolibre.com.ar/yerba-mate-playadito-suave-500grs/p/MLA19991741#reco_item_pos=2&reco_backend=item_decorator&reco_backend_type=function&reco_client=home_items-decorator-legacy&reco_id=9d1675cb-71bb-4632-a70c-ecb878920ab6&c_id=/home/second-best-navigation-trend-recommendations/element&c_uid=d47963a0-c512-4d20-aeca-3d3ec910f11d&da_id=second_best_navigation_trend&da_position=2&id_origin=/home/dynamic_access&da_sort_algorithm=ranker',
    'https://www.mercadolibre.com.ar/branca-fernet-750-ml/p/MLA20034085?pdp_filters=category:MLA403668#searchVariation=MLA20034085&position=2&search_layout=stack&type=product&tracking_id=32f2a960-6d7c-4000-9622-954513392276',
    'https://articulo.mercadolibre.com.ar/MLA-1144240255-gaseosa-coca-cola-sabor-original-15-lt-_JM#position=13&search_layout=stack&type=item&tracking_id=6c69d958-94e8-43a8-bb15-582f02730e8d'
]

all_data = {}

# Procesar todas las URLs
for url in urls:
    data = process_urls([url])
    date, store_products = next(iter(data.items()))
    store_name, products = next(iter(store_products.items()))

    if date not in all_data:
        all_data[date] = {}
    if store_name not in all_data[date]:
        all_data[date][store_name] = {}

    all_data[date][store_name].update(products)

# Crear la carpeta 'data' si no existe y guardar el archivo JSON
os.makedirs('../data', exist_ok=True)
with open(os.path.join('../data', 'productos.json'), 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=4)
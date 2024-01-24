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

import requests
from bs4 import BeautifulSoup
import json
import os
def extract_product_name(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Buscar el elemento con el nombre del producto
        product_h1 = soup.find('h1', class_='ui-pdp-title')
        product_name = product_h1.get_text().strip() if product_h1 else 'Nombre del producto no encontrado'

        return product_name
    else:
        return 'Solicitud fallida'


# Nueva función extract_product_name adaptada a la nueva estructura HTML
def extract_product_name(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Buscar el elemento con el nombre del producto
        product_h1 = soup.find('h1', class_='ui-pdp-title')
        product_name = product_h1.get_text().strip() if product_h1 else 'Nombre del producto no encontrado'

        return product_name
    else:
        return 'Solicitud fallida'

def extract_price_selenium(url):
    options = Options()
    options.headless = True

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(1)  # Ajusta este tiempo según sea necesario

        # Buscar el elemento que contiene el precio
        price_span = driver.find_element(By.CLASS_NAME, 'andes-money-amount__fraction')
        price = price_span.text.strip() if price_span else 'Precio no encontrado'
        return price
    finally:
        driver.quit()


def process_urls(url_list):
    products = {}
    for url in url_list:
        product_name = extract_product_name(url)
        price = extract_price_selenium(url)
        
        # Remover el signo de peso y convertir a número si es necesario
        price_number = float(price.replace('$', '').replace('.', '').replace(',', '.')) if price != 'Precio no encontrado' else None

        products[product_name] = price_number

        print(f"URL: {url}")
        print(f"Nombre del Producto: {product_name}")
        print(f"Precio: {price}")
        print("-" * 50)

    # Crear la carpeta 'data' si no existe
    os.makedirs('../data', exist_ok=True)

    # Guardar en un archivo JSON dentro de la carpeta 'data'
    with open(os.path.join('../data', 'productos_meli.json'), 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)


# Lista de URLs
urls = [
    'https://www.mercadolibre.com.ar/yerba-mate-playadito-suave-500grs/p/MLA19991741#reco_item_pos=2&reco_backend=item_decorator&reco_backend_type=function&reco_client=home_items-decorator-legacy&reco_id=9d1675cb-71bb-4632-a70c-ecb878920ab6&c_id=/home/second-best-navigation-trend-recommendations/element&c_uid=d47963a0-c512-4d20-aeca-3d3ec910f11d&da_id=second_best_navigation_trend&da_position=2&id_origin=/home/dynamic_access&da_sort_algorithm=ranker',
    'https://www.mercadolibre.com.ar/branca-fernet-750-ml/p/MLA20034085?pdp_filters=category:MLA403668#searchVariation=MLA20034085&position=2&search_layout=stack&type=product&tracking_id=32f2a960-6d7c-4000-9622-954513392276',
    'https://articulo.mercadolibre.com.ar/MLA-1144240255-gaseosa-coca-cola-sabor-original-15-lt-_JM#position=13&search_layout=stack&type=item&tracking_id=6c69d958-94e8-43a8-bb15-582f02730e8d'
]

process_urls(urls)
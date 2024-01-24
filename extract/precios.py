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
    elif 'carrefour.com.ar' in url:
        return 'carrefour'
    elif 'masonline.com.ar' in url:
        return 'chango_mas'
    else:
        return 'unknown'


def extract_product_name(url, store_name):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Define the search parameters based on store_name
        if store_name == 'disco' or store_name == 'carrefour' or store_name == 'chango_mas':
            product_tag = 'span'
            product_class = 'vtex-store-components-3-x-productBrand'
        elif store_name == 'MELI':
            product_tag = 'h1'
            product_class = 'ui-pdp-title'
        else:
            return 'Nombre del producto no encontrado'

        # Find the product name using the specified tag and class
        product_element = soup.find(product_tag, class_=product_class)
        return product_element.get_text().strip() if product_element else 'Nombre del producto no encontrado'
    return 'Solicitud fallida'


def extract_price_selenium(url, store_name):
    options = Options()
    options.headless = True
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        time.sleep(1)
        if store_name == 'disco':
            price_div = driver.find_element(By.CLASS_NAME, 'discoargentina-store-theme-1dCOMij_MzTzZOCohX1K7w')
        elif store_name == 'carrefour':
            price_div = driver.find_element(By.CLASS_NAME, 'valtech-carrefourar-product-price-0-x-sellingPriceValue')
        elif store_name == 'chango_mas':
            price_div = driver.find_element(By.CLASS_NAME, 'valtech-gdn-dynamic-product-0-x-dynamicProductPrice')
        elif store_name == 'MELI':
            price_div = driver.find_element(By.CLASS_NAME, 'andes-money-amount__fraction')
        else:
            price_div = None

        return price_div.text.strip() if price_div else 'Precio no encontrado'
    finally:
        driver.quit()

def process_urls(url_list):
    products = {}
    today = datetime.datetime.now().strftime("%d/%m/%Y") 

    for url in url_list:
        store_name = get_store_name_from_url(url)
        product_name = extract_product_name(url,store_name)

        price = extract_price_selenium(url, store_name)
        price_number = float(price.replace('$', '').replace('.', '').replace(',', '.')) if price != 'Precio no encontrado' else None
        products[product_name] = price_number

        print(f"URL: {url}")
        print(f"Nombre del Producto: {product_name}")
        print(f"Precio: {price}")
        print("-" * 50)

    return {today: {store_name: products}}


def process_all(urls: list):
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


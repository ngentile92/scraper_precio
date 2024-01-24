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


def extract_product_name(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        product_span = soup.find('span', class_='vtex-store-components-3-x-productBrand')
        product_name = product_span.get_text().strip() if product_span else 'Nombre del producto no encontrado'
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
        price_div = driver.find_element(By.CLASS_NAME, 'discoargentina-store-theme-1dCOMij_MzTzZOCohX1K7w')
        price = price_div.text.strip() if price_div else 'Precio no encontrado'
        return price
    finally:
        driver.quit()
import json

def process_urls(url_list):
    products = {}  # Diccionario para almacenar los nombres de productos y precios

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
    with open(os.path.join('../data', 'productos.json'), 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

# Lista de URLs
urls = [
    'https://www.disco.com.ar/gaseosa-coca-cola-sabor-original-1-5-lt/p',
    'https://www.disco.com.ar/yerba-mate-suave-playadito-500-gr/p',
    'https://www.disco.com.ar/fernet-branca-750-ml-2/p'
]

# Procesar todas las URLs y guardar los resultados en un archivo JSON
process_urls(urls)

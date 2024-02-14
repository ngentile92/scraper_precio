import re
import time
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_store_name_from_url(url):
    if 'disco.com.ar' in url:
        return 'disco'
    elif 'mercadolibre.com.ar' in url:
        return 'MELI'
    elif 'carrefour.com.ar' in url:
        return 'carrefour'
    elif 'masonline.com.ar' in url:
        return 'chango_mas'
    elif 'dexter.com.ar' in url:
        return 'dexter'
    else:
        return 'unknown'

def extract_price_selenium(url, store_name):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        # time.sleep(1)  # Removido ya que usaremos esperas explícitas

        # Diccionario para mapear nombres de tiendas a sus selectores CSS
        store_selectors = {
            'disco': 'discoargentina-store-theme-1dCOMij_MzTzZOCohX1K7w',
            'carrefour': 'valtech-carrefourar-product-price-0-x-sellingPriceValue',
            'chango_mas': 'valtech-gdn-dynamic-product-0-x-dynamicProductPrice',
            'MELI': 'andes-money-amount__fraction',
            'dexter': 'value'  # Asumiendo que 'value' es suficientemente único
        }

        if store_name in store_selectors:
            # Espera explícita para el elemento específico de cada tienda
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, store_selectors[store_name]))
            )
            price_div = driver.find_element(By.CLASS_NAME, store_selectors[store_name])
        else:
            price_div = None

        return price_div.text.strip() if price_div else None
    except Exception as e:
        print(e)
        return None
    finally:
        driver.quit()


def process_all(urls: list, product_names: list):
    all_data = {}
    today = datetime.datetime.now().strftime("%d/%m/%Y")

    for url, product_name_unified in zip(urls, product_names):
        store_name = get_store_name_from_url(url)

        price = extract_price_selenium(url, store_name)
        if price != None:
            # Limpia el string de precio de caracteres no numéricos, excepto el punto y la coma
            cleaned_price = re.sub(r'[^\d.,]', '', price)
            
            # Reemplaza comas con puntos y elimina puntos adicionales que representan miles
            cleaned_price = cleaned_price.replace('.', '').replace(',', '.')

            # Busca números con o sin parte decimal
            match = re.search(r'\d+(\.\d+)?', cleaned_price)
            price_number = float(match.group(0)) if match else None
        else:
            price_number = None

        if today not in all_data:
            all_data[today] = {}
        if store_name not in all_data[today]:
            all_data[today][store_name] = {}

        all_data[today][store_name][product_name_unified] = price_number

        print(f"URL: {url}")
        print(f"Nombre del Producto: {product_name_unified}")
        print(f"Precio: {price_number if price_number is not None else price}")
        print("-" * 50)

    return all_data



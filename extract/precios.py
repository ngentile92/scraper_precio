import re
import time
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
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
    elif 'levi.com.ar' in url:
        return 'levis'
    else:
        return 'unknown'

def extract_price_selenium(url, store_name):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    max_retries = 5  # Número máximo de intentos
    retry_wait = 3  # Tiempo de espera inicial en segundos
    
    try:
        for attempt in range(max_retries):
            try:
                driver.get(url)

                store_selectors = {
                    'disco': 'discoargentina-store-theme-1dCOMij_MzTzZOCohX1K7w',
                    'carrefour': 'valtech-carrefourar-product-price-0-x-sellingPriceValue',
                    'chango_mas': 'valtech-gdn-dynamic-product-0-x-dynamicProductPrice',
                    'MELI': 'andes-money-amount__fraction',
                    'dexter': 'value'
                }

                if store_name in store_selectors:
                    WebDriverWait(driver, retry_wait).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, store_selectors[store_name]))
                    )
                    price_div = driver.find_element(By.CLASS_NAME, store_selectors[store_name])
                else:
                    price_div = None
                
                return price_div.text.strip() if price_div else None
            
            except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
                print(f"Error on attempt {attempt+1}: {e}")
                time.sleep(retry_wait)
                retry_wait *= 2  # Duplica el tiempo de espera para el próximo intento
            except Exception as e:
                print(f"Unhandled exception: {e}")
                break  # Rompe el bucle en caso de una excepción no manejada
    finally:
        driver.quit()
    
    return None

def process_all(urls: list, product_names: list):
    all_data = {}
    today = datetime.datetime.now().strftime("%d/%m/%Y")

    for url, base_product_name in zip(urls, product_names):
        store_name = get_store_name_from_url(url)

        if store_name == 'levis':
            prices = extract_multiple_prices_selenium(url)  # Asume esta es tu función para múltiples precios
            if prices:
                for i, price in enumerate(prices, start=1):
                    cleaned_price = re.sub(r'[^\d.,]', '', price).replace('.', '').replace(',', '.')
                    price_number = float(re.search(r'\d+(\.\d+)?', cleaned_price).group(0)) if re.search(r'\d+(\.\d+)?', cleaned_price) else None
                    
                    # Construye el nombre del producto con un índice secuencial
                    product_name = f"{base_product_name}_{i}"  # Ahora cada producto tendrá un identificador único
                    
                    if today not in all_data:
                        all_data[today] = {}
                    if store_name not in all_data[today]:
                        all_data[today][store_name] = {}
                    all_data[today][store_name][product_name] = price_number
        else:
            price = extract_price_selenium(url, store_name)  # Tu función existente
            if price is not None:
                cleaned_price = re.sub(r'[^\d.,]', '', price).replace('.', '').replace(',', '.')
                price_number = float(re.search(r'\d+(\.\d+)?', cleaned_price).group(0)) if re.search(r'\d+(\.\d+)?', cleaned_price) else None

                if today not in all_data:
                    all_data[today] = {}
                if store_name not in all_data[today]:
                    all_data[today][store_name] = {}

                all_data[today][store_name][base_product_name] = price_number

    return all_data

def extract_multiple_prices_selenium(url, max_attempts=3):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    attempt = 0
    prices = None
    
    while attempt < max_attempts and prices is None:
        try:
            driver.get(url)
            WebDriverWait(driver, 10 + attempt * 5).until(  # Incrementa el tiempo de espera en cada intento
                EC.visibility_of_all_elements_located((By.CLASS_NAME, 'vtex-product-price-1-x-sellingPriceValue'))
            )
            price_elements = driver.find_elements(By.CLASS_NAME, 'vtex-product-price-1-x-sellingPriceValue')
            prices = [element.text.strip() for element in price_elements if element.text.strip() != '']
            if prices:  # Si encontramos precios, termina el bucle
                break
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            print(f"Error en el intento {attempt + 1}: {e}")
        finally:
            attempt += 1
            if prices is None:
                time.sleep(5)  # Espera antes de intentar nuevamente
    
    driver.quit()
    return prices if prices else None


if __name__ == "__main__":
    import pandas as pd
    with open('../url_productos.csv', 'r') as f:
        datos = datos = pd.read_csv(f, encoding='ISO-8859-1')
        # Convertir a listas
        url_list = datos['URL'].tolist()

    # Extraer los nombres de los productos
    product_names_unified = datos['producto_unificado'].tolist()
    print(product_names_unified)
    # Extraer los precios de las URLs para cada producto
    data_json = process_all(url_list, product_names_unified)
    print(data_json)

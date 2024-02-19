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
from unidecode import unidecode

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
    elif 'zonaprop.com.ar' in url:
        return 'zonaprop'
    elif 'argenprop.com' in url:
        return 'argenprop'
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

def get_type_store(url):
    if 'order' in url:
        return 'all'
    elif 'Order' in url:
        return 'all'
    if 'depar' in url:
        return 'all'
    else:
        return 'single'
def process_all(urls: list, product_names: list):
    all_data = {}
    today = datetime.datetime.now().strftime("%d/%m/%Y")

    for url, base_product_name in zip(urls, product_names):
        store_name = get_store_name_from_url(url)
        type_url = get_type_store(url)
        if type_url == 'all':
            products_data = extract_multiple_prices_and_names_selenium(url, store_name)  # Asegúrate de pasar store_name
            if products_data:
                for product in products_data:
                    product_name = product['name']
                    # Comprueba si 'price' ya es un número (float), en cuyo caso no necesita limpieza
                    if isinstance(product['price'], float):
                        price_number = product['price']
                    else:
                        # Solo intenta limpiar y convertir si 'price' es una cadena
                        cleaned_price = re.sub(r'[^\d.,]', '', product['price']).replace('.', '').replace(',', '.')
                        price_number = float(re.search(r'\d+(\.\d+)?', cleaned_price).group(0)) if re.search(r'\d+(\.\d+)?', cleaned_price) else None

                    if today not in all_data:
                        all_data[today] = {}
                    if store_name not in all_data[today]:
                        all_data[today][store_name] = {}
                    all_data[today][store_name][product_name] = price_number

        else:
            price_data = extract_price_selenium(url, store_name)  # Devuelve una cadena o None
            if price_data:
                cleaned_price = re.sub(r'[^\d.,]', '', price_data).replace('.', '').replace(',', '.')
                price_number = float(re.search(r'\d+(\.\d+)?', cleaned_price).group(0)) if re.search(r'\d+(\.\d+)?', cleaned_price) else None

                if today not in all_data:
                    all_data[today] = {}
                if store_name not in all_data[today]:
                    all_data[today][store_name] = {}

                # Utiliza base_product_name ya que no podemos extraer el nombre del producto de price_data directamente
                all_data[today][store_name][base_product_name] = price_number

    return all_data



def extract_and_sum_prices(text):
    # Encuentra todos los números en el texto
    numbers = re.findall(r'\$([\d.]+)', text)
    # Convierte los números encontrados a flotantes y suma
    total = sum([float(number.replace('.', '')) for number in numbers])
    return total

# https://www.zonaprop.com.ar/departamentos-alquiler-capital-federal-mas-de-1-bano-1-habitacion-2-ambientes-sin-garages-40-50-m2-cubiertos.html,departamentos CABA

def clean_text(text):
    # Translitera caracteres a sus equivalentes ASCII
    clean_text = unidecode(text)
    return clean_text

def extract_multiple_prices_and_names_selenium(url, store_name, max_attempts=3):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    attempt = 0
    data = []

    store_selectors = {
        # Actualiza los selectores según sea necesario
        'levis': {
            'price': 'vtex-product-price-1-x-sellingPriceValue',
            'name': '.vtex-product-summary-2-x-productBrand.vtex-product-summary-2-x-brandName.t-body'
        },
        'carrefour': {
            'price': 'valtech-carrefourar-product-price-0-x-sellingPriceValue',
            'name': '.vtex-product-summary-2-x-productBrand.vtex-product-summary-2-x-brandName.t-body'
        },
        'disco': {
            'price': 'discoargentina-store-theme-1dCOMij_MzTzZOCohX1K7w',
            'name': '.vtex-product-summary-2-x-productBrand.vtex-product-summary-2-x-brandName.t-body'
        },
        'zonaprop': {
            'price': '[data-qa="POSTING_CARD_PRICE"]',  # Actualizado para uso de atributos
            'name': '[data-qa="POSTING_CARD_LOCATION"]',  # Actualizado para uso de atributos
        },
        'MELI': {
            'price': 'andes-money-amount__fraction',
            'name': 'ui-search-item__location-label'
    },
        'argenprop': {
            'price': '.card__price',  # Selector para el precio
            'name': '.card__title--primary.show-mobile'  # Selector para el nombre o ubicación
        }
    }



    if store_name not in store_selectors:
        print(f"Store name '{store_name}' not found in store selectors.")
        driver.quit()
        return None
    
    price_selector = store_selectors[store_name]['price']
    name_selector = store_selectors[store_name]['name']
    print(f"Using price selector '{price_selector}' and name selector '{name_selector}' for store '{store_name}'")
    while attempt < max_attempts and not data:
        try:
            driver.get(url)
            time.sleep(2)  # Espera inicial para que la página comience a cargar
            
            # Simula el desplazamiento hacia abajo para cargar más productos
            for _ in range(15):  # Ajusta según la necesidad de la página
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            # Cambio para 'zonaprop'
            if store_name == 'zonaprop' or store_name == 'MELI' or store_name == 'argenprop':
                # Uso de presence_of_all_elements_located para zonaprop
                price_elements = WebDriverWait(driver, 30).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, price_selector))
                )
                name_elements = WebDriverWait(driver, 30).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, name_selector))
                )

                price_elements = driver.find_elements(By.CSS_SELECTOR, price_selector)
                name_elements = driver.find_elements(By.CSS_SELECTOR, name_selector)
                if store_name == 'argenprop':
                    prices = []
                    for element in price_elements:
                        price_text = element.text.strip()
                        total_price = extract_and_sum_prices(price_text)
                        prices.append(total_price)
                else:
                    prices = [element.text.strip() for element in price_elements if element.text.strip() != '']

            else:
                # Espera explícita para los precios
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_all_elements_located((By.CLASS_NAME, price_selector))
                )
                
                # Espera explícita para los nombres
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_all_elements_located((By.CSS_SELECTOR, name_selector))
                )
                price_elements = driver.find_elements(By.CLASS_NAME, price_selector)
                name_elements = driver.find_elements(By.CSS_SELECTOR, name_selector)

            names = [clean_text(element.text.strip()) for element in name_elements if element.text.strip() != '']

            print(price_elements)
            print(name_elements)            
            data = [{'name': name, 'price': price} for name, price in zip(names, prices) if name and price]
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            print(f"Error en el intento {attempt + 1}: {e}")
        finally:
            attempt += 1
            if not data:
                time.sleep(5)
    
    driver.quit()
    return data if data else None



if __name__ == "__main__":
    import pandas as pd
    with open('../url_alquileres.csv', 'r') as f:
        datos = datos = pd.read_csv(f, encoding='ISO-8859-1')
        # Convertir a listas
        url_list = datos['URL'].tolist()

    # Extraer los nombres de los productos
    product_names_unified = datos['producto_unificado'].tolist()
    # Extraer los precios de las URLs para cada producto
    data_json = process_all(url_list, product_names_unified)

    print(data_json)
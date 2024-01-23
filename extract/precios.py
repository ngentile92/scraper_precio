import requests
from bs4 import BeautifulSoup

url = 'https://www.disco.com.ar/gaseosa-coca-cola-sabor-original-1-5-lt/p'


def extract_information(url):
    # Enviar una solicitud HTTP GET a la URL
    response = requests.get(url)

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        # Analizar el contenido HTML de la página web usando BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Buscar el elemento con el precio
        price_div = soup.find('div', class_='discoargentina-store-theme-1dCOMij_MzTzZOCohX1K7w')
        if price_div:
            price = price_div.get_text().strip()  # Extrae y devuelve el texto del precio
        else:
            price = 'Precio no encontrado'

        # Buscar el elemento con el nombre del producto
        product_span = soup.find('span', class_='vtex-store-components-3-x-productBrand')
        product_name = product_span.get_text() if product_span else 'Nombre del producto no encontrado'

        return price, product_name

    else:
        return 'Solicitud fallida', 'Solicitud fallida'

# Usar la función y mostrar los resultados
price, product_name = extract_information(url)
print(f"Precio: {price}")
print(f"Nombre del Producto: {product_name}")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time


options = Options()
options.headless = True

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(url)
    time.sleep(5)  # Ajusta este tiempo según sea necesario

    # Modificación aquí: Uso de By.CLASS_NAME
    price_div = driver.find_element(By.CLASS_NAME, 'discoargentina-store-theme-1dCOMij_MzTzZOCohX1K7w')
    price = price_div.text if price_div else 'Precio no encontrado'

    print(f'Precio: {price}')
finally:
    driver.quit()

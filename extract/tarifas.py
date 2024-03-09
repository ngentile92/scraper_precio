from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import requests
import json
from bs4 import BeautifulSoup
import re
import certifi
from load.gcs_load import load_tarifas_to_db

def extraer_enlaces_cuadros_tarifarios(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get(url)

    # Espera hasta que el iframe esté presente y luego cambia al iframe
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe")))
    
    # Ahora dentro del iframe, encuentra los enlaces
    enlaces_elementos = driver.find_elements(By.TAG_NAME, "a")

    enlace_cuadro = ""
    for enlace in enlaces_elementos:
        href = enlace.get_attribute('href')
        if href and '/web/tarifasd.nsf/todoscuadros/' in href:
            enlace_cuadro = href.replace('\\', '/')
            break  # Sale del bucle después de encontrar el primer enlace

    driver.quit()
    return enlace_cuadro

def obtener_html_con_selenium(enlaces):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    print("Inicializando WebDriver de Chrome en modo headless...")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    html_pages = []  # Lista para almacenar el HTML de cada página
    
    # Asegurarse de que enlaces sea una lista
    if not isinstance(enlaces, list):
        enlaces = [enlaces]
    
    for enlace in enlaces:
        try:
            print(f"Accediendo a {enlace}...")
            driver.get(enlace)
            print("Esperando a que la página se cargue...")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("Página cargada. Obteniendo el código fuente...")
            html = driver.page_source
            html_pages.append(html)
            print("Código fuente obtenido con éxito.")
        except Exception as e:
            print(f"Error al obtener el HTML con Selenium para {enlace}: {e}")
    
    print("Cerrando el WebDriver...")
    driver.quit()
    
    if not html_pages:
        print("No se pudo obtener el HTML de ningún enlace. Retornando lista vacía.")
    return html_pages




def procesar_html_para_usuarios_generales(enlace):
    resultado = {"Usuarios Generales": {"EDENOR": {"Fijo": "", "Variable": ""}, "EDESUR": {"Fijo": "", "Variable": ""}, "Fecha del Cuadro Tarifario": ""}}
    
    htmls = obtener_html_con_selenium(enlace)
    print(f"HTMLs obtenidos: {len(htmls)}")
    print(htmls)
    for html in htmls:
        soup = BeautifulSoup(html, 'html.parser')
        print(soup)
        # Buscar la fecha del cuadro tarifario
        cuadro_tarifario = soup.find('div', class_="bg-primary col-md-12 text-center")
        print(cuadro_tarifario)
        if cuadro_tarifario:
            # Extraer la fecha del texto dentro del <h4>
            fecha_cuadro = cuadro_tarifario.find('h4').get_text(strip=True)
            # Suponiendo que el formato es "Cuadro Tarifario - Período MM/AAAA."
            # y queremos extraer solo "MM/AAAA"
            fecha = fecha_cuadro.split(' ')[-1].rstrip('.')
            resultado["Usuarios Generales"]["Fecha del Cuadro Tarifario"] = fecha

        # Encontrar el título "Usuarios Generales"
        titulo_usuarios_generales = soup.find('h4', string="Usuarios Generales")

        # Procesar solo si encontramos el título
        if titulo_usuarios_generales:
            tabla_siguiente = titulo_usuarios_generales.find_next('table')
            if tabla_siguiente:
                filas = tabla_siguiente.find_all('tr', valign="top")

                for fila in filas:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 4:  # Asegurar que hay suficientes celdas
                        categoria = celdas[0].get_text(strip=True)

                        if "Cargo Fijo" in categoria:
                            resultado["Usuarios Generales"]["EDENOR"]["Fijo"] = celdas[2].get_text(strip=True)
                            resultado["Usuarios Generales"]["EDESUR"]["Fijo"] = celdas[3].get_text(strip=True)
                        elif "Cargo Variable" in categoria:
                            resultado["Usuarios Generales"]["EDENOR"]["Variable"] = celdas[2].get_text(strip=True)
                            resultado["Usuarios Generales"]["EDESUR"]["Variable"] = celdas[3].get_text(strip=True)

    return resultado


def obtener_html_de_enlaces(enlaces):
    htmls = []
    for enlace in enlaces:
        respuesta = requests.get(enlace)
        if respuesta.status_code == 200:
            htmls.append(respuesta.text)
        else:
            print(f"Error al obtener {enlace}: Estado {respuesta.status_code}")
    return htmls


def limpiar_titulos(resultado):
    # Crear un nuevo diccionario para almacenar los resultados limpios
    resultado_limpio = {}

    # Compilar la expresión regular para detectar las variantes de "Período"
    regex_periodo = re.compile(r'Per\u00c3\u00adodo|Período')

    for titulo, datos in resultado.items():
        # Reemplazar las variantes de "Período" con una cadena vacía
        titulo_limpio = regex_periodo.sub('', titulo)

        # Asegurarse de eliminar espacios adicionales que puedan haber quedado
        titulo_limpio = titulo_limpio.strip()

        # Asignar los datos al título limpio en el nuevo diccionario
        resultado_limpio[titulo_limpio] = datos

    return resultado_limpio


if __name__ == '__main__':
    URL = "https://www.argentina.gob.ar/enre/cuadros_tarifarios"
    enlace_cuadro_tarifario = extraer_enlaces_cuadros_tarifarios(URL)
    resultados_globales = []
    #enlace_cuadro_tarifario = [
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/EE287D6D2EC07DE70325894B00640A20?opendocument",
    #    "https://www.enre.gov.ar/web/TARIFASD.nsf/todoscuadros/6AF98FD8169DDCB403258966004CE1ED?opendocument",
    #    "https://www.enre.gov.ar/web/TARIFASD.nsf/todoscuadros/02F87103D2A44EFA03258967004C56EB?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/2C70F98CD96070C2032589A6003EB4F1?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/C39BA4874DCA1FEF03258854004FBE7D?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/498ACB3ED0593512032588780042D316?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/DA9ACE2067B6D9F70325889100482B86?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/6831EEB39C0A5E2F032586CB006834CA?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/EB3643E64C0963C7032588D8004CB1D9?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/9BDA7860C6E30AFB032588EF00448161?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/C6449DE85BF30A030325890F006B5510?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/949C99A58F4C79EA0325892D00662E40?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/70443DAC0651153D032589B4004218B8?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/0C4CDDE197FF7409032589E4005EF7CB?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/D0A25F2999EC0CC1032589F900667B84?opendocument",
    #    "https://www.enre.gov.ar/web/TARIFASD.nsf/todoscuadros/77005EF0D0961ED403258A21004793BF?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/C120B41EBDDE16CD03258A3C003BD252?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/7F88055965CC017903258A5F00459959?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/BAF634BB93647DEA03258A7C00432386?opendocument",
    #    "https://www.enre.gov.ar/web/tarifasd.nsf/todoscuadros/A0CE9C40FB1AF8F203258AA20051EC60?opendocument"
    #]
    print(f"Enlace encontrado: {enlace_cuadro_tarifario}")

    datos_tarifas = procesar_html_para_usuarios_generales(enlace_cuadro_tarifario)
    datos_tarifas_limpio = limpiar_titulos(datos_tarifas)
    resultados_globales.append(datos_tarifas_limpio)

    # Cargar los datos a la base de datos
    load_tarifas_to_db(resultados_globales)

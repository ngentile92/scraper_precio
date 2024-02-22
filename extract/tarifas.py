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

def obtener_html_de_enlaces(enlace):
    htmls = []
    try:
        respuesta = requests.get(enlace)
        if respuesta.status_code == 200:
            htmls.append(respuesta.text)
        else:
            print(f"Error al obtener {enlace}: Estado {respuesta.status_code}")
    except requests.exceptions.MissingSchema as e:
        print(f"Error en la URL {enlace}: {e}")
    return htmls

def procesar_html_para_usuarios_generales(urls):
    resultado = {"Usuarios Generales": {"EDENOR": {"Fijo": "", "Variable": ""}, "EDESUR": {"Fijo": "", "Variable": ""}, "Fecha del Cuadro Tarifario": ""}}
    
    htmls = obtener_html_de_enlaces(urls)
    for html in htmls:
        soup = BeautifulSoup(html, 'html.parser')


        # Buscar la fecha del cuadro tarifario
        cuadro_tarifario = soup.find('div', class_="bg-primary col-md-12 text-center")
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
    print(f"Enlace encontrado: {enlace_cuadro_tarifario}")
    datos_tarifas = procesar_html_para_usuarios_generales([enlace_cuadro_tarifario])

    datos_tarifas_limpio = limpiar_titulos(datos_tarifas)

    # Convertir los datos a JSON
    with open('datos_tarifas.json', 'w') as fp:
        json.dump(datos_tarifas_limpio, fp, ensure_ascii=False)
   

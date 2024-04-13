"""
extrae las variables principales de politica monetaria
"""
import requests
from bs4 import BeautifulSoup
import json

def extract_BCRA_info(url: str ='https://www.bcra.gob.ar/PublicacionesEstadisticas/Principales_variables.asp') -> json:
    # Realizamos la petición a la web
    response = requests.get(url, verify=False)

    # Verificamos que la petición se haya realizado correctamente con response.status_code == 200
    if response.status_code == 200:
        # Procesamos la respuesta con Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscamos la tabla por alguna característica distintiva, por ejemplo, su clase CSS
        table = soup.find('table', class_='table-BCRA')

        # Inicializamos un diccionario para guardar los datos en el formato deseado
        data_json = {}

        # Iteramos sobre las filas de la tabla extrayendo las variables, fechas y valores
        for row in table.find_all('tr')[1:]:  # [1:] para saltar la fila de encabezados
            cells = row.find_all('td')
            if len(cells) == 3:  # Verificamos que la fila tenga la cantidad esperada de celdas
                variable = cells[0].text.strip()
                fecha = cells[1].text.strip()
                valor = cells[2].text.strip().replace('.', '').replace(',', '.')
                
                # Agregamos los datos al diccionario JSON
                if variable not in data_json:
                    data_json[variable] = {}
                data_json[variable][fecha] = valor

        return data_json
    else:
        print("Error al realizar la petición, código de estado:", response.status_code)

def clean_json_data(json_data):
    cleaned_data = {}
    for variable, dates in json_data.items():
        # Limpiar el nombre de la variable
        cleaned_variable = ' '.join(variable.split()).replace(u'\xa0', ' ')
        cleaned_variable = cleaned_variable.split(' - ')[0]  # Tomamos solo la primera parte antes del ' - ' si existe
        cleaned_variable = cleaned_variable.split('\n')[0]  # Eliminar saltos de línea y tomar la primera parte
        # Añadir la variable limpia al nuevo diccionario
        if cleaned_variable not in cleaned_data:
            cleaned_data[cleaned_variable] = {}
        for date, value in dates.items():
            # Asegurar que la fecha esté limpia también
            cleaned_date = ' '.join(date.split())
            # Añadir la fecha y el valor a la variable limpia
            cleaned_data[cleaned_variable][cleaned_date] = value
    return cleaned_data

def process_BCRA():
    print("Extrayendo información de BCRA...")
    data_json = extract_BCRA_info()
    print("Información extraída con éxito.")
    data_json = clean_json_data(data_json)
    print("Datos limpios.")
    return data_json
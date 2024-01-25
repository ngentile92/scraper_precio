import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


def extract_dolar_info(url: str='https://www.infodolar.com/'):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        dolar_data = []

        # Lista de nombres deseados
        nombres_deseados = ['Dólar Blue', 'Dólar MEP', 'Dólar CCL', 'Banco Nación']

        # Buscar todas las filas de la tabla de cotizaciones
        rows = soup.find_all('tr')
        for row in rows:
            col_nombre = row.find('td', class_='colNombre')
            col_compra_venta = row.find_all('td', class_='colCompraVenta')

            if col_nombre and col_compra_venta:
                nombre = col_nombre.get_text(strip=True)
                # Verificar si el nombre está en la lista de nombres deseados
                if any(nombre_deseado in nombre for nombre_deseado in nombres_deseados):
                    compra = col_compra_venta[0].get_text(strip=True) if len(col_compra_venta) > 0 else None
                    venta = col_compra_venta[1].get_text(strip=True) if len(col_compra_venta) > 1 else None

                    dolar_data.append({
                        'Nombre': nombre,
                        'Compra': compra,
                        'Venta': venta
                    })

        return dolar_data
    else:
        return 'Solicitud fallida'
    

def limpiar_y_estructurar_datos(dolar_info):
    data_limpia = {}
    fecha_scrapeo = datetime.now().strftime("%d/%m/%Y")
    
    nombres_deseados = ['Dólar Blue', 'Dólar MEP', 'Dólar CCL', 'Banco Nación']

    for info in dolar_info:
        nombre = next((nombre_deseado for nombre_deseado in nombres_deseados if nombre_deseado in info['Nombre']), None)
        if nombre:
            compra = re.findall(r'\$\s*\d+[\.,]?\d*', info['Compra'])[0]
            venta = re.findall(r'\$\s*\d+[\.,]?\d*', info['Venta'])[0]

            # Quitar el signo $, reemplazar comas por nada y convertir a float
            compra = float(compra.replace('$', '').replace(',', '').replace('.', ''))
            venta = float(venta.replace('$', '').replace(',', '').replace('.', ''))

            data_limpia[nombre] = {
                'compra': compra,
                'venta': venta
            }

    return {fecha_scrapeo: data_limpia}


def scrapeo_dolar():
    # Llamar a la función de extracción y luego a la de limpieza y estructuración
    dolar_info = extract_dolar_info()
    datos_estructurados = limpiar_y_estructurar_datos(dolar_info)

    return datos_estructurados
if __name__ == '__main__':
    print(scrapeo_dolar())
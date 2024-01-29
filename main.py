"""
Archivo principal de lógica del programa
"""
import json
import argparse
import pandas as pd

from prefect import flow


from extract.precios import process_all
from extract.dolar import scrapeo_dolar
from load.gcs_load import load_data_to_db, load_dolar_to_db
 
@flow
def pipeline_supermercados():
    """
    Función que ejecuta el pipeline de supermercados
    - Scrapea los datos de las URLs provistas en el .csv
    - Carga los datos en la base de datos
    """
    # Extraer los datos de las URLs
    # Open csv file
    with open('url_productos.csv', 'r') as f:
        datos = datos = pd.read_csv(f, encoding='ISO-8859-1')
        # Convertir a listas
        url_list = datos['URL'].tolist()

    # Extraer los nombres de los productos
    product_names_unified = datos['producto_unificado'].tolist()
    # Extraer los precios de las URLs para cada producto
    data_json = process_all(url_list, product_names_unified)

    print(data_json)

    # Cargar los datos en la base de datos
    load_data_to_db(data_json)

@flow
def pipeline_dolar():
    """
    Función que ejecuta el pipeline de dólar
    - Scrapea los datos de dolar de la pagina 'https://www.infodolar.com/'
    - Carga los datos en la base de datos
    """
    dolar_info = scrapeo_dolar()
    dolar_info_json = json.dumps(dolar_info)
    load_dolar_to_db(dolar_info_json)

def main() -> None:


    parser = argparse.ArgumentParser(description="Ejecuta el pipeline de supermercados o de dólar")

    parser.add_argument(
        "--supermercados",
        action="store_true",
        help="Ejecuta el pipeline de supermercados"
    )

    parser.add_argument(
        "--dolar",
        action="store_true",
        help="Ejecuta el pipeline de dólar"
    )

    args = parser.parse_args()

    if args.supermercados:
        pipeline_supermercados()
    elif args.dolar:
        pipeline_dolar()
    else:
        print("Debe especificar el pipeline a ejecutar")
        parser.print_help()

#################################################################################################################
#################################################################################################################

if __name__ == "__main__":
    main()

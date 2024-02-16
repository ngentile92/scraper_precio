"""
Archivo principal de lógica del programa
"""
import json
import argparse
import pandas as pd

from extract.precios import process_all
from extract.dolar import scrapeo_dolar
from extract.BCRA import process_BCRA
from load.gcs_load import load_data_to_db, load_dolar_to_db, load_bcra_to_db, load_categorias_productos_to_db
 
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
    #load_data_to_db(data_json)

def pipeline_dolar():
    """
    Función que ejecuta el pipeline de dólar
    - Scrapea los datos de dolar de la pagina 'https://www.infodolar.com/'
    - Carga los datos en la base de datos
    """
    dolar_info = scrapeo_dolar()
    dolar_info_json = json.dumps(dolar_info)
    load_dolar_to_db(dolar_info_json)

def pipeline_BCRA():
    """
    Función que ejecuta el pipeline de dólar
    - Scrapea los datos de dolar de la pagina bcra
    - Carga los datos en la base de datos
    """
    BCRA_data = process_BCRA()
    load_bcra_to_db(BCRA_data)

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
    parser.add_argument(
        "--bcra",
        action="store_true",
        help="ejecuta pipeline de BCRA estadisticas diarias"
    )
    parser.add_argument(
        "--categorias-productos",
        action="store_true",
        help="ejecuta pipeline de categorias de productos"
    )
    parser.add_argument(
        "--correr-todo",
        action="store_true",
        help="todos los flows empezando por dolar, bcra y luego supermercados"
    )
    args = parser.parse_args()

    if args.supermercados:
        pipeline_supermercados()
    elif args.dolar:
        pipeline_dolar()
    elif args.bcra:
        pipeline_BCRA()
    elif args.categorias_productos:
        load_categorias_productos_to_db('producto_categorias.csv')
    elif args.correr_todo:
        pipeline_dolar()
        pipeline_BCRA()
        pipeline_supermercados()
    else:
        print("Debe especificar el pipeline a ejecutar")
        parser.print_help()

#################################################################################################################
#################################################################################################################

if __name__ == "__main__":
    main()

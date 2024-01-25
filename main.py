"""
Archivo principal de lógica del programa
"""
import pandas as pd
from extract.precios import process_all
import json
from load.gcs_load import load_data_to_db
#from load.gcs_load import load_data_to_db
 

def main():
    # Extraer los datos de las URLs
    # Open csv file
    with open('url_productos.csv', 'r') as f:
        datos = pd.read_csv(f)
    url_list = datos['URL'].tolist()
    product_names_unified = datos['producto_unificado'].tolist()
    process_all(url_list, product_names_unified)
    # Cargar los datos en la base de datos
    with open('./data/productos.json', 'r') as f:
        data_json = f.read()
    load_data_to_db(data_json)

        
if __name__ == "__main__":
    main()
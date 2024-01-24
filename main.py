"""
Archivo principal de lógica del programa
"""
import pandas as pd
from extract.precios import process_all
#from load.gcs_load import load_data_to_db


def main():
    # Extraer los datos de las URLs
    
    # Open csv file
    with open('urls_to_scrap.csv', 'r') as f:
        urls = pd.read_csv(f)

    process_all(urls["URL"].tolist())

    # Cargar los datos en la base de datos
    with open('../data/productos.json', 'r') as f:
        data_json = f.read()

    #load_data_to_db(data_json)
        
if __name__ == "__main__":
    main()
import mysql.connector
import json
from datetime import datetime
import os
#import from .env variables
from dotenv import load_dotenv
load_dotenv()

GCS_PASSWORD = os.getenv("GCS_PASSWORD")
GCS_USER_ROOT=os.getenv("GCS_USER_ROOT")
GCS_HOST=os.getenv("GCS_HOST")
GCS_DATABASE=os.getenv("GCS_DATABASE")
# Reemplaza 'your_username', 'your_password', 'your_host', 'your_database' con tus propios detalles de la base de datos.


# Esta es tu estructura JSON
# abrir json con los datos que estan en ../data
with open('../data/productos.json', 'r') as f:
    data_json = f.read()

# Función para cargar los datos en la base de datos
def load_data_to_db(json_data):

    # Establecer la conexión dentro de la función
    try:
        conn = mysql.connector.connect(
            user=GCS_USER_ROOT,
            password=GCS_PASSWORD,
            host=GCS_HOST,
            database=GCS_DATABASE
        )
        cursor = conn.cursor()

        data = json.loads(json_data)
        for date, chains in data.items():
            formatted_date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d %H:%M:%S")
            for chain, products in chains.items():
                for product, price in products.items():
                    price_value = 'NULL' if price != price else price
                    sql = f"""INSERT INTO almacen (date, producto, precio, cadena)
                              VALUES (%s, %s, %s, %s)"""
                    cursor.execute(sql, (formatted_date, product, price_value, chain))

        conn.commit()
    except mysql.connector.Error as err:
        print("Error in SQL operation: ", err)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# Cerrar la conexión


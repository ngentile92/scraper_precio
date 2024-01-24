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
conn = mysql.connector.connect(
    user=GCS_USER_ROOT,
    password=GCS_PASSWORD,
    host=GCS_HOST,
    database=GCS_DATABASE
)
cursor = conn.cursor()

# Esta es tu estructura JSON
# abrir json con los datos que estan en ../data
with open('../data/productos.json', 'r') as f:
    data_json = f.read()

# Función para cargar los datos en la base de datos
def load_data_to_db(json_data):
    data = json.loads(json_data)
    for date, chains in data.items():
        # Formatear la fecha del JSON para que coincida con el formato de MySQL DATETIME
        formatted_date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d %H:%M:%S")
        for chain, products in chains.items():
            for product, price in products.items():
                # Comprueba si el precio es NaN (no un número) y lo reemplaza con NULL para SQL
                price_value = 'NULL' if price != price else price
                try:
                    # Crear y ejecutar el comando SQL
                    sql = f"""INSERT INTO almacen (date, producto, precio, cadena)
                              VALUES (%s, %s, %s, %s)"""
                    cursor.execute(sql, (formatted_date, product, price_value, chain))
                except mysql.connector.Error as err:
                    print("Something went wrong: {}".format(err))
    
    # Asegurarse de que se hagan los cambios en la base de datos
    conn.commit()

# Llamar a la función con nuestro JSON
load_data_to_db(data_json)

# Cerrar la conexión
cursor.close()
conn.close()

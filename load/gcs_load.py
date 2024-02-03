import mysql.connector
import json
from datetime import datetime
import os
#import from .env variables
from dotenv import load_dotenv
load_dotenv(".env")

GCS_PASSWORD = os.getenv("GCS_PASSWORD")
GCS_USER_ROOT=os.getenv("GCS_USER_ROOT")
GCS_DATABASE=os.getenv("GCS_DATABASE")
GCS_HOST=os.getenv("GCS_HOST")
# Reemplaza 'your_username', 'your_password', 'your_host', 'your_database' con tus propios detalles de la base de datos.

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

        data = json_data
        for date, chains in data.items():
            formatted_date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d %H:%M:%S")
            for chain, products in chains.items():
                for product, price in products.items():
                    price_value = 'NULL' if price != price else price
                    sql = f"""INSERT INTO precios (date, producto, precio, cadena)
                              VALUES (%s, %s, %s, %s)"""
                    cursor.execute(sql, (formatted_date, product, price_value, chain))

        conn.commit()
    except mysql.connector.Error as err:
        print("Error in SQL operation: ", err)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def load_dolar_to_db(json_data):
    try:
        conn = mysql.connector.connect(
            user=GCS_USER_ROOT,
            password=GCS_PASSWORD,
            host=GCS_HOST,
            database=GCS_DATABASE
        )
        cursor = conn.cursor()
        print("Connected to MySQL database")

        data = json.loads(json_data)
        for date, currencies in data.items():
            formatted_date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d %H:%M:%S")
            
            # Preparar los datos como JSON para cada tipo de dólar
            dolar_blue = json.dumps(currencies.get('Dólar Blue', {}))
            dolar_mep = json.dumps(currencies.get('Dólar MEP', {}))
            dolar_ccl = json.dumps(currencies.get('Dólar CCL', {}))
            dolar_oficial = json.dumps(currencies.get('Banco Nación', {}))

            sql = """INSERT INTO dolar (date, dolar_blue, dolar_mep, dolar_ccl, dolar_oficial)
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (formatted_date, dolar_blue, dolar_mep, dolar_ccl, dolar_oficial))

        conn.commit()
        
    except mysql.connector.Error as err:
        print("Error in SQL operation: ", err)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# Function to load BCRA data into the MySQL database
# Function to load or update BCRA data into the MySQL database
def load_bcra_to_db(json_data):
    try:
        conn = mysql.connector.connect(
            user=GCS_USER_ROOT,
            password=GCS_PASSWORD,
            host=GCS_HOST,
            database=GCS_DATABASE
        )
        cursor = conn.cursor()
        print("Connected to MySQL database")

        # Make sure that the combination of `variable` and `fecha` is a unique index in your MySQL table
        for variable, dates_values in json_data.items():
            for date, value in dates_values.items():
                formatted_date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d %H:%M:%S")

                # SQL query with ON DUPLICATE KEY UPDATE clause
                sql = """INSERT INTO BCRA (variable, fecha, valor)
                         VALUES (%s, %s, %s)
                         ON DUPLICATE KEY UPDATE valor = VALUES(valor)"""
                cursor.execute(sql, (variable, formatted_date, value))

        conn.commit()
        print("Data loaded successfully")
        
    except mysql.connector.Error as err:
        print("Error in SQL operation: ", err)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection is closed")

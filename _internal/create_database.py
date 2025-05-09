import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import configparser
import os
# -*- coding: utf-8 -*-
# Cargar configuración
config = configparser.ConfigParser()
config_file_path = os.path.join(os.path.dirname(__file__), "config.ini")
config.read(config_file_path)

DB_NAME = config.get('database', 'database')
DB_USER = config.get('database', 'user')
DB_PASSWORD = config.get('database', 'password')
DB_HOST = config.get('database', 'host')
DB_PORT = config.get('database', 'port')

def crear_base_de_datos():
    try:
        conn = psycopg2.connect(
            dbname="postgres",  # Se conecta a la base default
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Verificar si la base ya existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s;", (DB_NAME,))
        existe = cursor.fetchone()

        if not existe:
            cursor.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"Base de datos '{DB_NAME}' creada exitosamente.")
        else:
            print(f"La base de datos '{DB_NAME}' ya existe.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error creando la base de datos: {e}")

if __name__ == "__main__":
    crear_base_de_datos()
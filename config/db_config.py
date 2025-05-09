import psycopg2
import configparser
import os
import sys

def get_connection():
    config = configparser.ConfigParser()
    config_file_path = os.path.join(os.path.dirname(__file__), "../config.ini")
    config.read(config_file_path)

    if not config.sections():
        print("❌ Error al leer el archivo config.ini")
        return None

    try:
        dbname = config.get("database", "database")
        user = config.get("database", "user")
        password = config.get("database", "password")
        host = config.get("database", "host")
        port = config.get("database", "port")

        return psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )

    except Exception as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        return None
import psycopg2
import configparser
import os

# Cargar configuración
config = configparser.ConfigParser()
config_file_path = os.path.join(os.path.dirname(__file__), "config.ini")
config.read(config_file_path)

query = """
CREATE TABLE IF NOT EXISTS pacientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    dni VARCHAR(20) UNIQUE NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    pbs BOOLEAN DEFAULT FALSE,
    pbs_ultima_renovacion DATE
);
"""

def get_connection():
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

def crear_tabla_pacientes():
    try:
        conn = get_connection()
        if conn:
            cur = conn.cursor()
            # Verificar si la tabla ya existe
            cur.execute("SELECT 1 FROM pg_tables WHERE tablename='pacientes';")
            existe = cur.fetchone()

            if existe:
                print("La tabla 'pacientes' ya existe.")
            else:
                cur.execute(query)
                print("Tabla 'pacientes' creada correctamente.")

            conn.commit()
            cur.close()
            conn.close()
        else:
            print("No se pudo conectar a la base de datos.")
    except Exception as e:
        print(f"Error al crear la tabla: {e}")

if __name__ == "__main__":
    crear_tabla_pacientes()
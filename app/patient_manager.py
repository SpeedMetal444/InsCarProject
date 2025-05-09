import psycopg2
from config.db_config import get_connection
from datetime import date, timedelta

def buscar_paciente(dni=None, nombre=None, apellido=None):
    try:
        conn = get_connection()
        if not conn:
            return None
        cur = conn.cursor()

        if dni:
            cur.execute("SELECT * FROM pacientes WHERE dni = %s;", (dni,))
        elif nombre and apellido:
            cur.execute("SELECT * FROM pacientes WHERE nombre ILIKE %s AND apellido ILIKE %s;", (nombre, apellido))
        else:
            print("⚠️ Debes ingresar un DNI o nombre y apellido.")
            return None

        paciente = cur.fetchone()
        cur.close()
        conn.close()

        if paciente:
            return {
                "id": paciente[0],
                "nombre": paciente[1],
                "apellido": paciente[2],
                "dni": paciente[3],
                "direccion": paciente[4],
                "telefono": paciente[5],
                "pbs": paciente[6],
                "pbs_ultima_renovacion": paciente[7]
            }
        return None

    except Exception as e:
        print(f"❌ Error al buscar paciente: {e}")
        return None
    
def buscar_pacientes(nombre, apellido):
    try:
        conn = get_connection()
        if not conn:
            return []
        cur = conn.cursor()

        cur.execute("SELECT * FROM pacientes WHERE nombre ILIKE %s AND apellido ILIKE %s;", (f"%{nombre}%", f"%{apellido}%"))

        pacientes = cur.fetchall()
        cur.close()
        conn.close()

        return [
            {
                "id": paciente[0],
                "nombre": paciente[1],
                "apellido": paciente[2],
                "dni": paciente[3],
                "direccion": paciente[4],
                "telefono": paciente[5],
                "pbs": paciente[6],
                "pbs_ultima_renovacion": paciente[7]
            }
            for paciente in pacientes
        ]

    except Exception as e:
        print(f"❌ Error al buscar pacientes: {e}")
        return []
    
def agregar_paciente(nombre, apellido, dni, direccion, telefono, pbs):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pacientes (nombre, apellido, dni, direccion, telefono, pbs)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (nombre, apellido, dni, direccion, telefono, pbs))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error al registrar paciente: {e}")
        return False

def obtener_pbs_vencidos():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Fecha límite: hoy - 3 meses
        tres_meses_atras = date.today() - timedelta(days=90)

        query = """
        SELECT id, nombre, apellido, dni, pbs_ultima_renovacion
        FROM pacientes
        WHERE pbs = FALSE AND pbs_ultima_renovacion IS NOT NULL AND pbs_ultima_renovacion < %s
        ORDER BY pbs_ultima_renovacion DESC;
        """
        cursor.execute(query, (tres_meses_atras,))
        pacientes = cursor.fetchall()

        # Actualizar pbs a False para los pacientes vencidos
        update_query = """
        UPDATE pacientes
        SET pbs = FALSE
        WHERE pbs = TRUE AND pbs_ultima_renovacion IS NOT NULL AND pbs_ultima_renovacion < %s
        """
        cursor.execute(update_query, (tres_meses_atras,))
        conn.commit()

        cursor.close()
        conn.close()

        return pacientes
    except Exception as e:
        print(f"❌ Error obteniendo PBS vencidos: {e}")
        return []

def actualizar_paciente(paciente):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE pacientes
            SET nombre = %s, apellido = %s, direccion = %s, telefono = %s, pbs = %s
            WHERE dni = %s
        """, (
            paciente['nombre'],
            paciente['apellido'],
            paciente['direccion'],
            paciente['telefono'],
            paciente['pbs'],
            paciente['dni']
        ))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error al actualizar paciente: {e}")
        return False

def renovar_pbs(dni):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE pacientes
            SET pbs = TRUE, pbs_ultima_renovacion = %s
            WHERE dni = %s
        """, (date.today(), dni))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error al renovar PBS: {e}")
        return False

def eliminar_paciente(dni):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM pacientes WHERE dni = %s", (dni,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error al eliminar paciente: {e}")
        return False

from database import get_connection, hash_password
import pandas as pd
from email_utils import enviar_correo

# ---- Usuarios ----
def verificar_usuario(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, nombre, rol FROM usuarios
    WHERE email=? AND password_hash=?
    """, (email, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user  # (id, nombre, rol) o None

def registrar_usuario(nombre, email, password, rol):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO usuarios (nombre, email, password_hash, rol)
        VALUES (?, ?, ?, ?)
        """, (nombre, email, hash_password(password), rol))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# ---- Historias ----
def guardar_historia(numero_carpeta, cedula, servicio, fecha, usuario_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO historias_clinicas (numero_carpeta, cedula_paciente, servicio, fecha_recepcion, usuario_registro)
    VALUES (?, ?, ?, ?, ?)
    """, (numero_carpeta, cedula, servicio, fecha, usuario_id))
    conn.commit()
    conn.close()

def obtener_enfermeros():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM usuarios WHERE rol='user'")
    data = cursor.fetchall()
    conn.close()
    return data

def obtener_historias(fecha_ini, fecha_fin, enfermero_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if enfermero_id and enfermero_id != None:
        cursor.execute("""
            SELECT h.id, h.numero_carpeta, h.cedula_paciente, h.servicio, h.fecha_recepcion, u.nombre
            FROM historias_clinicas h
            JOIN usuarios u ON h.usuario_registro = u.id
            WHERE h.fecha_recepcion BETWEEN ? AND ? AND u.id = ?
        """, (fecha_ini, fecha_fin, enfermero_id))
    else:
        cursor.execute("""
            SELECT h.id, h.numero_carpeta, h.cedula_paciente, h.servicio, h.fecha_recepcion, u.nombre
            FROM historias_clinicas h
            JOIN usuarios u ON h.usuario_registro = u.id
            WHERE h.fecha_recepcion BETWEEN ? AND ?
        """, (fecha_ini, fecha_fin))

    data = cursor.fetchall()
    conn.close()
    return data

def agregar_observacion(historia_id, texto):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE historias_clinicas
        SET observacion=?, estado='pendiente'
        WHERE id=?
    """, (texto, historia_id))
    conn.commit()

    # Obtener email
    cursor.execute("""
        SELECT u.email
        FROM historias_clinicas h
        INNER JOIN usuarios u ON h.usuario_registro = u.id
        WHERE h.id=?
    """, (historia_id,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        correo_enfermero = resultado[0]
        enviar_correo(
            correo_enfermero,
            "Observación en historia clínica",
            f"Se ha agregado una observación en la historia #{numero_historia}. Por favor revisar."
        )

def exportar_reporte_excel(fecha_inicio=None, fecha_fin=None, usuario_id=None, ruta_salida="reporte.xlsx"):
    conn = get_connection()
    query = """
    SELECT h.id, h.numero_carpeta, h.cedula_paciente, h.servicio, h.fecha_recepcion, 
           u.nombre as enfermero, h.observacion, h.estado
    FROM historias_clinicas h
    INNER JOIN usuarios u ON h.usuario_registro = u.id
    WHERE 1=1
    """
    params = []

    if fecha_inicio:
        query += " AND date(h.fecha_recepcion) >= date(?)"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND date(h.fecha_recepcion) <= date(?)"
        params.append(fecha_fin)
    if usuario_id:
        query += " AND h.usuario_registro = ?"
        params.append(usuario_id)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if df.empty:
        return False

    df.to_excel(ruta_salida, index=False)
    return True

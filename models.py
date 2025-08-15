from database import get_connection, hash_password
import pandas as pd
from email_utils import enviar_correo
from datetime import date

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
            SELECT h.id, h.numero_carpeta, h.cedula_paciente, h.servicio, h.fecha_recepcion, u.nombre, h.estado
            FROM historias_clinicas h
            JOIN usuarios u ON h.usuario_registro = u.id
            WHERE h.fecha_recepcion BETWEEN ? AND ? AND u.id = ?
        """, (fecha_ini, fecha_fin, enfermero_id))
    else:
        cursor.execute("""
            SELECT h.id, h.numero_carpeta, h.cedula_paciente, h.servicio, h.fecha_recepcion, u.nombre, h.estado
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
        SET observacion=?, estado='devuelta'
        WHERE id=?
    """, (texto, historia_id))
    conn.commit()

    # Obtener email
    cursor.execute("""
        SELECT u.email, h.numero_carpeta,  h.observacion
        FROM historias_clinicas h
        INNER JOIN usuarios u ON h.usuario_registro = u.id
        WHERE h.id=?
    """, (historia_id,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        correo_enfermero, numero_carpeta, observacion= resultado
        mensaje = (
            f"Estimado(a),\n\n"
            f"Se ha agregado una observación a la historia clínica:\n"
            f"📂 Número de carpeta: {numero_carpeta}\n"
            f"📝 Observación: {observacion}\n\n"
            "Por favor, revisa el sistema para realizar las correcciones necesarias."
        )
        enviar_correo(
            correo_enfermero,
            "Observación en historia clínica",
            mensaje
        )

def exportar_reporte_excel(ruta_salida="reporte.xlsx"):
    conn = get_connection()
    query = """
    SELECT h.id, h.numero_carpeta, h.cedula_paciente, h.servicio, h.fecha_recepcion, 
           u.nombre as enfermero, h.observacion, h.estado
    FROM historias_clinicas h
    INNER JOIN usuarios u ON h.usuario_registro = u.id
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        return False

    df.to_excel(ruta_salida, index=False)
    return True

def marcar_entregada(historia_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE historias_clinicas
        SET estado='entregada', observacion=NULL
        WHERE id=?
    """, (historia_id,))
    conn.commit()
    conn.close()

def devolver_historia(historia_id, texto):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE historias_clinicas
        SET observacion=?, estado='devuelta'
        WHERE id=?
    """, (texto, historia_id))
    conn.commit()
    conn.close()

# Funciones para el usuario
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

def obtener_historias_devueltas(usuario_id: int):
    """Historias del usuario en estado 'devuelta'."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, numero_carpeta, cedula_paciente, servicio, fecha_recepcion, observacion
        FROM historias_clinicas
        WHERE usuario_registro = ? AND estado = 'devuelta'
        ORDER BY date(fecha_recepcion) DESC
    """, (usuario_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def obtener_historia_por_id(historia_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, numero_carpeta, cedula_paciente, servicio, fecha_recepcion, observacion, estado
        FROM historias_clinicas
        WHERE id = ?
    """, (historia_id,))
    row = cur.fetchone()
    conn.close()
    return row

def actualizar_historia_revisada(historia_id: int, numero_carpeta: str, cedula_paciente: str,servicio: str, fecha_recepcion: str | None = None):
    """
    Actualiza la historia devuelta; por defecto pone la fecha de hoy
    y cambia estado a 'revisada'.
    """
    if not fecha_recepcion:
        fecha_recepcion = date.today().isoformat()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE historias_clinicas
        SET numero_carpeta = ?, cedula_paciente = ?, servicio = ?, fecha_recepcion = ?, estado = 'revisada'
        WHERE id = ?
    """, (numero_carpeta, cedula_paciente, servicio, fecha_recepcion, historia_id))
    conn.commit()
    conn.close()
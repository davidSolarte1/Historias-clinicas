import hashlib
import mysql.connector

MYSQL_CFG = {
    "host": "172.20.100.141",   
    "user": "sireh_user",
    "password": "sireh27082025",
    "database": "sireh_db",
    "autocommit": False,
}

def get_connection():
    return mysql.connector.connect(**MYSQL_CFG)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# # --- PRUEBA DE CONEXIÓN ---
# if __name__ == "__main__":
#     try:
#         conn = get_connection()
#         print("✅ Conexión a MySQL exitosa")
#         cursor = conn.cursor()
#         cursor.execute("SHOW TABLES;")
#         print("Tablas encontradas:", cursor.fetchall())
#         cursor.execute("SELECT * FROM usuarios WHERE email=%s AND password_hash = %s",('dsolarte2809@gmail.com',hash_password('david'),))
#         print("se inicia sesion con:", cursor.fetchall())
        

#         conn.close()
#     except Exception as e:
#         print("❌ Error al conectar con MySQL:", e)
# """Esto en local"""

# # DB_NAME = "historias.db"

# # def get_connection():
# #     return sqlite3.connect(DB_NAME)

# """ ESto si se trabaja con la app en red"""
# DB_PATH = Path(r"\\172.20.100.145\fase_2_depuracion\Historias_Entregadas\bdhistorias.db") 
# # o \\192.168.1.25\AppHistorias\historias.db


# def create_tables():
#     conn = get_connection()
#     cursor = conn.cursor()

#     # Tabla usuarios
#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS usuarios (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         nombre TEXT NOT NULL,
#         email TEXT UNIQUE NOT NULL,
#         password_hash TEXT NOT NULL,
#         rol TEXT CHECK(rol IN ('admin', 'user')) NOT NULL
#     )
#     """)

#     # Tabla historias clínicas
#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS historias_clinicas (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         numero_carpeta TEXT NOT NULL,
#         cedula_paciente TEXT NOT NULL,
#         nombre_paciente TEXT NOT NULL,
#         apellido_paciente TEXT NOT NULL,
#         servicio TEXT NOT NULL,
#         fecha_recepcion TEXT NOT NULL,
#         observacion TEXT,
#         estado TEXT CHECK(estado IN ('registrada', 'devuelta', 'entregada', 'revisada')) DEFAULT 'registrada',
#         usuario_registro INTEGER NOT NULL,
#         fecha_devolucion TEXT NOT NULL DEFAULT '-',
#         fecha_entrega_nueva TEXT NOT NULL DEFAULT '-',
#         FOREIGN KEY(usuario_registro) REFERENCES usuarios(id)
#     )
#     """)

#     conn.commit()
#     conn.close()



# def seed_admin():
#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("SELECT * FROM usuarios WHERE rol='admin'")
#     admin = cursor.fetchone()

#     if not admin:
#         cursor.execute("""
#         INSERT INTO usuarios (nombre, email, password_hash, rol)
#         VALUES (?, ?, ?, ?)
#         """, ("Administrador", "admin", hash_password("Morita2025"), "admin"))
#         conn.commit()
#         # print("✅ Usuario administrador creado: admin / admin123")
#     conn.close()

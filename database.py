import sqlite3
import hashlib

DB_NAME = "historias.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT CHECK(rol IN ('admin', 'user')) NOT NULL
    )
    """)

    # Tabla historias clínicas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historias_clinicas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_carpeta TEXT NOT NULL,
        cedula_paciente TEXT NOT NULL,
        servicio TEXT NOT NULL,
        fecha_recepcion TEXT NOT NULL,
        observacion TEXT,
        estado TEXT CHECK(estado IN ('registrada', 'devuelta', 'entregada', 'revisada')) DEFAULT 'registrada',
        usuario_registro INTEGER NOT NULL,
        FOREIGN KEY(usuario_registro) REFERENCES usuarios(id)
    )
    """)

    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def seed_admin():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE rol='admin'")
    admin = cursor.fetchone()

    if not admin:
        cursor.execute("""
        INSERT INTO usuarios (nombre, email, password_hash, rol)
        VALUES (?, ?, ?, ?)
        """, ("Administrador", "admin", hash_password("admin123"), "admin"))
        conn.commit()
        print("✅ Usuario administrador creado: admin / admin123")
    conn.close()

if __name__ == "__main__":
    create_tables()
    seed_admin()
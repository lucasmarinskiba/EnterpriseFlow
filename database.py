import sqlite3
import os
from contextlib import contextmanager

DATABASE_PATH = "/tmp/enterpriseflow.db"  # Ruta válida en Streamlit Cloud

@contextmanager
def database_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        cursor = conn.cursor()
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT CHECK(role IN ('admin', 'manager', 'user'))''')
        # Tabla de logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                action TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        yield conn
    finally:
        conn.close()

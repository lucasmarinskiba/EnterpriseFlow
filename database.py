# database.py
import sqlite3
import hashlib

class DatabaseManager:
    def __init__(self, db_name="enterpriseflow.db"):
        self.conn = sqlite3.connect(db_name)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        ''')
        # Tabla de tareas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automations (
                user_email TEXT,
                type TEXT,
                data TEXT,
                FOREIGN KEY(user_email) REFERENCES users(email)
            )
        ''')
        self.conn.commit()

    def create_user(self, email: str, password: str):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users VALUES (?, ?)", (email, password_hash))
        self.conn.commit()

    def verify_user(self, email: str, password: str) -> bool:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor = self.conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE email=?", (email,))
        result = cursor.fetchone()
        return result[0] == password_hash if result else False

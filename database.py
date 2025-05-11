import sqlite3
import hashlib
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('enterpriseflow.db')
        self._create_tables()

    def _create_tables(self):
        """Crea estructura inicial de la base de datos"""
        tables = [
            '''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE,
                password TEXT,
                plan TEXT DEFAULT 'free',
                trial_end DATE
            )''',
            '''CREATE TABLE IF NOT EXISTS automation_tasks (
                id INTEGER PRIMARY KEY,
                user_email TEXT,
                task_type TEXT,
                schedule TEXT
            )'''
        ]
        
        for table in tables:
            self.conn.execute(table)
        self.conn.commit()

    def verify_user(self, email, password):
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        cursor = self.conn.execute(
            'SELECT * FROM users WHERE email=? AND password=?',
            (email, hashed_pw)
        )
        return cursor.fetchone() is not None

    def create_user(self, email, password):
        """Crea un nuevo usuario"""
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        trial_end = datetime.now() + timedelta(days=30)
        self.conn.execute(
            'INSERT INTO users (email, password, trial_end) VALUES (?, ?, ?)',
            (email, hashed_pw, trial_end)
        )
        self.conn.commit()

    def save_automation_task(self, user_email, task_data):
        """Guarda tareas automatizadas"""
        self.conn.execute(
            'INSERT INTO automation_tasks (user_email, task_type, schedule) VALUES (?, ?, ?)',
            (user_email, task_data['type'], task_data['schedule'])
        )
        self.conn.commit()

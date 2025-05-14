import sqlite3
import hashlib
from datetime import datetime, timedelta
# En database.py
import os
def __init__(self):
    db_path = os.path.join(os.path.expanduser("~"), "EnterpriseFlow", "enterpriseflow.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    self.conn = sqlite3.connect(db_path)
    self._create_tables()

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

    # En database.py
   def create_company(self, company_name, admin_email):
       # Crea una empresa y su administrador
       company_id = self.conn.execute('INSERT INTO companies (name) VALUES (?)', (company_name,)).lastrowid
       self.create_user(admin_email, "temp_password", company_id, is_admin=True)
       self.conn.commit()

   def create_user(self, email, password, company_id, is_admin=False):
       # Usuarios vinculados a una empresa
       hashed_pw = hashlib.sha256(password.encode()).hexdigest()
       self.conn.execute('''
           INSERT INTO users (email, password, company_id, is_admin) 
           VALUES (?, ?, ?, ?)
       ''', (email, hashed_pw, company_id, is_admin))

    def save_automation_task(self, user_email, task_data):
        """Guarda tareas automatizadas"""
        self.conn.execute(
            'INSERT INTO automation_tasks (user_email, task_type, schedule) VALUES (?, ?, ?)',
            (user_email, task_data['type'], task_data['schedule'])
        )
        self.conn.commit()

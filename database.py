import sqlite3
import hashlib
from datetime import datetime

class DatabaseManager:
    def _init_(self):
        self.conn = sqlite3.connect('enterpriseflow.db')
        self._create_tables()

    def _create_tables(self):
        tables = [
            '''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE,
                password TEXT
            )''',
            '''CREATE TABLE IF NOT EXISTS automation_tasks (
                id INTEGER PRIMARY KEY,
                user_email TEXT,
                task_type TEXT,
                schedule TEXT
            )''',
            '''CREATE TABLE IF NOT EXISTS recognitions (
                id INTEGER PRIMARY KEY,
                sender TEXT,
                receiver TEXT,
                message TEXT,
                date DATE
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
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.conn.execute(
                'INSERT INTO users (email, password) VALUES (?, ?)',
                (email, hashed_pw)
            )
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            raise e

    def save_automation_task(self, user_email, task_data):
        self.conn.execute(
            'INSERT INTO automation_tasks (user_email, task_type, schedule) VALUES (?, ?, ?)',
            (user_email, task_data['type'], task_data['schedule'])
        )
        self.conn.commit()

    def save_recognition(self, sender, receiver, message):
        self.conn.execute(
            'INSERT INTO recognitions (sender, receiver, message, date) VALUES (?, ?, ?, ?)',
            (sender, receiver, message, datetime.now().date())
        )
        self.conn.commit()

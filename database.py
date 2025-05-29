import sqlite3
import hashlib
from datetime import datetime

class DatabaseManager:
    def __init__(self):
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
            )''',
            '''CREATE TABLE IF NOT EXISTS health_data (
                id INTEGER PRIMARY KEY,
                user_email TEXT UNIQUE,
                dias_sin_incidentes INTEGER,
                horas_sueno_promedio REAL,
                pasos_diarios INTEGER
            )''',  # <- CORRECCIÓN: agrega la coma aquí
            '''CREATE TABLE IF NOT EXISTS personal_goals (
                id INTEGER PRIMARY KEY,
                user_email TEXT,
                goal TEXT,
                created_at DATE DEFAULT CURRENT_DATE
            )'''
        ]
        for table in tables:
            self.conn.execute(table)
        self.conn.commit()

    def save_personal_goal(self, user, goal):
        self.conn.execute(
            'INSERT INTO personal_goals (user_email, goal) VALUES (?, ?)',
            (user, goal)
        )
        self.conn.commit()

    def get_personal_goals(self, user):
        cursor = self.conn.execute(
            'SELECT id, goal FROM personal_goals WHERE user_email=? ORDER BY created_at DESC',
            (user,)
        )
        return cursor.fetchall()

    def edit_personal_goal(self, goal_id, new_goal):
        self.conn.execute(
            'UPDATE personal_goals SET goal=? WHERE id=?',
            (new_goal, goal_id)
        )
        self.conn.commit()

    def delete_personal_goal(self, goal_id):
        self.conn.execute(
            'DELETE FROM personal_goals WHERE id=?',
            (goal_id,)
        )
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

    def get_health_data(self, user):
        """
        Devuelve un dict con los datos de salud si existen, sino None.
        """
        cursor = self.conn.execute(
            'SELECT dias_sin_incidentes, horas_sueno_promedio, pasos_diarios FROM health_data WHERE user_email=?',
            (user,)
        )
        row = cursor.fetchone()
        if row:
            return {
                'dias': row[0],
                'sueno': row[1],
                'pasos': row[2]
            }
        else:
            return None

    def save_health_data(self, user, dias, sueno, pasos):
        """
        Inserta o actualiza los datos de salud del usuario.
        """
        # Verifica si ya existen datos para el usuario
        cursor = self.conn.execute(
            'SELECT id FROM health_data WHERE user_email=?',
            (user,)
        )
        if cursor.fetchone():
            # Actualizar
            self.conn.execute(
                'UPDATE health_data SET dias_sin_incidentes=?, horas_sueno_promedio=?, pasos_diarios=? WHERE user_email=?',
                (dias, sueno, pasos, user)
            )
        else:
            # Insertar
            self.conn.execute(
                'INSERT INTO health_data (user_email, dias_sin_incidentes, horas_sueno_promedio, pasos_diarios) VALUES (?, ?, ?, ?)',
                (user, dias, sueno, pasos)
            )
        self.conn.commit()

    # En database.py dentro de class DatabaseManager:

    def get_medical_record(self, user_email):
        conn = sqlite3.connect("enterprise_flow.db")
        c = conn.cursor()
        c.execute("SELECT patologia, enfermedades, embarazo, observaciones FROM medical_records WHERE user_email=?", (user_email,))
        row = c.fetchone()
        onn.close()
        if row:
            return {"patologia": row[0], "enfermedades": row[1], "embarazo": row[2], "observaciones": row[3]}
        return None

    def save_medical_record(self, user_email, patologia, enfermedades, embarazo, observaciones):
        conn = sqlite3.connect("enterprise_flow.db")
        c = conn.cursor()
        c.execute("SELECT id FROM medical_records WHERE user_email=?", (user_email,))
        if c.fetchone():
            c.execute("""
                UPDATE medical_records 
                SET patologia=?, enfermedades=?, embarazo=?, observaciones=?
                WHERE user_email=?
            """, (patologia, enfermedades, int(embarazo), observaciones, user_email))
        else:
            c.execute("""
                INSERT INTO medical_records (user_email, patologia, enfermedades, embarazo, observaciones)
                VALUES (?, ?, ?, ?, ?)
            """, (user_email, patologia, enfermedades, int(embarazo), observaciones))
        conn.commit()
        conn.close()

    def save_leave_request(self, user_email, tipo, fecha_inicio, fecha_fin, motivo, observaciones):
        conn = sqlite3.connect("enterprise_flow.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO leave_requests (user_email, tipo_permiso, fecha_inicio, fecha_fin, motivo, observaciones)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_email, tipo, fecha_inicio, fecha_fin, motivo, observaciones))
        conn.commit()
        conn.close()

    def get_leave_requests(self, user_email):
        conn = sqlite3.connect("enterprise_flow.db")
        c = conn.cursor()
        c.execute("""
            SELECT tipo_permiso, fecha_inicio, fecha_fin, estado, motivo, observaciones
            FROM leave_requests WHERE user_email=?
            ORDER BY fecha_inicio DESC
        """, (user_email,))
        rows = c.fetchall()
        conn.close()
        return [
            {
                "tipo_permiso": r[0],
                "fecha_inicio": r[1],
                "fecha_fin": r[2],
                "estado": r[3],
                "motivo": r[4],
                "observaciones": r[5]
            }
            for r in rows
        ]

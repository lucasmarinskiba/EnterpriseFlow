import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class DatabaseManager:
    def __init__(self, db_path="enterprise_flow.db"):
        self.db_path = db_path

    def create_user(self, email, password, nombre="", apellido=""):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        hashed = hash_password(password)
        try:
            c.execute(
                "INSERT INTO users (email, password, nombre, apellido) VALUES (?, ?, ?, ?)",
                (email.strip().lower(), hashed, nombre, apellido)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Email {email.strip()} already exists.")
            return False
        except sqlite3.Error as e:
            print(f"SQLite Error: {e}")
            return False
        finally:
            conn.close()

    def verify_user(self, email, password):
        if not email.strip() or not password.strip():
            return False
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            hashed = hash_password(password)
            c.execute(
                "SELECT * FROM users WHERE email=? AND password=?",
                (email.strip().lower(), hashed)
            )
            user = c.fetchone()
            conn.close()
            return user is not None
        except sqlite3.Error as e:
            print(f"SQLite Error: {e}")
            return False
        
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

    def ensure_tables(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            nombre TEXT,
            apellido TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        conn.close()

   
    
    def save_personal_goal(self, user, goal):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            'INSERT INTO personal_goals (user_email, goal_text) VALUES (?, ?)',
            (user, goal)
        )
        conn.commit()
        conn.close()

    def get_user(self, email):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email.strip(),))
        user = c.fetchone()
        conn.close()
        return user

    def get_personal_goals(self, user):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
           'SELECT id, goal_text FROM personal_goals WHERE user_email=? ORDER BY created_at DESC',
            (user,)
        )
        rows = c.fetchall()
        conn.close()
        return rows

    def edit_personal_goal(self, goal_id, new_goal):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            'UPDATE personal_goals SET goal_text=? WHERE id=?',
            (new_goal, goal_id)
        )
        conn.commit()
        conn.close()

    def delete_personal_goal(self, goal_id):
        self.conn.execute(
            'DELETE FROM personal_goals WHERE id=?',
            (goal_id,)
        )
        self.conn.commit()
    

    def save_automation_task(self, user_email, task_data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO automation_tasks (user_email, type, schedule, responsible, notification_method)
            VALUES (?, ?, ?, ?, ?)
        """, (user_email, task_data['type'], task_data['schedule'], task_data['responsible'], task_data['notification_method']))
        conn.commit()
        conn.close()

    def get_automation_tasks(self, user_email):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT type, schedule, responsible, notification_method, status, created_at FROM automation_tasks WHERE user_email=? ORDER BY created_at DESC", (user_email,))
        rows = c.fetchall()
        conn.close()
        return [{"Tipo": r[0], "Horario": r[1], "Responsable": r[2], "Notificación": r[3], "Estado": r[4], "Creado": r[5]} for r in rows]

    def log_automation_task_creation(self, user_email, task_type):
        # Puedes enlazar esto con automation_task_logs si quieres
        pass  # Simple placeholder, puedes expandir
    
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
        conn.close()
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

    def save_invoice(self, user_email, client_name, client_email, client_address, subtotal, iva, total, invoice_number, pdf_bytes):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO invoices (user_email, client_name, client_email, client_address, subtotal, iva, total, invoice_number, pdf_file)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_email, client_name, client_email, client_address, subtotal, iva, total, invoice_number, pdf_bytes))
        conn.commit()
        conn.close()

    def log_invoice_action(self, invoice_number, user_email, action):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id FROM invoices WHERE invoice_number=?", (invoice_number,))
        inv = c.fetchone()
        if inv:
            c.execute("INSERT INTO invoice_logs (invoice_id, user_email, action) VALUES (?, ?, ?)", (inv[0], user_email, action))
            conn.commit()
        conn.close()

    def update_invoice_status(self, invoice_number, status):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE invoices SET status=?, sent_at=CURRENT_TIMESTAMP WHERE invoice_number=?", (status, invoice_number))
        conn.commit()
        conn.close()

    def get_invoices_by_user(self, user_email):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT invoice_number, client_name, total, status, created_at FROM invoices WHERE user_email=? ORDER BY created_at DESC", (user_email,))
        rows = c.fetchall()
        conn.close()
        return [{"Número": r[0], "Cliente": r[1], "Total": r[2], "Estado": r[3], "Fecha": r[4]} for r in rows]

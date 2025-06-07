PRAGMA table_info(users);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    nombre TEXT,
    apellido TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    puntos INTEGER DEFAULT 0,
    nivel INTEGER DEFAULT 1,
    insignias INTEGER DEFAULT 0,
    tareas_completadas INTEGER DEFAULT 0,
    dias_constancia INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_email)
);

CREATE TABLE personal_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    goal_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed BOOLEAN DEFAULT 0
);

CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL UNIQUE,
    nombre TEXT,
    apellido TEXT,
    fecha_nacimiento DATE,
    documento TEXT
);

CREATE TABLE medical_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    patologia TEXT,
    enfermedades TEXT,
    embarazo BOOLEAN DEFAULT 0,
    observaciones TEXT,
    FOREIGN KEY(user_email) REFERENCES employees(user_email)
);

CREATE TABLE sick_leaves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    fecha_inicio DATE,
    fecha_fin DATE,
    motivo TEXT,
    observaciones TEXT,
    FOREIGN KEY(user_email) REFERENCES employees(user_email)
);

CREATE TABLE leave_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    tipo_permiso TEXT, -- "vacaciones", "enfermedad", "otro"
    fecha_inicio DATE,
    fecha_fin DATE,
    estado TEXT DEFAULT 'pendiente', -- "pendiente", "aprobado", "rechazado"
    motivo TEXT,
    observaciones TEXT,
    FOREIGN KEY(user_email) REFERENCES employees(user_email)
);

CREATE TABLE IF NOT EXISTS medical_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    patologia TEXT,
    enfermedades TEXT,
    embarazo BOOLEAN DEFAULT 0,
    observaciones TEXT,
    FOREIGN KEY(user_email) REFERENCES employees(user_email)
);

CREATE TABLE IF NOT EXISTS leave_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    tipo_permiso TEXT,
    fecha_inicio DATE,
    fecha_fin DATE,
    estado TEXT DEFAULT 'pendiente',
    motivo TEXT,
    observaciones TEXT,
    FOREIGN KEY(user_email) REFERENCES employees(user_email)
);

CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL UNIQUE,
    nombre TEXT,
    apellido TEXT,
    fecha_nacimiento DATE,
    documento TEXT
);

ALTER TABLE medical_records ADD COLUMN apellido TEXT;
ALTER TABLE medical_records ADD COLUMN nombre TEXT;
ALTER TABLE medical_records ADD COLUMN file_path TEXT;

CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    nombre TEXT,
    apellido TEXT,
    fecha_nacimiento DATE,
    documento TEXT
);

CREATE TABLE IF NOT EXISTS medical_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    file_name TEXT,
    file_path TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(employee_id) REFERENCES employees(id)
);

CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    client_name TEXT,
    client_email TEXT,
    client_address TEXT,
    subtotal REAL,
    iva REAL,
    total REAL,
    invoice_number TEXT,
    pdf_file BLOB,
    status TEXT DEFAULT 'pendiente', -- pendiente, enviada, pagada, vencida
    sent_at TIMESTAMP,
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS invoice_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    user_email TEXT,
    action TEXT,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(invoice_id) REFERENCES invoices(id)
);

CREATE TABLE IF NOT EXISTS automation_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    type TEXT,
    schedule TEXT,
    responsible TEXT,
    notification_method TEXT,
    status TEXT DEFAULT 'pendiente',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS automation_task_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    action TEXT,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES automation_tasks(id)
);

CREATE TABLE IF NOT EXISTS advanced_automations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    name TEXT,
    script TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rollback_of INTEGER,
    status TEXT DEFAULT 'activo'
);

CREATE TABLE IF NOT EXISTS advanced_automation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    automation_id INTEGER,
    user_email TEXT,
    status TEXT,
    output TEXT,
    error TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(automation_id) REFERENCES advanced_automations(id)
);

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


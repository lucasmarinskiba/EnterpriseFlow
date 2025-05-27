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

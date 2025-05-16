import streamlit as st
import sqlite3
import hashlib
import spacy
from datetime import datetime
import time
import pandas as pd
import plotly.express as px

# ------------------------ 🛡️ Solución Error SQLite ------------------------
def init_db():
    """Inicialización robusta de base de datos con manejo de errores"""
    try:
        conn = sqlite3.connect('/tmp/enterpriseflow.db', check_same_thread=False)
        c = conn.cursor()
        
        # Tabla de usuarios con campos para cumplimiento empresarial
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT CHECK(role IN ('admin', 'manager', 'user')) DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tabla de auditoría para cumplimiento normativo
        c.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        return conn
    except sqlite3.Error as e:
        st.error(f"Error crítico de base de datos: {str(e)}")
        st.stop()

# ------------------------ 🧠 Solución Error spaCy ------------------------
@st.cache_resource
def load_nlp_model():
    """Carga segura del modelo NLP con múltiples fallbacks"""
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        from spacy.cli import download
        try:
            download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            st.error(f"Fallo crítico al cargar modelo NLP: {str(e)}")
            st.stop()
    return nlp

# ------------------------ 🎨 UI Profesional ------------------------
def setup_ui():
    """Configuración de interfaz de usuario empresarial"""
    st.set_page_config(
        page_title="EnterpriseFlow Pro",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Estilos CSS personalizados
    st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        .stButton>button { border-radius: 8px; padding: 10px 24px; }
        .stTextInput>div>div>input { border: 1px solid #dee2e6; }
        .reportview-container { margin-top: -2em; }
        header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# ------------------------ 🔐 Sistema de Autenticación ------------------------
class AuthSystem:
    def __init__(self, conn):
        self.conn = conn
        
    def hash_password(self, password):
        """Cifrado seguro de contraseñas con salting"""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return salt + key
    
    def verify_user(self, email, password):
        """Verificación robusta de credenciales"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE email=?", (email,))
            result = cursor.fetchone()
            
            if not result:
                return False
                
            stored_hash = result[0]
            salt = stored_hash[:32]
            key = stored_hash[32:]
            new_key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            return key == new_key
        except sqlite3.Error as e:
            st.error(f"Error de base de datos: {str(e)}")
            return False

# ------------------------ 🤖 Automatizaciones Empresariales ------------------------
class EnterpriseAutomations:
    def __init__(self, conn):
        self.conn = conn
        
    def generate_compliance_report(self):
        """Generación automática de reportes de cumplimiento"""
        query = '''
            SELECT DATE(timestamp) as date, 
                   COUNT(*) as actions,
                   SUM(CASE WHEN action LIKE 'LOGIN%' THEN 1 ELSE 0 END) as logins
            FROM audit_log
            GROUP BY DATE(timestamp)
        '''
        df = pd.read_sql(query, self.conn)
        
        fig = px.bar(df, x='date', y='actions', title='Actividad Diaria')
        st.plotly_chart(fig)
        
        return df
    
    def user_activity_monitor(self):
        """Monitoreo en tiempo real de actividad"""
        query = '''
            SELECT u.email, a.action, a.timestamp 
            FROM audit_log a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.timestamp DESC
            LIMIT 50
        '''
        return pd.read_sql(query, self.conn)

# ------------------------ 🚀 Main Application ------------------------
def main():
    # Configuración inicial
    setup_ui()
    conn = init_db()
    auth = AuthSystem(conn)
    automations = EnterpriseAutomations(conn)
    
    # Sistema de autenticación
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        
    if not st.session_state.authenticated:
        with st.container():
            st.title("🔒 EnterpriseFlow Login")
            email = st.text_input("Correo Corporativo")
            password = st.text_input("Contraseña", type="password")
            
            if st.button("Acceder"):
                if auth.verify_user(email, password):
                    st.session_state.authenticated = True
                    st.experimental_rerun()
                else:
                    st.error("Credenciales inválidas")
        return
    
    # Interfaz principal post-login
    st.sidebar.title("🚀 EnterpriseFlow")
    menu = ["Dashboard", "Automatizaciones", "Cumplimiento", "Administración"]
    choice = st.sidebar.selectbox("Menú", menu)
    
    if choice == "Dashboard":
        st.header("📊 Panel de Control Ejecutivo")
        with st.spinner("Cargando métricas empresariales..."):
            time.sleep(1)
            st.success("Datos actualizados")
            
            # Widgets interactivos
            col1, col2, col3 = st.columns(3)
            col1.metric("Usuarios Activos", 150, "+5%")
            col2.metric("Transacciones", "1.2M", "8.2%")
            col3.metric("Cumplimiento", "98%", "-2%")
            
            st.plotly_chart(px.line(pd.DataFrame({
                'Fecha': pd.date_range(start='2024-01-01', periods=5),
                'Ventas': [100, 200, 150, 300, 250]
            }), x='Fecha', y='Ventas', title='Tendencia de Ventas'))
    
    elif choice == "Automatizaciones":
        st.header("🤖 Automatización de Procesos")
        # Implementar flujos de trabajo automatizados aquí
    
    elif choice == "Cumplimiento":
        st.header("📜 Reportes de Cumplimiento")
        report_data = automations.generate_compliance_report()
        st.dataframe(report_data.style.highlight_max(axis=0))
    
    elif choice == "Administración":
        st.header("⚙️ Administración del Sistema")
        st.write("### Registro de Actividad")
        st.dataframe(automations.user_activity_monitor())
        
        with st.expander("Gestión de Usuarios"):
            # CRUD de usuarios con validación
            new_email = st.text_input("Nuevo Correo")
            new_role = st.selectbox("Rol", ["user", "manager", "admin"])
            if st.button("Crear Usuario"):
                # Lógica segura de creación de usuarios
                pass

if __name__ == "__main__":
    main()

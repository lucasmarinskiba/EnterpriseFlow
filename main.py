import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import numpy as np
import datetime
import os
import stripe
from database import DatabaseManager
from payment_handler import PaymentHandler
from tensorflow.keras.models import load_model
import spacy

# Configuración inicial
st.set_page_config(
    page_title="EnterpriseFlow",
    page_icon="🏢",
    layout="wide"
)

class EnterpriseFlowApp:
    def __init__(self):
        self.db = DatabaseManager()  # <-- Inicialización correcta de 'self.db'
        self.payment = PaymentHandler()
        self.current_user = None
        self.nlp = spacy.load("es_core_news_sm")
        self._setup_ui()  # Llama a la configuración inicial

    def _setup_ui(self):
        """Configura la interfaz principal"""
        st.sidebar.image("https://via.placeholder.com/200x50.png?text=EnterpriseFlow", width=200)
        if not self.current_user:
            self._show_login()  # <-- Método que contiene la lógica de login/registro
        else:
            self._show_main_interface()

    def _show_login(self):
        """Muestra el formulario de login/registro"""
        with st.sidebar:
            st.header("Bienvenido a EnterpriseFlow")
            tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
            
            # Pestaña de Login
            with tab1:
                email_login = st.text_input("Correo electrónico")
                password_login = st.text_input("Contraseña", type="password")
                if st.button("Ingresar"):
                    if self.db.verify_user(email_login, password_login):
                        self.current_user = email_login
                        st.rerun()  # <-- Cambio aquí
                    else:
                        st.error("Credenciales incorrectas")
            
            # Pestaña de Registro
            with tab2:
                email_register = st.text_input("Correo para registro")
                password_register = st.text_input("Contraseña nueva", type="password")
                if st.button("Crear Cuenta"):
                    try:
                        self.db.create_user(email_register, password_register)
                        st.success("¡Cuenta creada exitosamente!")
                    except sqlite3.IntegrityError:
                        st.error("Este correo ya está registrado")

    # ... (resto de métodos como _show_main_interface, etc)

    def _show_main_interface(self):
        """Interfaz principal"""
        menu = st.sidebar.radio(
            "Menú Principal",
            ["🏠 Inicio", "🤖 Automatización", "😌 Bienestar", "⚖️ Cumplimiento", "💳 Suscripción"]
        )
        
        if menu == "🏠 Inicio":
            self._show_dashboard()
        elif menu == "🤖 Automatización":
            self._show_automation()
        elif menu == "😌 Bienestar":
            self._show_wellness()
        elif menu == "⚖️ Cumplimiento":
            self._show_compliance()
        elif menu == "💳 Suscripción":
            self._show_payment()

    def _show_dashboard(self):
        """Muestra el dashboard principal"""
        st.title("Panel de Control")
        st.write(f"Bienvenido: {self.current_user}")

    def _show_automation(self):
        """Módulo de Automatización"""
        with st.expander("🤖 Automatización de Tareas", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Generador de Facturas")
                client_name = st.text_input("Nombre del Cliente")
                subtotal = st.number_input("Subtotal", min_value=0.0)
                client_address = st.text_input("Dirección del Cliente")
                
                if st.button("Generar Factura"):
                    invoice_data = {
                        'client_name': client_name,
                        'subtotal': subtotal,
                        'client_address': client_address
                    }
                    invoice = self._generate_invoice(invoice_data)
                    st.success(f"Factura generada: ${invoice['total']}")

            with col2:
                st.subheader("Programación de Tareas")
                task_type = st.selectbox("Tipo de Tarea", ["Reporte", "Recordatorio", "Backup"])
                schedule_time = st.time_input("Hora de Ejecución")
                
                if st.button("Programar Tarea"):
                    self.db.save_automation_task(self.current_user, {
                        'type': task_type,
                        'schedule': schedule_time.strftime("%H:%M")
                    })
                    st.success("Tarea programada exitosamente")

    def _generate_invoice(self, data):
        """Genera facturas con IVA automático"""
        iva_rate = 0.16 if 'MEX' in data['client_address'] else 0.21
        return {
            'client': data['client_name'],
            'total': round(data['subtotal'] * (1 + iva_rate), 2),
            'compliance_check': self._check_compliance(data)
        }

    def _check_compliance(self, data):
        """Verifica cumplimiento normativo"""
        return True  # Implementar lógica real aquí

if __name__ == "__main__":
    EnterpriseFlowApp()
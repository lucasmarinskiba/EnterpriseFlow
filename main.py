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
        self.db = DatabaseManager()
        self.payment = PaymentHandler()
        self.nlp = spacy.load("es_core_news_sm")
        
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
            
        self._setup_ui()

    def _setup_ui(self):
        st.sidebar.image("https://via.placeholder.com/200x50.png?text=EnterpriseFlow", width=200)
        if not st.session_state.logged_in:
            self._show_login()
        else:
            self._show_main_interface()

    def _show_login(self):
        with st.sidebar:
            st.header("Bienvenido a EnterpriseFlow")
            tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
            
            with tab1:
                email_login = st.text_input("Correo electrónico")
                password_login = st.text_input("Contraseña", type="password")
                if st.button("Ingresar"):
                    if self.db.verify_user(email_login, password_login):
                        st.session_state.logged_in = True
                        st.session_state.current_user = email_login
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas")
            
            with tab2:
                email_register = st.text_input("Correo para registro")
                password_register = st.text_input("Contraseña nueva", type="password")
                if st.button("Crear Cuenta"):
                    try:
                        self.db.create_user(email_register, password_register)
                        st.success("¡Cuenta creada exitosamente!")
                    except sqlite3.IntegrityError:
                        st.error("Este correo ya está registrado")

    def _show_main_interface(self):
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
        if menu == "💳 Suscripción":
            self._show_payment()

    def _show_dashboard(self):
        st.title("Panel de Control")
        st.write(f"Bienvenido: {st.session_state.current_user}")

    def _show_automation(self):
     with st.expander("🤖 Automatización de Tareas", expanded=True):
        col1, col2, col3 = st.columns(3)  # Nueva columna agregada
        
        # Columna 1 Existente (Facturas)
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

        # Columna 2 Existente (Tareas)
        with col2:
            st.subheader("Programación de Tareas")
            task_type = st.selectbox("Tipo de Tarea", ["Reporte", "Recordatorio", "Backup"])
            schedule_time = st.time_input("Hora de Ejecución")
            
            if st.button("Programar Tarea"):
                self.db.save_automation_task(st.session_state.current_user, {
                    'type': task_type,
                    'schedule': schedule_time.strftime("%H:%M")
                })
                st.success("Tarea programada exitosamente")

        # Nueva Columna 3 (Automatizaciones Adicionales)
        with col3:
            st.subheader("Nuevas Automatizaciones")
            
            # Automatización 1: Envío Masivo de Emails
            with st.container(border=True):
                st.markdown("**📧 Email Masivo**")
                email_subject = st.text_input("Asunto del Email")
                email_template = st.text_area("Plantilla HTML")
                if st.button("Programar Envío"):
                    self.db.save_automation_task(st.session_state.current_user, {
                        'type': 'email_masivo',
                        'subject': email_subject,
                        'template': email_template
                    })
                    st.success("Envío programado!")
            
            # Automatización 2: Actualización de CRM
            with st.container(border=True):
                st.markdown("**🔄 Sync CRM**")
                crm_action = st.selectbox("Acción", ["Actualizar clientes", "Importar leads"])
                sync_frequency = st.selectbox("Frecuencia", ["Diario", "Semanal", "Mensual"])
                if st.button("Configurar Sync"):
                    self.db.save_automation_task(st.session_state.current_user, {
                        'type': 'crm_sync',
                        'action': crm_action,
                        'frequency': sync_frequency
                    })
                    st.success("Sincronización configurada")

        # Nueva Sección Debajo (Escalable)
        with st.container():
            st.subheader("Automatizaciones Avanzadas")
            adv_col1, adv_col2 = st.columns(2)
            
            with adv_col1:
                # Automatización 3: Análisis Predictivo
                st.markdown("**🔮 Análisis Predictivo**")
                model_type = st.selectbox("Modelo", ["Ventas", "Retención", "Inventario"])
                if st.button("Ejecutar Modelo"):
                    self._run_predictive_model(model_type)
                    st.success("Modelo ejecutado")
            
            with adv_col2:
                # Automatización 4: Integración API
                st.markdown("**⚙️ Integración Externa**")
                api_endpoint = st.text_input("URL API")
                if st.button("Conectar"):
                    self._test_api_connection(api_endpoint)
                    st.success("Conexión exitosa")
    
    #limite
    def _generate_invoice(self, data):
        iva_rate = 0.16 if 'MEX' in data['client_address'] else 0.21
        return {
            'client': data['client_name'],
            'total': round(data['subtotal'] * (1 + iva_rate), 2),
            'compliance_check': self._check_compliance(data)
        }

    def _check_compliance(self, data):
        return True

    def _show_wellness(self):
        with st.expander("😌 Bienestar del Equipo", expanded=True):
            st.subheader("Predicción de Burnout")
            hours_worked = st.slider("Horas trabajadas esta semana", 0, 100, 40)
            
            if st.button("Calcular Riesgo"):
                prediction = self._predict_burnout(np.array([[hours_worked, 0, 0, 0, 0]]))
                st.metric("Riesgo de Burnout", f"{prediction}%")

            st.subheader("Sistema de Reconocimiento")
            colleague = st.text_input("Nombre del Colega")
            recognition = st.text_area("Mensaje de Reconocimiento")
            
            if st.button("Enviar 🏆"):
                self.db.save_recognition(st.session_state.current_user, colleague, recognition)
                st.success("Reconocimiento enviado!")

    def _predict_burnout(self, input_data):
        try:
            return min(100, int(input_data[0][0] * 1.5))
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return 0

    def _show_compliance(self):
        """Módulo de Cumplimiento Normativo"""
        with st.expander("⚖️ Auditoría Normativa", expanded=True):
            uploaded_file = st.file_uploader("Subir Documento", type=["txt", "docx", "pdf"])
            
            if uploaded_file:
                text = ""
                try:
                    if uploaded_file.type == "text/plain":
                        text = uploaded_file.getvalue().decode()
                    elif uploaded_file.type == "application/pdf":
                        import PyPDF2
                        reader = PyPDF2.PdfReader(uploaded_file)
                        text = "\n".join([page.extract_text() for page in reader.pages])
                    else:
                        from docx import Document
                        doc = Document(uploaded_file)
                        text = "\n".join([para.text for para in doc.paragraphs])
                except Exception as e:
                    st.error(f"Error al leer el archivo: {str(e)}")
                    return
                
                audit_result = self._audit_document(text)
                st.write("**Resultados de Auditoría:**")
                st.json(audit_result)

    def _audit_document(self, text):
        """Analiza documentos para detectar normativas"""
        doc = self.nlp(text)
        resultados = {
            'GDPR': any(token.text.lower() in ('datos personales', 'consentimiento') for token in doc),
            'SOX': any(token.text.lower() in ('control interno', 'auditoría financiera') for token in doc),
            'ISO27001': any(token.text.lower() in ('seguridad de la información', 'riesgos') for token in doc)
        }
        return resultados

    def _show_payment(self):
        """Interfaz de suscripciones corregida"""
        st.header("📈 Planes EnterpriseFlow")
        
        cols = st.columns(3)
        
        with cols[0]:
            st.subheader("Básico")
            st.markdown("""
                - 10 usuarios
                - Soporte básico
                - Reportes estándar
                **Precio: $99/mes**
            """)
            if st.button("Elegir Básico", key="basico"):
                self._handle_subscription('basico')  # Key en español

        with cols[1]:
            st.subheader("Premium")
            st.markdown("""
                - 50 usuarios
                - Soporte prioritario
                - Reportes avanzados
                **Precio: $299/mes**
            """)
            if st.button("Elegir Premium", key="premium"):
                self._handle_subscription('premium')

        with cols[2]:
            st.subheader("Enterprise")
            st.markdown("""
                - Usuarios ilimitados
                - Soporte 24/7
                - Personalización
                **Precio: $999/mes**
            """)
            if st.button("Contactar Ventas", key="enterprise"):
                st.info("contacto@enterpriseflow.com")

    def _handle_subscription(self, plan: str):
        """Manejo de suscripciones corregido"""
        try:
            if not st.session_state.current_user:
                raise ValueError("Debe iniciar sesión primero")
            
            subscription_data = self.payment.create_subscription(
                customer_email=st.session_state.current_user,
                price_key=plan
            )
            
            if subscription_data.get('client_secret'):
                st.session_state.subscription = subscription_data
                self._show_payment_confirmation()
            else:
                st.error("Error al crear la suscripción")
        
        except Exception as e:
            st.error(f"Error en suscripción: {str(e)}")

    def _show_payment_confirmation(self):
        """Interfaz para completar el pago"""
        with st.form("payment-form"):
            st.write("Complete los datos de pago")
            
            # Campos seguros para tarjeta (mejor usar Stripe Elements)
            card_number = st.text_input("Número de tarjeta")
            expiry = st.text_input("MM/AA")
            cvc = st.text_input("CVC")
            
            if st.form_submit_button("Confirmar Pago"):
                try:
                    # Lógica de confirmación de pago
                    # Deberías implementar Stripe Elements aquí
                    st.success("Pago procesado exitosamente!")
                    st.session_state.subscription = None  # Resetear estado
                except Exception as e:
                    st.error(f"Error en pago: {str(e)}")
    
if __name__ == "__main__":
    EnterpriseFlowApp()

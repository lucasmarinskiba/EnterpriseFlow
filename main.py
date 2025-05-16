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
from fpdf import FPDF  # Corregido: Usar fpdf2 pero el import sigue siendo from fpdf
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

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
        if 'subscription' not in st.session_state:
            st.session_state.subscription = None
            
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
        elif menu == "💳 Suscripción":
            self._show_payment()

    def _show_dashboard(self):
        st.title("Panel de Control")
        st.write(f"Bienvenido: {st.session_state.current_user}")
        if st.session_state.subscription:
            st.subheader("Estado de Suscripción")
            st.write(f"Plan: {st.session_state.subscription.get('plan_type', 'Básico')}")
            st.write(f"Estado: {st.session_state.subscription.get('status', 'Activa')}")

    def _show_automation(self):
        with st.expander("🤖 Automatización de Tareas", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            # Columna 1 - Generador de Facturas
            with col1:
                st.subheader("Generador de Facturas")
                client_name = st.text_input("Nombre del Cliente")
                client_email = st.text_input("Email del Cliente")
                subtotal = st.number_input("Subtotal", min_value=0.0)
                client_address = st.text_input("Dirección del Cliente")
                
                with st.expander("Opciones Avanzadas"):
                    logo = st.file_uploader("Logo (PNG/JPG)", type=["png", "jpg"])
                    due_date = st.date_input("Fecha Vencimiento")
                    payment_method = st.selectbox("Método Pago", ["Transferencia", "Tarjeta", "Efectivo"])
                
                if st.button("Generar Factura"):
                    try:
                        invoice_data = {
                            'client_name': client_name,
                            'client_email': client_email,
                            'subtotal': subtotal,
                            'client_address': client_address,
                            'due_date': due_date.strftime("%d/%m/%Y"),
                            'payment_method': payment_method,
                            'logo': logo.read() if logo else None
                        }
                        
                        invoice = self._generate_invoice(invoice_data)
                        pdf_path = self._generate_pdf(invoice)
                        
                        st.success(f"Factura generada: ${invoice['total']}")
                        with open(pdf_path, "rb") as f:
                            st.download_button("Descargar Factura", f, file_name=f"factura_{client_name}.pdf")
                        
                        if client_email:
                            if st.button("📤 Enviar por Email"):
                                self._send_invoice_email(client_email, pdf_path)
                                st.success("Email enviado exitosamente!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

            # Columna 2 - Programación de Tareas
            with col2:
                st.subheader("Programación de Tareas")
                task_type = st.selectbox("Tipo de Tarea", ["Reporte", "Recordatorio", "Backup"])
                schedule_time = st.time_input("Hora Ejecución")
                
                if st.button("Programar Tarea"):
                    self.db.save_automation_task(st.session_state.current_user, {
                        'type': task_type,
                        'schedule': schedule_time.strftime("%H:%M")
                    })
                    st.success("Tarea programada exitosamente")

            # Columna 3 - Automatizaciones Adicionales
            with col3:
                st.subheader("Nuevas Automatizaciones")
                
                with st.container(border=True):
                    st.markdown("**📧 Email Masivo**")
                    email_subject = st.text_input("Asunto Email")
                    email_template = st.text_area("Plantilla HTML")
                    if st.button("Programar Envío Masivo"):
                        self.db.save_automation_task(st.session_state.current_user, {
                            'type': 'email_masivo',
                            'subject': email_subject,
                            'template': email_template
                        })
                        st.success("Envío programado!")
                
                with st.container(border=True):
                    st.markdown("**🔄 Sync CRM**")
                    crm_action = st.selectbox("Acción CRM", ["Actualizar clientes", "Importar leads"])
                    sync_frequency = st.selectbox("Frecuencia Sync", ["Diario", "Semanal", "Mensual"])
                    if st.button("Configurar Sincronización"):
                        self.db.save_automation_task(st.session_state.current_user, {
                            'type': 'crm_sync',
                            'action': crm_action,
                            'frequency': sync_frequency
                        })
                        st.success("Sincronización configurada")

            # Sección Avanzada
            with st.container():
                st.subheader("Automatizaciones Avanzadas")
                adv_col1, adv_col2 = st.columns(2)
                
                with adv_col1:
                    st.markdown("**🔮 Análisis Predictivo**")
                    model_type = st.selectbox("Modelo Predictivo", ["Ventas", "Retención", "Inventario"])
                    if st.button("Ejecutar Análisis"):
                        self._run_predictive_model(model_type)
                        st.success("Análisis completado")
                
                with adv_col2:
                    st.markdown("**⚙️ Integración API**")
                    api_endpoint = st.text_input("Endpoint API")
                    if st.button("Testear Conexión"):
                        self._test_api_connection(api_endpoint)
                        st.success("Conexión exitosa")

    def _generate_invoice(self, data):
        try:
            iva_rate = 0.16 if 'MEX' in data['client_address'] else 0.21
            total = round(data['subtotal'] * (1 + iva_rate), 2)
            return {
                'total': total,
                'invoice_number': f"INV-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}",
                'details': data,
                'compliance_check': self._check_compliance(data)
            }
        except Exception as e:
            raise ValueError(f"Error generando factura: {str(e)}")

    def _generate_pdf(self, invoice):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Encabezado (Corregido el cierre de llave en f-string)
            pdf.cell(200, 10, txt=f"Factura #{invoice['invoice_number']}", ln=1, align='C')
            pdf.cell(200, 10, txt=f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=1)
            
            # Detalles Cliente
            pdf.cell(200, 10, txt=f"Cliente: {invoice['details']['client_name']}", ln=1)
            pdf.cell(200, 10, txt=f"Dirección: {invoice['details']['client_address']}", ln=1)
            
            # Detalles Pago
            pdf.cell(200, 10, txt=f"Subtotal: ${invoice['details']['subtotal']}", ln=1)
            pdf.cell(200, 10, txt=f"IVA ({'16%' if 'MEX' in invoice['details']['client_address'] else '21%'}): ${round(invoice['details']['subtotal'] * 0.16 if 'MEX' in invoice['details']['client_address'] else invoice['details']['subtotal'] * 0.21, 2)}", ln=1)
            pdf.cell(200, 10, txt=f"Total: ${invoice['total']}", ln=1)
            
            pdf_path = f"/tmp/{invoice['invoice_number']}.pdf"
            pdf.output(pdf_path)
            return pdf_path
        except Exception as e:
            raise RuntimeError(f"Error generando PDF: {str(e)}")

    def _send_invoice_email(self, email, pdf_path):
        try:
            msg = MIMEMultipart()
            msg['From'] = os.getenv('EMAIL_FROM')
            msg['To'] = email
            msg['Subject'] = "Su factura de EnterpriseFlow"
            
            body = "Adjunto encontrará su factura generada automáticamente."
            msg.attach(MIMEText(body, 'plain'))
            
            with open(pdf_path, "rb") as attachment:
                part = MIMEApplication(attachment.read(), Name="factura.pdf")
                part['Content-Disposition'] = f'attachment; filename="factura.pdf"'
                msg.attach(part)
            
            server = smtplib.SMTP(os.getenv('SMTP_SERVER'), 587)
            server.starttls()
            server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASS'))
            server.sendmail(msg['From'], email, msg.as_string())
            server.quit()
        except Exception as e:
            raise RuntimeError(f"Error enviando email: {str(e)}")

    def _show_payment(self):
        st.header("📈 Planes de Suscripción")
        cols = st.columns(3)
        
        with cols[0]:
            st.subheader("Básico")
            st.markdown("""
                - 10 usuarios
                - Soporte básico
                - Reportes estándar
                **$99/mes**
            """)
            if st.button("Elegir Básico", key="basic_sub"):
                self._handle_subscription('basico')

        with cols[1]:
            st.subheader("Premium")
            st.markdown("""
                - 50 usuarios
                - Soporte prioritario
                - Reportes avanzados
                **$299/mes**
            """)
            if st.button("Elegir Premium", key="premium_sub"):
                self._handle_subscription('premium')

        with cols[2]:
            st.subheader("Enterprise")
            st.markdown("""
                - Usuarios ilimitados
                - Soporte 24/7
                - Personalización total
                **$999/mes**
            """)
            if st.button("Contactar Ventas", key="enterprise_sub"):
                st.info("contacto@enterpriseflow.com")

    def _handle_subscription(self, plan):
        try:
            if not st.session_state.current_user:
                raise ValueError("Debe iniciar sesión primero")
            
            subscription_data = self.payment.create_subscription(
                customer_email=st.session_state.current_user,
                price_key=plan
            )
            
            st.session_state.subscription = {
                'plan_type': plan.capitalize(),
                'status': subscription_data.get('status', 'active'),
                'details': subscription_data
            }
            
            st.success(f"Suscripción {plan.capitalize()} activada!")
            if subscription_data.get('client_secret'):
                self._show_payment_confirmation(subscription_data['client_secret'])
        except Exception as e:
            st.error(f"Error en suscripción: {str(e)}")

    def _show_payment_confirmation(self, client_secret):
        with st.form("payment_confirm_form"):
            st.write("Complete los datos de pago")
            card_number = st.text_input("Número de Tarjeta")
            exp_date = st.text_input("MM/AA")
            cvc = st.text_input("CVC")
            
            if st.form_submit_button("Confirmar Pago"):
                try:
                    stripe.PaymentIntent.confirm(
                        client_secret,
                        payment_method={
                            'type': 'card',
                            'card': {
                                'number': card_number,
                                'exp_month': exp_date.split('/')[0],
                                'exp_year': exp_date.split('/')[1],
                                'cvc': cvc
                            }
                        }
                    )
                    st.success("Pago procesado exitosamente!")
                except stripe.error.StripeError as e:
                    st.error(f"Error en pago: {e.user_message}")

    # ... (Métodos restantes _show_wellness, _show_compliance, etc.)

if __name__ == "__main__":
    EnterpriseFlowApp()

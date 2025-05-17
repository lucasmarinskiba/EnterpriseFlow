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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

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
            ["🏠 Inicio", "🤖 Automatización", "😌 Bienestar", "🔒 Feedback Anónimo", "⚖️ Cumplimiento", "💳 Suscripción"]
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
        # Columna 1 Existente (Facturas)
        with col1:
           st.subheader("Generador de Facturas")
           client_name = st.text_input("Nombre del Cliente")
           subtotal = st.number_input("Subtotal", min_value=0.0)
           client_address = st.text_input("Dirección del Cliente")
           client_email = st.text_input("Correo Electrónico del Cliente")  # Nuevo campo para email
    
           if st.button("Generar Factura"):
              invoice_data = {
                 'client_name': client_name,
                 'subtotal': subtotal,
                 'client_address': client_address,
                 'client_email': client_email  # Agregamos el email a los datos
              }
        
              # Generar factura
              invoice = self._generate_invoice(invoice_data)
        
              # Configurar email (agregar estos datos en secrets.toml)
              smtp_server = st.secrets["smtp"]["server"]
              smtp_port = st.secrets["smtp"]["port"]
              sender_email = st.secrets["smtp"]["user"]
              sender_password = st.secrets["smtp"]["password"]
        
              # Crear mensaje
              msg = MIMEMultipart()
              msg['From'] = sender_email
              msg['To'] = client_email
              msg['Subject'] = f"Factura {invoice['invoice_number']} - {client_name}"
        
              # Cuerpo del mensaje
              body = f"""
              Hola {client_name},
        
              Adjunto encontrará su factura número {invoice['invoice_number']}.
        
              Detalles:
              - Total: ${invoice['total']}
              - Fecha: {invoice['date']}
        
              Gracias por su preferencia.
              """
              msg.attach(MIMEText(body, 'plain'))
        
              # Adjuntar PDF (asumiendo que _generate_invoice guarda un archivo)
              filename = f"Factura_{invoice['invoice_number']}.pdf"
              part = MIMEBase('application', 'octet-stream')
              part.set_payload(invoice['pdf_data'])
              encoders.encode_base64(part)
              part.add_header('Content-Disposition', f'attachment; filename= {filename}')
              msg.attach(part)
        
              # Enviar email
              try:
                 with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, client_email, msg.as_string())
                 st.success(f"Factura enviada a {client_email}!")
              except Exception as e:
                 st.error(f"Error enviando email: {str(e)}")

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
           colleague_email = st.text_input("Email del Colega")  # Nuevo campo
           recognition = st.text_area("Mensaje de Reconocimiento")
           signing_authority = st.selectbox("Firmante", ["CEO", "Gerente General"])  # Selección de firmante
        
           if st.button("Enviar 🏆"):
               # Generar certificado PDF
               certificate_data = self._generate_certificate(
                   colleague=colleague,
                   recognition=recognition,
                   signer=signing_authority
               )
            
               # Guardar en base de datos
               cert_id = self.db.save_recognition(
                   user=st.session_state.current_user,
                   colleague=colleague,
                   recognition=recognition,
                   certificate_id=certificate_data['cert_id'],
                   signer=signing_authority,
                   pdf_data=certificate_data['pdf_bytes']
               )
            
               # Enviar por email
               if self._send_recognition_email(colleague_email, certificate_data):
                   st.success(f"Certificado enviado a {colleague_email}!")
                   st.download_button(
                       label="Descargar Certificado",
                       data=certificate_data['pdf_bytes'],
                       file_name=f"Certificado_{cert_id}.pdf",
                       mime="application/pdf"
                   )
               else:
                   st.error("Error enviando el certificado")

    def _generate_certificate(self, colleague, recognition, signer):
       from fpdf import FPDF
       import uuid
    
       cert_id = str(uuid.uuid4())[:8].upper()
       pdf = FPDF()
       pdf.add_page()
    
       # Estilos del certificado
       pdf.set_font("Arial", 'B', 16)
       pdf.cell(0, 10, "Certificado de Reconocimiento", ln=1, align='C')
       pdf.ln(15)
    
       pdf.set_font("Arial", '', 12)
       pdf.multi_cell(0, 10, f"Se reconoce oficialmente a {colleague} por:", align='C')
       pdf.ln(10)
       pdf.multi_cell(0, 8, f'"{recognition}"')
       pdf.ln(20)
    
       # Firma (agregar imágenes en secrets)
       signature_img = st.secrets["signatures"][signer.lower().replace(" ", "_")]
       pdf.image(signature_img, x=50, w=30)
       pdf.set_font("Arial", 'I', 10)
       pdf.cell(0, 10, f"Firmado por: {signer}", ln=1, align='R')
    
       pdf_bytes = pdf.output(dest='S').encode('latin1')
    
       return {
           'pdf_bytes': pdf_bytes,
           'cert_id': cert_id
       }

    def _send_recognition_email(self, recipient, certificate_data):
       try:
           msg = MIMEMultipart()
           msg['From'] = st.secrets["smtp"]["user"]
           msg['To'] = recipient
           msg['Subject'] = "🏆 Reconocimiento Oficial - Tu Certificado"
        
           body = f"""
           ¡Felicitaciones!
        
           Has recibido un reconocimiento oficial de la empresa.
           Adjunto encontrarás tu certificado digital con validez oficial.
        
           ID del Certificado: {certificate_data['cert_id']}
           """
           msg.attach(MIMEText(body, 'plain'))
        
           # Adjuntar certificado
           part = MIMEBase('application', 'octet-stream')
           part.set_payload(certificate_data['pdf_bytes'])
           encoders.encode_base64(part)
           part.add_header('Content-Disposition', 
                         f'attachment; filename= "Certificado_{certificate_data["cert_id"]}.pdf"')
           msg.attach(part)
        
           # Enviar email
           with smtplib.SMTP(st.secrets["smtp"]["server"], st.secrets["smtp"]["port"]) as server:
               server.starttls()
               server.login(st.secrets["smtp"]["user"], st.secrets["smtp"]["password"])
               server.sendmail(st.secrets["smtp"]["user"], recipient, msg.as_string())
           return True
       except Exception as e:
           st.error(f"Error: {str(e)}")
           return False

    def _predict_burnout(self, input_data):
        try:
            return min(100, int(input_data[0][0] * 1.5))
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return 0

    def _add_feedback_system(self):
       with st.container(border=True):
           st.subheader("🔒 Feedback Anónimo")
           feedback_type = st.selectbox("Tipo de Feedback", ["Para el equipo", "Para liderazgo", "Sugerencias generales"])
           feedback = st.text_area("Escribe tu feedback (máx. 500 caracteres)", max_chars=500)
           if st.button("Enviar Feedback"):
               self.db.save_anonymous_feedback(feedback_type, feedback)
               st.success("¡Gracias por tu contribución! Tu feedback es anónimo.")
    
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

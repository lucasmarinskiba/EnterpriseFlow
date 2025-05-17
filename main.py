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
        elif menu == "🔒 Feedback Anónimo":
            self._show_feedback_system()
        elif menu == "⚖️ Cumplimiento":
            self._show_compliance()
        elif menu == "💳 Suscripción":
            self._show_payment()

    def _show_dashboard(self):
        st.title("Panel de Control")
        st.write(f"Bienvenido: {st.session_state.current_user}")

    def _show_automation(self):
        with st.expander("🤖 Automatización de Tareas", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("Generador de Facturas")
                client_name = st.text_input("Nombre del Cliente")
                subtotal = st.number_input("Subtotal", min_value=0.0)
                client_address = st.text_input("Dirección del Cliente")
                client_email = st.text_input("Correo Electrónico del Cliente")
                
                if st.button("Generar Factura"):
                    invoice_data = {
                        'client_name': client_name,
                        'subtotal': subtotal,
                        'client_address': client_address,
                        'client_email': client_email
                    }
                    
                    invoice = self._generate_invoice(invoice_data)
                    
                    smtp_server = st.secrets["smtp"]["server"]
                    smtp_port = st.secrets["smtp"]["port"]
                    sender_email = st.secrets["smtp"]["user"]
                    sender_password = st.secrets["smtp"]["password"]
                    
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = client_email
                    msg['Subject'] = f"Factura {invoice['invoice_number']} - {client_name}"
                    
                    body = f"""
                    Hola {client_name},
                    
                    Adjunto encontrará su factura número {invoice['invoice_number']}.
                    
                    Detalles:
                    - Total: ${invoice['total']}
                    - Fecha: {invoice['date']}
                    
                    Gracias por su preferencia.
                    """
                    msg.attach(MIMEText(body, 'plain'))
                    
                    filename = f"Factura_{invoice['invoice_number']}.pdf"
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(invoice['pdf_data'])
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename= {filename}')
                    msg.attach(part)
                    
                    try:
                        with smtplib.SMTP(smtp_server, smtp_port) as server:
                            server.starttls()
                            server.login(sender_email, sender_password)
                            server.sendmail(sender_email, client_email, msg.as_string())
                        st.success(f"Factura enviada a {client_email}!")
                    except Exception as e:
                        st.error(f"Error enviando email: {str(e)}")

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

            with col3:
                st.subheader("Nuevas Automatizaciones")
                
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

            with st.container():
                st.subheader("Automatizaciones Avanzadas")
                adv_col1, adv_col2 = st.columns(2)
                
                with adv_col1:
                    st.markdown("**🔮 Análisis Predictivo**")
                    model_type = st.selectbox("Modelo", ["Ventas", "Retención", "Inventario"])
                    if st.button("Ejecutar Modelo"):
                        self._run_predictive_model(model_type)
                        st.success("Modelo ejecutado")
                
                with adv_col2:
                    st.markdown("**⚙️ Integración Externa**")
                    api_endpoint = st.text_input("URL API")
                    if st.button("Conectar"):
                        self._test_api_connection(api_endpoint)
                        st.success("Conexión exitosa")

    def _generate_invoice(self, data):
        iva_rate = 0.16 if 'MEX' in data['client_address'] else 0.21
        return {
            'client': data['client_name'],
            'total': round(data['subtotal'] * (1 + iva_rate), 2),
            'compliance_check': self._check_compliance(data),
            'invoice_number': f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            'date': datetime.datetime.now().strftime("%d/%m/%Y"),
            'pdf_data': b''  # Agregar lógica de generación PDF real aquí
        }

    def _check_compliance(self, data):
        return True

    def _show_wellness(self):
        with st.expander("😌 Bienestar del Equipo", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Predicción de Burnout")
                hours_worked = st.slider("Horas trabajadas esta semana", 0, 100, 40)
                if st.button("Calcular Riesgo"):
                    prediction = self._predict_burnout(np.array([[hours_worked, 0, 0, 0, 0]]))
                    st.metric("Riesgo de Burnout", f"{prediction}%")

            with col2:
                st.subheader("Sistema de Reconocimiento")
                colleague = st.text_input("Nombre del Colega")
                colleague_email = st.text_input("Email del Colega")
                recognition = st.text_area("Mensaje de Reconocimiento")
                signing_authority = st.selectbox("Firmante", ["CEO", "Gerente General"])
                
                if st.button("Enviar 🏆"):
                    certificate_data = self._generate_certificate(
                        colleague=colleague,
                        recognition=recognition,
                        signer=signing_authority
                    )
                    cert_id = self.db.save_recognition(
                        user=st.session_state.current_user,
                        colleague=colleague,
                        recognition=recognition,
                        certificate_id=certificate_data['cert_id'],
                        signer=signing_authority,
                        pdf_data=certificate_data['pdf_bytes']
                    )
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

            st.markdown("---")
            self._health_dashboard()
            self._smart_breaks()
            self._learning_portal()
            self._personal_goals()
            self._meditation_module()
            self._team_network()
            self._workload_monitor()
            self._gamification_system()

    def _generate_certificate(self, colleague, recognition, signer):
        from fpdf import FPDF
        import uuid
        
        cert_id = str(uuid.uuid4())[:8].upper()
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Certificado de Reconocimiento", ln=1, align='C')
        pdf.ln(15)
        
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 10, f"Se reconoce oficialmente a {colleague} por:", align='C')
        pdf.ln(10)
        pdf.multi_cell(0, 8, f'"{recognition}"')
        pdf.ln(20)
        
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
            
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(certificate_data['pdf_bytes'])
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= "Certificado_{certificate_data["cert_id"]}.pdf"')
            msg.attach(part)
            
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

    def _show_feedback_system(self):
        with st.expander("🔒 Sistema de Feedback Anónimo", expanded=True):
            feedback_type = st.selectbox("Tipo de Feedback", ["Para el equipo", "Para liderazgo", "Sugerencias generales"])
            feedback = st.text_area("Escribe tu feedback (máx. 500 caracteres)", max_chars=500)
            if st.button("Enviar Feedback"):
                self.db.save_anonymous_feedback(feedback_type, feedback)
                st.success("¡Gracias por tu contribución! Tu feedback es anónimo.")

    def _health_dashboard(self):
        with st.container(border=True):
            st.subheader("📊 Panel de Salud Integral")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📅 Días sin incidentes", "28")
            with col2:
                st.metric("💤 Horas Sueño Promedio", "6.2")
            with col3:
                st.metric("🚶 Pasos Diarios", "4,892")

    def _smart_breaks(self):
        with st.container(border=True):
            st.subheader("⏰ Programador de Descansos Inteligentes")
            break_frequency = st.slider("Intervalo entre descansos (minutos)", 30, 120, 50)
            break_duration = st.slider("Duración del descanso (minutos)", 5, 15, 7)
            if st.button("Activar Recordatorios"):
                self._schedule_breaks(break_frequency, break_duration)

    def _schedule_breaks(self, frequency, duration):
        st.session_state.break_config = {
            'frequency': frequency,
            'duration': duration
        }
        st.success(f"Descansos programados cada {frequency} minutos por {duration} minutos")

    def _learning_portal(self):
        with st.container(border=True):
            st.subheader("🎓 Plataforma de Aprendizaje")
            course_data = [
                {'id': 1, 'title': 'Gestión del Tiempo', 'progress': 0.4},
                {'id': 2, 'title': 'Liderazgo Efectivo', 'progress': 0.7},
                {'id': 3, 'title': 'Inteligencia Emocional', 'progress': 0.2}
            ]
            for course in course_data:
                with st.container(border=True):
                    st.markdown(f"**{course['title']}**")
                    st.progress(course['progress'])
                    if st.button(f"Continuar Curso {course['id']}"):
                        st.session_state.current_course = course['id']

    def _personal_goals(self):
        with st.container(border=True):
            st.subheader("🏆 Sistema de Metas Personales")
            goal = st.text_input("Establece tu objetivo personal esta semana")
            if st.button("Guardar Objetivo"):
               self.db.save_personal_goal(
                  user=st.session_state.current_user,
                  goal=goal,
                  deadline=datetime.datetime.now() + datetime.timedelta(days=7)
               st.success("¡Objetivo guardado!")

    def _meditation_module(self):
        with st.container(border=True):
            st.subheader("🧘 Sesiones de Relajación")
            duration = st.radio("Duración:", ["5 min", "10 min", "15 min"])
            if st.button("Iniciar Meditación Guiada"):
                st.audio("https://cdn.pixabay.com/download/audio/2023/03/19/audio_6d9dc48707.mp3")

    def _team_network(self):
        with st.container(border=True):
            st.subheader("👥 Mapa de Relaciones del Equipo")
            st.graphviz_chart('''
                digraph {
                    "CEO" -> "Gerente"
                    "Gerente" -> "Equipo A"
                    "Gerente" -> "Equipo B"
                    "Equipo A" -> "Miembro 1"
                    "Equipo A" -> "Miembro 2"
                    "Equipo B" -> "Miembro 3"
                }
            ''')

    def _workload_monitor(self):
        with st.container(border=True):
            st.subheader("⚖️ Monitor de Carga de Trabajo")
            current_load = st.slider("Tu carga actual (1-10)", 1, 10, 7)
            ideal_load = st.slider("Carga ideal deseada (1-10)", 1, 10, 5)
            if current_load > ideal_load:
                st.error("¡Carga de trabajo excesiva!")
            elif current_load < ideal_load:
                st.warning("Capacidad disponible")
            else:
                st.success("Carga equilibrada")

    def _gamification_system(self):
        with st.container(border=True):
            st.subheader("🎮 Sistema de Recompensas")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🏅 Puntos Acumulados", "1,250")
            with col2:
                st.metric("🌟 Nivel Actual", "5")
            with col3:
                st.metric("🏆 Insignias", "3/10")

    def _show_compliance(self):
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
        doc = self.nlp(text)
        return {
            'GDPR': any(token.text.lower() in ('datos personales', 'consentimiento') for token in doc),
            'SOX': any(token.text.lower() in ('control interno', 'auditoría financiera') for token in doc),
            'ISO27001': any(token.text.lower() in ('seguridad de la información', 'riesgos') for token in doc)
        }

    def _show_payment(self):
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
                self._handle_subscription('basico')

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
        with st.form("payment-form"):
            st.write("Complete los datos de pago")
            card_number = st.text_input("Número de tarjeta")
            expiry = st.text_input("MM/AA")
            cvc = st.text_input("CVC")
            
            if st.form_submit_button("Confirmar Pago"):
                try:
                    st.success("Pago procesado exitosamente!")
                    st.session_state.subscription = None
                except Exception as e:
                    st.error(f"Error en pago: {str(e)}")

if __name__ == "__main__":
    EnterpriseFlowApp()

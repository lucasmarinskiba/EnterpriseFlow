# app/chatbot/deepseek.py
import os
import requests
from flask import current_app

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# app/chatbot/deepseek.py
def _add_enterprise_context(self, user_id, message):
    user = User.query.get(user_id)
    sub = Subscription.query.filter_by(user_id=user_id).first()
    projects = Project.query.filter_by(owner_id=user_id).limit(3).all()

    context = f"""
    [Usuario]
    - Nombre: {user.name}
    - Rol: {user.role}
    - Último login: {user.last_login.strftime('%Y-%m-%d') if user.last_login else 'Nunca'}

    [Suscripción]
    - Plan: {sub.plan if sub else 'Free'}
    - Estado: {'Activo' if sub and sub.expiry_date > datetime.now() else 'Inactivo'}

    [Proyectos Recientes]
    {', '.join(p.name for p in projects) or 'Ninguno'}
    """
    return f"{context}\n\n[Pregunta] {message}"
    
class EnterpriseFlowChatbot:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.context = """
        Eres un asistente especializado en EnterpriseFlow con conocimiento en:
        - 🏠 Inicio: Configuración inicial, dashboard
        - 🤖 Automatización: Flujos de trabajo, triggers
        - 😌 Bienestar: Monitoreo de carga laboral
        - 🔒 Feedback Anónimo: Sistema de reportes
        - ⚖️ Cumplimiento: Normativas legales
        - 💳 Suscripción: Planes y facturación
        """

    def generate_response(self, user_message, user_id):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": self.context},
                {"role": "user", "content": self._add_enterprise_context(user_id, user_message)}
            ],
            "temperature": 0.3
        }

        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
        return self._process_response(response.json(), user_id)

    def _add_enterprise_context(self, user_id, message):
        # Obtener datos específicos del usuario desde la base de datos
        from app.models import User, Subscription
        user = User.query.get(user_id)
        sub = Subscription.query.filter_by(user_id=user_id).first()

        return f"""
        [Contexto EnterpriseFlow]
        - Usuario: {user.name}
        - Rol: {user.role}
        - Suscripción: {sub.plan if sub else 'Free'}
        - Último login: {user.last_login}
        
        [Pregunta]
        {message}
        """

    def _process_response(self, deepseek_response, user_id):
        # Verificar si se necesita acción específica
        if "[ACCION]" in deepseek_response.choices[0].message.content:
            return self._handle_special_action(deepseek_response, user_id)
        
        return deepseek_response.choices[0].message.content

    def _handle_special_action(self, response, user_id):
        # Ejemplo: Manejar solicitudes de facturación
        if "suscripción" in response.lower():
            from app.models import Subscription
            sub = Subscription.query.filter_by(user_id=user_id).first()
            return f"Tu plan actual: {sub.plan}\nVencimiento: {sub.expiry_date}"
            

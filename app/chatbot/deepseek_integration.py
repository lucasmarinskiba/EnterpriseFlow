# app/chatbot/deepseek_integration.py
import os
import requests
from flask import current_app
from app.models import User, Project, Subscription  # Asegúrate de que estos modelos existan

class EnterpriseFlowChatbot:
    def __init__(self):
        self.api_key = current_app.config['DEEPSEEK_API_KEY']
        self.base_context = """
        Eres el asistente principal de EnterpriseFlow. Funcionalidades clave:
        1. 🏠 Inicio: Dashboard con resumen de proyectos
        2. 🤖 Automatización: Configuración de triggers y acciones
        3. 😌 Bienestar: Monitoreo de carga laboral
        4. 🔒 Feedback: Sistema de reportes anónimos
        5. ⚖️ Cumplimiento: Auditorías y normativas
        6. 💳 Suscripción: Gestión de planes de pago
        """

    def get_user_context(self, user_id):
        user = User.query.get(user_id)
        subscription = Subscription.query.filter_by(user_id=user_id).first()
        projects = Project.query.filter_by(owner_id=user_id).limit(3).all()
        
        return f"""
        [Usuario]
        - Nombre: {user.name}
        - Rol: {user.role}
        - Proyectos activos: {len(projects)}
        - Plan: {subscription.plan if subscription else 'Free'}
        """

    def generate_response(self, user_input, user_id):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system", 
                    "content": f"{self.base_context}\n{self.get_user_context(user_id)}"
                },
                {
                    "role": "user", 
                    "content": user_input
                }
            ],
            "temperature": 0.5
        }

        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload
        )

        return response.json()['choices'][0]['message']['content']

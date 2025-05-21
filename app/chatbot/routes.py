# app/chatbot/routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .deepseek import EnterpriseFlowChatbot

chatbot_bp = Blueprint('chatbot', __name__)
bot = EnterpriseFlowChatbot()

@chatbot_bp.post('/api/chat')
@jwt_required()
def handle_chat():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({"error": "Mensaje requerido"}), 400

    try:
        response = bot.generate_response(data['message'], user_id)
        return jsonify({"reply": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chatbot_bp.get('/api/features')
def get_features():
    return jsonify({
        "funcionalidades": [
            {
                "icono": "🏠",
                "nombre": "Inicio",
                "endpoint": "/api/home",
                "descripción": "Configuración inicial y dashboard principal"
            },
            {
                "icono": "🤖",
                "nombre": "Automatización",
                "endpoint": "/api/automation",
                "descripción": "Crea flujos de trabajo automatizados"
            },
            # ... Agregar todas las funcionalidades
        ]
    })

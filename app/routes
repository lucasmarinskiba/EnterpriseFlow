# app/routes.py (Modificar este archivo existente)
from flask import render_template
+ from app.chatbot import chatbot_bp
+ from app.chatbot.deepseek_integration import EnterpriseFlowChatbot

# Añadir al inicio del archivo
+ app.register_blueprint(chatbot_bp, url_prefix='/chatbot')

# Añadir esta ruta
@app.route('/')
def index():
    return render_template('index.html')  # Asegurar que incluya chatbot_embed.html

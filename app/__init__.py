# app/__init__.py
from app.chatbot.routes import chatbot_bp

app.register_blueprint(chatbot_bp, url_prefix='/chatbot')

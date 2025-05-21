# app/__init__.py
from app.chatbot.routes import chatbot_bp

# app/__init__.py
from flask import Flask
from dotenv import load_dotenv

load_dotenv()  # Carga variables del .env

app = Flask(__name__)
app.config["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY")

app.register_blueprint(chatbot_bp, url_prefix='/chatbot')

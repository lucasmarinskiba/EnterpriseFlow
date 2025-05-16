#!/bin/bash
# 1. Configuración inicial de Git
git init
git add .
git config --global user.email "tu@email.com"
git config --global user.name "Tu Nombre"
git commit -m "Fix: Indentación y dependencias"
git remote add origin https://github.com/lucasmarinskiba/EnterpriseFlow.git
git push -u origin main

# 2. Instalación de dependencias y validación
pip install -r requirements.txt
python -m spacy download es_core_news_sm
pip install flake8  # Instalar linter

# 3. Verificación de código
echo "=== Verificando errores de indentación con flake8 ==="
flake8 main.py --show-source --statistics

# 4. Generación del ejecutable (opcional)
pip install pyinstaller
pyinstaller --onefile --windowed --clean main.py

# 5. Despliegue en Streamlit Cloud
echo "=== Ejecutando la aplicación ==="
streamlit run main.py

flake8 main.py database.py

#para pagos
pip install pydantic

# Primera capa: Paquetes esenciales
pip install streamlit pandas numpy

# Segunda capa: Procesamiento de documentos
pip install python-docx PyPDF2 pdfplumber

# Tercera capa: NLP
pip install spacy==3.7.4 thinc==8.2.4
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.0/en_core_web_sm-3.7.0-py3-none-any.whl

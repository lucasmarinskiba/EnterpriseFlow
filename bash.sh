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
pip install fpdf2 spacy pandas streamlit
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

mkdir -p firmas
convert -size 200x100 xc:white -font Arial -pointsize 24 -draw "text 30,50 'CEO'" firmas/ceo_signature.png

# Crea la carpeta para las firmas
mkdir -p firmas
touch firmas/ceo_signature.png

# Añade estos archivos (Reemplázalos con tus firmas reales)
touch firmas/ceo_signature.png
touch firmas/gerente_signature.png

mkdir -p firmas
convert -size 200x100 xc:white -font Arial -pointsize 24 -draw "text 30,50 'CEO'" firmas/ceo_signature.png
git add firmas/ceo_signature.png
git commit -m "Agrega firma digital CEO"
git push

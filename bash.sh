git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/lucasmarinskiba/EnterpriseFlow.git
git push -u origin main
# Con PyInstaller (ejecuta en tu terminal):
pip install pyinstaller
pyinstaller --onefile --windowed main.py
streamlit run main.py
python -m spacy download es_core_news_sm

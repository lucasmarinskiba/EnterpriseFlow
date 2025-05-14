import PyInstaller.__main__
PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name=EnterpriseFlow',
    '--icon=app_icon.ico'
])

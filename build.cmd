IF NOT EXIST venv (
    python -m venv venv
    venv\Scripts\pip.exe install -r requirements.txt
)
IF NOT EXIST venv\Scripts\pyinstaller.exe (
    venv\Scripts\pip.exe install -I pyinstaller
)
venv\Scripts\pyinstaller.exe main.py --noconsole -y --onefile
move dist\main.exe main.exe
rmdir dist

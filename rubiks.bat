@echo off
cd /d "%~dp0"

if exist ".installed" goto run_rubiks

echo =======================================
echo Checking and installing requirements...
echo =======================================
pip install -r requirements.txt
playwright install
echo Installation Complete > .installed
cls

:run_rubiks
python main.py
pause

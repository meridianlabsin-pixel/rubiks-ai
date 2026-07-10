@echo off
cd /d "%~dp0"
echo =======================================
echo Checking and installing requirements...
echo =======================================
pip install -r requirements.txt
playwright install
cls
python main.py
pause

@echo off
echo [1/3] Kiem tra Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] May nay chua cai Python. Hay cai Python 3.10 tro len!
    pause
    exit
)

echo [2/3] Dang tao moi truong ao venv...
if not exist "venv" (
    python -m venv venv
)

echo [3/3] Dang cai dat thu vien tu requirements.txt...
call venv\Scripts\activate
pip install -r requirements.txt

echo ------------------------------------------------
echo [SUCCESS] Dang khoi chay Delta Robot Control...
python main.py
pause
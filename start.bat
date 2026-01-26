@echo off
setlocal enabledelayedexpansion

echo ========================================
echo     Expense AI Assistant - Starting
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [!] Virtual environment not found
    echo Creating virtual environment...
    python -m venv venv
    
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo [OK] Virtual environment found
    call venv\Scripts\activate.bat
)

REM Check if database exists
if not exist "data\database\expenses.db" (
    echo [!] Database not found
    set /p init="Would you like to initialize the database with sample data? (y/n): "
    if /i "!init!"=="y" (
        python scripts\init_db.py
    ) else (
        python -c "from backend.models.database import init_db; init_db()"
    )
)

echo.
echo ========================================
echo     Starting services...
echo ========================================
echo.

REM Start backend
echo [*] Starting Backend (FastAPI)...
start "Backend API" cmd /k "venv\Scripts\activate.bat && python backend\api\main.py"

REM Wait for 3 seconds
timeout /t 3 /nobreak > nul

REM Start frontend
echo [*] Starting Frontend (Streamlit)...
start "Frontend" cmd /k "venv\Scripts\activate.bat && streamlit run frontend\streamlit\app.py"

echo.
echo [OK] Services started successfully!
echo.
echo URLs:
echo    - Frontend: http://localhost:8501
echo    - Backend API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo.
echo Close the command windows to stop the services.
echo.

pause

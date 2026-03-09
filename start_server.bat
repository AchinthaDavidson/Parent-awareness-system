@echo off
REM Startup script for Parent Dashboard Backend

echo ========================================
echo   Parent Dashboard Backend Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [INFO] Starting Parent Dashboard API server...
echo [INFO] Server will run on http://localhost:8000
echo [INFO] API docs available at http://localhost:8000/docs
echo.
echo [NOTE] Make sure serviceAccountKey.json exists in project root
echo.

REM Run the server
python main.py

pause

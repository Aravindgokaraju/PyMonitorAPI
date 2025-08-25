@echo off
echo Starting Django Production Server on Windows...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Waitress is installed
python -c "import waitress" >nul 2>&1
if errorlevel 1 (
    echo Waitress is not installed. Installing now...
    pip install waitress
)

REM Check if dotenv is installed
python -c "import dotenv" >nul 2>&1
if errorlevel 1 (
    echo python-dotenv is not installed. Installing now...
    pip install python-dotenv
)

REM Check if .env.production exists
if not exist ".env.production_local" (
    echo Error: .env.production file not found!
    echo Please create .env.production file with your settings.
    pause
    exit /b 1
)

REM Run the production script
python run_production.py

REM Keep the window open after execution
echo.
echo Server stopped.
pause
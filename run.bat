@echo off
REM DatasetDoctor - One-Command Run Script for Windows CMD

echo 🏥 DatasetDoctor - Starting...
echo =================================
echo.

REM Check Python
where python >nul 2>nul
if errorlevel 1 (
    echo ❌ Error: Python 3 is required
    exit /b 1
)

REM Create venv if it doesn't exist
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
)

REM Activate venv
call .venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies (this may take a few minutes)...

python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ Failed to upgrade pip.
    exit /b 1
)

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements from requirements.txt.
    exit /b 1
)

echo ✅ Dependencies installed successfully.


REM Create directories
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs
if not exist "traces" mkdir traces
if not exist "uploads\.gitkeep" type nul > uploads\.gitkeep
if not exist "outputs\.gitkeep" type nul > outputs\.gitkeep

REM Create .env if it doesn't exist
if not exist ".env" (
    echo GOOGLE_API_KEY= > .env
    echo ⚠️  Note: GOOGLE_API_KEY not set. AI features will be disabled.
)

echo.
echo 🚀 Starting DatasetDoctor Web UI...
echo   Open: http://localhost:5000
echo   Press Ctrl+C to stop
echo.

python ui\app.py

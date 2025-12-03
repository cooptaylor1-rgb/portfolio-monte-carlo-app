@echo off
REM Setup script for Salem Portfolio Analysis (Windows)
REM Run this script to set up both backend and frontend

echo 🚀 Setting up Salem Portfolio Analysis...
echo.

echo 📋 Checking prerequisites...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is not installed. Please install Python 3.12+
    exit /b 1
)

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+
    exit /b 1
)

echo ✅ Prerequisites check passed
echo.

REM Backend setup
echo 🔧 Setting up backend...
cd backend

echo   Creating virtual environment...
python -m venv venv

echo   Activating virtual environment...
call venv\Scripts\activate.bat

echo   Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Backend setup complete
echo.

cd ..

REM Frontend setup
echo 🎨 Setting up frontend...
cd frontend

echo   Installing Node dependencies...
call npm install

echo ✅ Frontend setup complete
echo.

cd ..

echo.
echo ✨ Setup complete!
echo.
echo To start the application:
echo.
echo 1. Start the backend (Terminal 1):
echo    cd backend
echo    venv\Scripts\activate
echo    python main.py
echo.
echo 2. Start the frontend (Terminal 2):
echo    cd frontend
echo    npm run dev
echo.
echo 3. Open your browser to http://localhost:3000
echo.
echo 📚 View API docs at http://localhost:8000/api/docs
echo.

pause

@echo off
echo ========================================
echo    AUDEXA - Mental Health AI Assistant
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python is installed
echo.

REM Check if we're in the correct directory
if not exist "app.py" (
    echo ERROR: app.py not found in current directory
    echo Please run this script from the ListenAI-main directory
    pause
    exit /b 1
)

echo ✅ Found app.py
echo.

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  WARNING: .env file not found
    echo Please create .env file with your API keys
    echo See env_template.txt for reference
    echo.
)

REM Check if required packages are installed
echo 🔍 Checking required packages...
python -c "import flask, twilio, telegram, gtts" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        pause
        exit /b 1
    )
    echo ✅ Packages installed successfully
) else (
    echo ✅ All required packages are installed
)

echo.
echo 🚀 Starting AUDEXA with WhatsApp and Telegram integration...
echo.
echo 📱 WhatsApp Integration: ACTIVE
echo 🤖 Telegram Integration: ACTIVE
echo 🎤 Voice Features: ACTIVE
echo 🌍 Multilingual Support: ACTIVE
echo.
echo 🌐 Web Interface: http://127.0.0.1:5000
echo 📱 WhatsApp Webhook: http://127.0.0.1:5000/chatbot
echo 🤖 Telegram Webhook: http://127.0.0.1:5000/telegram
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the application
python app.py

echo.
echo AUDEXA has been stopped.
pause

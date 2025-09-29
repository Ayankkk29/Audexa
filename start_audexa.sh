#!/bin/bash

echo "========================================"
echo "   AUDEXA - Mental Health AI Assistant"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ ERROR: Python is not installed"
        echo "Please install Python 3.8+ and try again"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✅ Python is installed: $($PYTHON_CMD --version)"
echo

# Check if we're in the correct directory
if [ ! -f "app.py" ]; then
    echo "❌ ERROR: app.py not found in current directory"
    echo "Please run this script from the ListenAI-main directory"
    exit 1
fi

echo "✅ Found app.py"
echo

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found"
    echo "Please create .env file with your API keys"
    echo "See env_template.txt for reference"
    echo
fi

# Check if required packages are installed
echo "🔍 Checking required packages..."
if ! $PYTHON_CMD -c "import flask, twilio, telegram, gtts" 2>/dev/null; then
    echo "📦 Installing required packages..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: Failed to install packages"
        exit 1
    fi
    echo "✅ Packages installed successfully"
else
    echo "✅ All required packages are installed"
fi

echo
echo "🚀 Starting AUDEXA with WhatsApp and Telegram integration..."
echo
echo "📱 WhatsApp Integration: ACTIVE"
echo "🤖 Telegram Integration: ACTIVE"
echo "🎤 Voice Features: ACTIVE"
echo "🌍 Multilingual Support: ACTIVE"
echo
echo "🌐 Web Interface: http://127.0.0.1:5000"
echo "📱 WhatsApp Webhook: http://127.0.0.1:5000/chatbot"
echo "🤖 Telegram Webhook: http://127.0.0.1:5000/telegram"
echo
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo

# Start the application
$PYTHON_CMD app.py

echo
echo "AUDEXA has been stopped."

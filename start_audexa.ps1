# AUDEXA Startup Script with Telegram Integration
# PowerShell Version

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AUDEXA - Mental Health AI Assistant" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python is installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if we're in the correct directory
if (-not (Test-Path "app.py")) {
    Write-Host "❌ ERROR: app.py not found in current directory" -ForegroundColor Red
    Write-Host "Please run this script from the ListenAI-main directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Found app.py" -ForegroundColor Green
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  WARNING: .env file not found" -ForegroundColor Yellow
    Write-Host "Please create .env file with your API keys" -ForegroundColor Yellow
    Write-Host "See env_template.txt for reference" -ForegroundColor Yellow
    Write-Host ""
}

# Check if required packages are installed
Write-Host "🔍 Checking required packages..." -ForegroundColor Blue
try {
    python -c "import flask, twilio, telegram, gtts" 2>$null
    Write-Host "✅ All required packages are installed" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing required packages..." -ForegroundColor Blue
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: Failed to install packages" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Packages installed successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 Starting AUDEXA with Telegram integration..." -ForegroundColor Green
Write-Host ""
Write-Host "🤖 Telegram Integration: ACTIVE" -ForegroundColor Green
Write-Host "🎤 Voice Features: ACTIVE" -ForegroundColor Green
Write-Host "🌍 Multilingual Support: ACTIVE" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Web Interface: http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "📱 Messaging Interface: http://127.0.0.1:5000/messaging" -ForegroundColor Cyan
Write-Host "🤖 Telegram Webhook: http://127.0.0.1:5000/telegram" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start the application
try {
    python app.py
} catch {
    Write-Host ""
    Write-Host "❌ Error starting AUDEXA: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "AUDEXA has been stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"

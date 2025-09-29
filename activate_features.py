#!/usr/bin/env python3
"""
AUDEXA Feature Activation Script
Activates WhatsApp and Telegram integrations with comprehensive testing
"""

import os
import sys
import subprocess
import time
import requests
from dotenv import load_dotenv

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("   🚀 AUDEXA - Mental Health AI Assistant")
    print("   📱 WhatsApp & Telegram Integration Activator")
    print("=" * 60)
    print()

def check_environment():
    """Check environment setup"""
    print("🔍 Checking environment setup...")
    
    # Load environment variables
    load_dotenv()
    
    required_vars = {
        'GEMINI_KEY': 'Google Gemini API key',
        'TWILIO_ACCOUNT_SID': 'Twilio Account SID',
        'TWILIO_AUTH_TOKEN': 'Twilio Auth Token',
        'TWILIO_PHONE_NUMBER': 'Twilio Phone Number',
        'TELEGRAM_BOT_TOKEN': 'Telegram Bot Token'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  - {var} ({description})")
        else:
            print(f"  ✅ {var}: Configured")
    
    if missing_vars:
        print(f"\n❌ Missing environment variables:")
        for var in missing_vars:
            print(var)
        print("\nPlease add these to your .env file and try again.")
        return False
    
    print("✅ All environment variables configured!")
    return True

def check_dependencies():
    """Check and install dependencies"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'flask', 'twilio', 'python-telegram-bot', 'gtts', 
        'google-generativeai', 'pydub', 'openai-whisper'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}: Installed")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}: Missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please install manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

def test_integrations():
    """Test WhatsApp and Telegram integrations"""
    print("\n🧪 Testing integrations...")
    
    try:
        from backend.messaging import messaging_bot
        
        # Test WhatsApp
        print("  📱 Testing WhatsApp integration...")
        test_data = {
            'WaId': 'test_user_123',
            'Body': 'Hello, I need help with anxiety',
            'From': 'whatsapp:+1234567890',
            'To': 'whatsapp:+0987654321'
        }
        
        response = messaging_bot.process_whatsapp_webhook(test_data)
        if response and '<?xml' in response:
            print("    ✅ WhatsApp webhook processing: OK")
        else:
            print("    ❌ WhatsApp webhook processing: FAILED")
            return False
        
        # Test Telegram
        print("  🤖 Testing Telegram integration...")
        telegram_app = messaging_bot.setup_telegram_bot()
        if telegram_app:
            print("    ✅ Telegram bot setup: OK")
        else:
            print("    ❌ Telegram bot setup: FAILED")
            return False
        
        # Test AI Response
        print("  🧠 Testing AI response generation...")
        response_data = messaging_bot.get_ai_response(
            "I'm feeling anxious about my job interview",
            "test_user_123",
            "test"
        )
        if response_data and response_data.get('text'):
            print("    ✅ AI response generation: OK")
        else:
            print("    ❌ AI response generation: FAILED")
            return False
        
        # Test Voice Generation
        print("  🎤 Testing voice generation...")
        voice_file = messaging_bot.generate_voice_response(
            "Hello, this is a test voice message",
            "en"
        )
        if voice_file and os.path.exists(voice_file):
            print("    ✅ Voice generation: OK")
            os.unlink(voice_file)  # Clean up
        else:
            print("    ❌ Voice generation: FAILED")
            return False
        
        print("✅ All integrations tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def start_application():
    """Start the AUDEXA application"""
    print("\n🚀 Starting AUDEXA application...")
    print()
    print("📱 WhatsApp Integration: ACTIVE")
    print("🤖 Telegram Integration: ACTIVE")
    print("🎤 Voice Features: ACTIVE")
    print("🌍 Multilingual Support: ACTIVE")
    print()
    print("🌐 Web Interface: http://127.0.0.1:5000")
    print("📱 WhatsApp Webhook: http://127.0.0.1:5000/chatbot")
    print("🤖 Telegram Webhook: http://127.0.0.1:5000/telegram")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        # Start the application
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n\n🛑 AUDEXA stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")

def main():
    """Main function"""
    print_banner()
    
    # Check environment
    if not check_environment():
        return 1
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Test integrations
    if not test_integrations():
        return 1
    
    # Start application
    start_application()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

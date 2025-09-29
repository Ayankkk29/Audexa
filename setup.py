#!/usr/bin/env python3
"""
ListenAI Setup Script
This script helps you set up the ListenAI application with all required dependencies.
"""

import os
import sys
import subprocess
import platform

def print_banner():
    print("=" * 60)
    print("🎤 ListenAI - AI Mental Health Assistant Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ {env_file} already exists")
        return True
    
    print(f"\n📝 Creating {env_file} file...")
    env_content = """# Flask Configuration
FLASK_DEBUG=True
FLASK_APP=app.py
FLASK_RUN_PORT=5000

# Google Gemini API Key (REQUIRED)
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_KEY=your_actual_gemini_api_key_here

# Cohere API Key (Optional - for sentiment analysis)
# Get your API key from: https://cohere.ai/
COHERE_API_KEY=your_cohere_api_key_here

# Twilio Configuration (Optional - for WhatsApp integration)
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ {env_file} created successfully!")
        print("⚠️  Please edit the .env file and add your actual API keys")
        return True
    except Exception as e:
        print(f"❌ Error creating {env_file}: {e}")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  FFmpeg not found - audio processing may be limited")
        print("   Install FFmpeg for full audio support:")
        if platform.system() == "Windows":
            print("   - Download from: https://ffmpeg.org/download.html")
            print("   - Or use: winget install ffmpeg")
        elif platform.system() == "Darwin":  # macOS
            print("   - Use: brew install ffmpeg")
        else:  # Linux
            print("   - Use: sudo apt install ffmpeg (Ubuntu/Debian)")
            print("   - Or: sudo yum install ffmpeg (CentOS/RHEL)")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete! Next Steps:")
    print("=" * 60)
    print()
    print("1. 📝 Edit the .env file and add your API keys:")
    print("   - Get Gemini API key: https://makersuite.google.com/app/apikey")
    print("   - Replace 'your_actual_gemini_api_key_here' with your real key")
    print()
    print("2. 🚀 Run the application:")
    print("   python app.py")
    print()
    print("3. 🌐 Open your browser and go to:")
    print("   http://127.0.0.1:5000")
    print()
    print("4. 🎤 Test the features:")
    print("   - Try voice recording (microphone icon)")
    print("   - Test different languages")
    print("   - Use voice responses (speaker icon)")
    print()
    print("5. 📖 Check TEST_EXAMPLES.md for testing examples")
    print()
    print("🔧 Troubleshooting:")
    print("   - If voice doesn't work, check microphone permissions")
    print("   - If audio processing fails, install FFmpeg")
    print("   - Check console for error messages")
    print()

def main():
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed during package installation")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("\n❌ Setup failed during .env file creation")
        sys.exit(1)
    
    # Check FFmpeg
    check_ffmpeg()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()

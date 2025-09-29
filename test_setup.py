#!/usr/bin/env python3
"""
Test script for ListenAI setup
This script helps verify that your API keys are configured correctly
"""

import os
from dotenv import load_dotenv

def test_environment():
    """Test if environment variables are loaded correctly"""
    print("🔍 Testing ListenAI Environment Configuration...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check required variables
    gemini_key = os.getenv("GEMINI_KEY")
    cohere_key = os.getenv("COHERE_API_KEY")
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    print(f"✅ GEMINI_KEY: {'✅ Configured' if gemini_key and gemini_key != 'your_gemini_api_key_here' else '❌ Not configured'}")
    print(f"✅ COHERE_API_KEY: {'✅ Configured' if cohere_key and cohere_key != 'your_cohere_api_key_here' else '❌ Not configured'}")
    print(f"✅ TWILIO_ACCOUNT_SID: {'✅ Configured' if twilio_sid and twilio_sid != 'your_twilio_account_sid_here' else '❌ Not configured'}")
    print(f"✅ TWILIO_AUTH_TOKEN: {'✅ Configured' if twilio_token and twilio_token != 'your_twilio_auth_token_here' else '❌ Not configured'}")
    
    print("\n" + "=" * 50)
    
    if not gemini_key or gemini_key == 'your_gemini_api_key_here':
        print("❌ CRITICAL: GEMINI_KEY is not configured!")
        print("\n📋 To fix this:")
        print("1. Go to: https://makersuite.google.com/app/apikey")
        print("2. Sign in with your Google account")
        print("3. Click 'Create API Key'")
        print("4. Copy the generated API key")
        print("5. Create a .env file in this directory with:")
        print("   GEMINI_KEY=your_actual_api_key_here")
        print("6. Restart the application")
        return False
    
    print("✅ GEMINI_KEY is configured correctly!")
    return True

def test_gemini_connection():
    """Test if Gemini API is working"""
    print("\n🧪 Testing Gemini API Connection...")
    print("=" * 50)
    
    try:
        import google.generativeai as genai
        from backend.config import Config
        
        # Configure Gemini
        genai.configure(api_key=Config.GEMINI_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Test with a simple prompt
        response = model.generate_content("Say 'Hello from ListenAI!' in one sentence.")
        print(f"✅ Gemini API Test: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API Test Failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 ListenAI Setup Test")
    print("=" * 50)
    
    # Test environment
    env_ok = test_environment()
    
    if env_ok:
        # Test Gemini connection
        gemini_ok = test_gemini_connection()
        
        if gemini_ok:
            print("\n🎉 All tests passed! ListenAI is ready to run.")
            print("Run 'python app.py' to start the application.")
        else:
            print("\n❌ Gemini API test failed. Check your API key.")
    else:
        print("\n❌ Environment not configured. Please fix the issues above.")

if __name__ == "__main__":
    main()

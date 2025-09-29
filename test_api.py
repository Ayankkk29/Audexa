#!/usr/bin/env python3
"""
Test script to verify API keys and AI functionality
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API functionality"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_KEY")
        if not api_key:
            print("❌ GEMINI_KEY not found in environment")
            return False
            
        print(f"✅ GEMINI_KEY found: {api_key[:20]}...")
        
        genai.configure(api_key=api_key)
        
        # Test with a simple query
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello, respond with 'AI is working'")
        
        print(f"✅ Gemini API Test Successful!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return False

def test_cohere_api():
    """Test Cohere API functionality"""
    try:
        import cohere
        
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            print("❌ COHERE_API_KEY not found in environment")
            return False
            
        print(f"✅ COHERE_API_KEY found: {api_key[:20]}...")
        
        co = cohere.Client(api_key)
        
        # Test sentiment analysis
        response = co.classify(
            model='embed-english-v2.0',
            inputs=["I'm feeling great today!"],
            examples=[("I love this!", "positive"), ("This is terrible", "negative")]
        )
        
        print(f"✅ Cohere API Test Successful!")
        return True
        
    except Exception as e:
        print(f"❌ Cohere API Error: {e}")
        return False

def test_telegram_api():
    """Test Telegram API functionality"""
    try:
        from telegram import Bot
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            print("❌ TELEGRAM_BOT_TOKEN not found in environment")
            return False
            
        print(f"✅ TELEGRAM_BOT_TOKEN found: {token[:20]}...")
        
        bot = Bot(token=token)
        bot_info = bot.get_me()
        
        print(f"✅ Telegram API Test Successful!")
        print(f"Bot name: {bot_info.first_name}")
        return True
        
    except Exception as e:
        print(f"❌ Telegram API Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing AUDEXA API Keys and AI Functionality")
    print("=" * 50)
    
    # Test all APIs
    gemini_ok = test_gemini_api()
    print()
    
    cohere_ok = test_cohere_api()
    print()
    
    telegram_ok = test_telegram_api()
    print()
    
    print("=" * 50)
    print("📊 Test Results:")
    print(f"🤖 Gemini AI: {'✅ Working' if gemini_ok else '❌ Failed'}")
    print(f"🧠 Cohere Sentiment: {'✅ Working' if cohere_ok else '❌ Failed'}")
    print(f"📱 Telegram Bot: {'✅ Working' if telegram_ok else '❌ Failed'}")
    
    if gemini_ok:
        print("\n🎉 AI functionality is ready! The chatbot should work properly.")
    else:
        print("\n⚠️ AI functionality needs to be fixed.")

"""
Enhanced messaging integration for WhatsApp and Telegram
Supports voice messages, multilingual responses, and text-to-speech
"""

import os
import json
import requests
import tempfile
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse, Message
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from backend.wbot import GeminiBot, get_welcome_message
from backend.api import get_gemini_response, get_fallback_response
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessagingBot:
    def __init__(self):
        # Twilio configuration
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Telegram configuration
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        # Initialize Twilio client
        if self.twilio_account_sid and self.twilio_auth_token:
            self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
        else:
            self.twilio_client = None
            logger.warning("Twilio credentials not configured")
        
        # Initialize Telegram bot
        if self.telegram_token:
            self.telegram_bot = Bot(token=self.telegram_token)
        else:
            self.telegram_bot = None
            logger.warning("Telegram bot token not configured")
    
    def detect_language(self, text: str) -> str:
        """Enhanced language detection from text"""
        # Simple language detection based on script
        if any('\u0900' <= char <= '\u097F' for char in text):  # Devanagari
            return 'hi'
        elif any('\u0980' <= char <= '\u09FF' for char in text):  # Bengali
            return 'bn'
        elif any('\u0B80' <= char <= '\u0BFF' for char in text):  # Tamil
            return 'ta'
        elif any('\u0C00' <= char <= '\u0C7F' for char in text):  # Telugu
            return 'te'
        elif any('\u0A80' <= char <= '\u0AFF' for char in text):  # Gujarati
            return 'gu'
        elif any('\u0A00' <= char <= '\u0A7F' for char in text):  # Gurmukhi (Punjabi)
            return 'pa'
        elif any('\u0C80' <= char <= '\u0CFF' for char in text):  # Kannada
            return 'kn'
        elif any('\u0D00' <= char <= '\u0D7F' for char in text):  # Malayalam
            return 'ml'
        elif any('\u0600' <= char <= '\u06FF' for char in text):  # Arabic/Persian/Urdu
            return 'ur'
        elif any('\u4E00' <= char <= '\u9FFF' for char in text):  # Chinese
            return 'zh'
        elif any('\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF' for char in text):  # Japanese
            return 'ja'
        elif any('\uAC00' <= char <= '\uD7AF' for char in text):  # Korean
            return 'ko'
        elif any('\u0400' <= char <= '\u04FF' for char in text):  # Cyrillic (Russian)
            return 'ru'
        elif any('\u1E00' <= char <= '\u1EFF' for char in text):  # Latin Extended (Spanish, French, etc.)
            # Check for common Spanish words
            spanish_words = ['hola', 'gracias', 'por favor', 'sí', 'no', 'buenos', 'días', 'noche', 'cómo', 'estás']
            if any(word in text.lower() for word in spanish_words):
                return 'es'
            # Check for common French words
            french_words = ['bonjour', 'merci', 's\'il vous plaît', 'oui', 'non', 'comment', 'allez-vous']
            if any(word in text.lower() for word in french_words):
                return 'fr'
            # Check for common German words
            german_words = ['hallo', 'danke', 'bitte', 'ja', 'nein', 'wie', 'geht', 'es']
            if any(word in text.lower() for word in german_words):
                return 'de'
            return 'es'  # Default to Spanish for Latin extended
        else:
            return 'en'  # Default to English
    
    def get_ai_response(self, message: str, user_id: str, platform: str = "whatsapp") -> Dict[str, Any]:
        """Get AI response with language detection and voice support"""
        try:
            # Detect language
            detected_lang = self.detect_language(message)
            
            # Create conversation history
            messages = [
                {
                    "role": "system",
                    "content": f"You are AUDEXA, a compassionate mental health AI assistant. Respond in {detected_lang} if possible, otherwise in English. Provide comprehensive, helpful responses with detailed information and guidance. Be warm, professional, and supportive."
                }
            ]
            
            # Get AI response
            response_text = get_gemini_response(message, messages)
            
            return {
                "text": response_text,
                "language": detected_lang,
                "platform": platform,
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return {
                "text": "I'm sorry, I'm having trouble processing your message right now. Please try again later.",
                "language": "en",
                "platform": platform,
                "user_id": user_id
            }
    
    def send_whatsapp_message(self, to: str, message: str, media_url: Optional[str] = None) -> bool:
        """Send WhatsApp message via Twilio"""
        if not self.twilio_client:
            logger.error("Twilio client not initialized")
            return False
        
        try:
            message_params = {
                'from_': f'whatsapp:{self.twilio_phone_number}',
                'to': f'whatsapp:{to}',
                'body': message
            }
            
            if media_url:
                message_params['media_url'] = [media_url]
            
            message = self.twilio_client.messages.create(**message_params)
            logger.info(f"WhatsApp message sent: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    def send_telegram_message(self, chat_id: str, message: str, voice_file: Optional[str] = None) -> bool:
        """Send Telegram message"""
        if not self.telegram_bot:
            logger.error("Telegram bot not initialized")
            return False
        
        try:
            if voice_file:
                with open(voice_file, 'rb') as voice:
                    self.telegram_bot.send_voice(chat_id=chat_id, voice=voice, caption=message)
            else:
                self.telegram_bot.send_message(chat_id=chat_id, text=message)
            
            logger.info(f"Telegram message sent to {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def generate_voice_response(self, text: str, language: str = "en") -> Optional[str]:
        """Optimized voice generation with faster response times"""
        try:
            from gtts import gTTS
            import tempfile
            import time
            
            start_time = time.time()
            
            # Optimized language mapping
            language_map = {
                'hi': 'hi', 'bn': 'bn', 'ta': 'ta', 'te': 'te', 'gu': 'gu', 'pa': 'pa',
                'kn': 'kn', 'ml': 'ml', 'ur': 'ur', 'zh': 'zh', 'ja': 'ja', 'ko': 'ko',
                'ru': 'ru', 'es': 'es', 'fr': 'fr', 'de': 'de', 'it': 'it', 'pt': 'pt',
                'ar': 'ar', 'en': 'en'
            }
            
            tts_lang = language_map.get(language, 'en')
            
            # For faster response, limit text length
            if len(text) > 300:
                logger.warning(f"Long text detected ({len(text)} chars), truncating for faster TTS")
                text = text[:300] + "..."
            
            # Create TTS with optimized settings for speed
            tts = gTTS(
                text=text, 
                lang=tts_lang, 
                slow=False,  # Fast speech
                tld='com'    # Use faster server
            )
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            tts.save(temp_file.name)
            temp_file.close()
            
            generation_time = time.time() - start_time
            logger.info(f"⚡ Voice generated in {generation_time:.2f}s ({tts_lang}): {text[:30]}...")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error generating voice for language {language}: {e}")
            # Fast fallback to English
            try:
                tts = gTTS(text=text[:300], lang='en', slow=False, tld='com')
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                tts.save(temp_file.name)
                temp_file.close()
                
                generation_time = time.time() - start_time
                logger.info(f"⚡ Fallback voice in {generation_time:.2f}s: {text[:30]}...")
                return temp_file.name
            except Exception as fallback_error:
                logger.error(f"Fallback TTS also failed: {fallback_error}")
                return None
    
    def process_whatsapp_webhook(self, request_data: Dict[str, Any]) -> str:
        """Process WhatsApp webhook"""
        try:
            # Extract message data
            wa_id = request_data.get('WaId', '')
            body = request_data.get('Body', '')
            media_url = request_data.get('MediaUrl0', '')
            
            if not body and not media_url:
                return str(MessagingResponse())
            
            # Get AI response
            response_data = self.get_ai_response(body, wa_id, "whatsapp")
            response_text = response_data["text"]
            
            # Create TwiML response
            resp = MessagingResponse()
            msg = resp.message()
            msg.body(response_text)
            
            # If user requested voice response, generate and send
            if "voice" in body.lower() or "speak" in body.lower():
                voice_file = self.generate_voice_response(response_text, response_data["language"])
                if voice_file:
                    # Upload to a temporary URL (in production, use cloud storage)
                    # For now, we'll just mention voice is available
                    msg.body(f"{response_text}\n\n🎤 Voice response available - say 'voice' to hear it!")
            
            return str(resp)
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp webhook: {e}")
            resp = MessagingResponse()
            resp.message("Sorry, I'm having trouble right now. Please try again later.")
            return str(resp)
    
    async def process_telegram_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Process Telegram message"""
        try:
            message = update.message
            chat_id = str(message.chat_id)
            user_id = str(message.from_user.id)
            
            # Handle text messages
            if message.text:
                response_data = self.get_ai_response(message.text, user_id, "telegram")
                response_text = response_data["text"]
                
                # Send text response
                await context.bot.send_message(chat_id=chat_id, text=response_text)
                
                # If user requested voice, generate and send
                if "voice" in message.text.lower() or "speak" in message.text.lower():
                    voice_file = self.generate_voice_response(response_text, response_data["language"])
                    if voice_file:
                        with open(voice_file, 'rb') as voice:
                            await context.bot.send_voice(chat_id=chat_id, voice=voice, caption="AUDEXA's voice response")
                        os.unlink(voice_file)  # Clean up temp file
            
            # Handle voice messages
            elif message.voice:
                # Download voice file
                voice_file = await context.bot.get_file(message.voice.file_id)
                voice_path = f"temp_voice_{user_id}.ogg"
                await voice_file.download_to_drive(voice_path)
                
                # Process voice with Whisper (you'd need to implement this)
                # For now, send a text response
                response_text = "I received your voice message! Voice processing is coming soon. For now, please send text messages."
                await context.bot.send_message(chat_id=chat_id, text=response_text)
                
                # Clean up
                if os.path.exists(voice_path):
                    os.unlink(voice_path)
            
        except Exception as e:
            logger.error(f"Error processing Telegram message: {e}")
            await context.bot.send_message(chat_id=chat_id, text="Sorry, I'm having trouble right now. Please try again later.")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        # Get language from context or default to English
        language = context.args[0] if context.args else "en"
        welcome_message = get_welcome_message(language)
        
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        help_message = """🆘 AUDEXA Help

Available commands:
/start - Welcome message
/help - This help message
/voice - Get voice response for your last message

Features:
• Multilingual support (Hindi, English, Spanish, etc.)
• Voice responses
• Mental health guidance
• Crisis support

Just send me a message and I'll help you!"""
        
        await update.message.reply_text(help_message)
    
    def setup_telegram_bot(self) -> Optional[Application]:
        """Setup Telegram bot application"""
        if not self.telegram_token:
            logger.warning("Telegram token not configured")
            return None
        
        try:
            # Create application
            application = Application.builder().token(self.telegram_token).build()
            
            # Add handlers
            application.add_handler(CommandHandler("start", self.start_command))
            application.add_handler(CommandHandler("help", self.help_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_telegram_message))
            application.add_handler(MessageHandler(filters.VOICE, self.process_telegram_message))
            
            return application
            
        except Exception as e:
            logger.error(f"Error setting up Telegram bot: {e}")
            return None

# Global instance
messaging_bot = MessagingBot()

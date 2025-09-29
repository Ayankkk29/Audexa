from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import asyncio
import threading

# Load environment variables BEFORE importing modules that read them
load_dotenv()

from backend.api import api  # Import your api blueprint
from backend.wbot import GeminiBot
from backend.messaging import messaging_bot  # Import for Telegram only

def create_app():
    app = Flask(__name__)

    with app.app_context():
        app.register_blueprint(api, url_prefix="/home/api")  # Register the api blueprint

        @app.route("/")  # Add this route for the root URL
        def index():
            return render_template("index.html")
        
        @app.route("/messaging")
        def messaging():
            return render_template("messaging.html")
        
        
        


        # WhatsApp integration removed
        
        @app.route("/telegram", methods=["POST"])
        def telegram_webhook():
            """Telegram webhook endpoint"""
            try:
                # This would be called by Telegram
                # The actual processing is handled by the Telegram bot application
                return jsonify({"status": "ok"})
            except Exception as e:
                print(f"Error in Telegram webhook: {e}")
                return jsonify({"status": "error"}), 500
        
        # WhatsApp send API removed
        
        @app.route("/send_telegram", methods=["POST"])
        def send_telegram():
            """Send Telegram message via API"""
            try:
                data = request.get_json()
                chat_id = data.get('chat_id')
                message = data.get('message')
                
                if not chat_id or not message:
                    return jsonify({"error": "Missing 'chat_id' or 'message' parameter"}), 400
                
                success = messaging_bot.send_telegram_message(chat_id, message)
                
                if success:
                    return jsonify({"status": "success", "message": "Message sent"})
                else:
                    return jsonify({"status": "error", "message": "Failed to send message"}), 500
                    
            except Exception as e:
                print(f"Error sending Telegram message: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500

        @app.after_request
        def after_request(response):
            request.get_data()
            return response

    return app

app = create_app()

def run_telegram_bot():
    """Run Telegram bot in a separate thread"""
    try:
        import asyncio
        telegram_app = messaging_bot.setup_telegram_bot()
        if telegram_app:
            print("🤖 Starting Telegram bot...")
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(telegram_app.run_polling())
        else:
            print("⚠️ Telegram bot not configured - skipping")
    except Exception as e:
        print(f"❌ Error running Telegram bot: {e}")

if __name__ == "__main__":
    # Start Telegram bot in a separate thread
    telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    telegram_thread.start()
    
    print("🚀 Starting AUDEXA Flask application...")
    print("🤖 Telegram webhook: http://127.0.0.1:5000/telegram")
    print("🌐 Web interface: http://127.0.0.1:5000")
    
    app.run(host="127.0.0.1", debug=True, port=5000)

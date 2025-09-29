import json
import os
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            # Read the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            message = data.get('message', '').lower()
            
            # Enhanced AI responses for mental health support
            responses = {
                'hello': "Hello! I'm AUDEXA, your mental health AI assistant. I'm here to provide support, guidance, and a listening ear. How are you feeling today? 😊",
                'anxiety': "I understand you're feeling anxious. Let's work through this together. Try the 4-7-8 breathing technique: inhale for 4, hold for 7, exhale for 8. What's making you feel anxious right now? 💙",
                'sad': "I'm sorry you're feeling down. It's completely okay to feel this way. You're not alone, and I'm here to support you. What's been weighing on your mind? 🌟",
                'stress': "Stress can be overwhelming. Let's break it down together. Try the 5-4-3-2-1 grounding technique: 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste. What's causing you stress? 🤝",
                'sleep': "Sleep issues can really affect your well-being. Try establishing a consistent bedtime routine: no screens 1 hour before bed, cool dark room, same sleep/wake times daily. What's keeping you up? 🌙",
                'help': "I'm here to help! I can provide support for anxiety, depression, stress management, sleep issues, and general mental wellness. What would you like to talk about? 💚",
                'thank': "You're very welcome! I'm always here when you need someone to talk to. Remember, seeking help is a sign of strength, not weakness. 💪"
            }
            
            # Check for specific mental health keywords
            response_text = None
            for key, response in responses.items():
                if key in message:
                    response_text = response
                    break
            
            # Check for emotional indicators
            if not response_text:
                if any(word in message for word in ['worried', 'nervous', 'panic', 'fear']):
                    response_text = "I can sense you're feeling worried. Anxiety is a normal human emotion. Let's talk about what's on your mind. You're safe here, and I'm listening. 💙"
                elif any(word in message for word in ['depressed', 'hopeless', 'empty', 'worthless']):
                    response_text = "I hear that you're going through a difficult time. Depression can make everything feel heavy. You matter, and your feelings are valid. What's been the hardest part lately? 🌟"
                elif any(word in message for word in ['angry', 'frustrated', 'irritated', 'mad']):
                    response_text = "Anger is a natural emotion, and it's okay to feel frustrated. Let's explore what's behind these feelings. Sometimes anger masks other emotions. What's really bothering you? 🔥"
                elif any(word in message for word in ['lonely', 'isolated', 'alone', 'disconnected']):
                    response_text = "Feeling lonely can be really tough. You're not truly alone - I'm here, and there are people who care about you. What would help you feel more connected? 🤗"
                else:
                    response_text = "I'm listening and here to help. Please tell me more about what's on your mind or how you're feeling. I can provide support for mental health, stress management, and general wellness. What's going on? 💭"
            
            # Send response
            response_data = {'response': response_text}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            error_response = {'response': "I'm here to help! Please tell me more about what's on your mind. 💭"}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

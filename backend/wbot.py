
import google.generativeai as genai
import re
import json
import requests
from backend.config import Config
from backend.career_guidance import career_guidance
from dotenv import load_dotenv
import os

GEMINI_API_KEY = os.getenv("GEMINI_KEY")

def get_welcome_message(language: str = "en") -> str:
    """Generate welcome message in the specified language"""
    welcome_messages = {
        'hi': "नमस्ते! मैं AUDEXA हूं, आपकी मानसिक स्वास्थ्य सहायक AI। मैं यहां आपकी मदद के लिए हूं। आप कैसे हैं? 🤗",
        'bn': "নমস্কার! আমি AUDEXA, আপনার মানসিক স্বাস্থ্য সহায়ক AI। আমি এখানে আপনার সাহায্যের জন্য আছি। আপনি কেমন আছেন? 🤗",
        'ta': "வணக்கம்! நான் AUDEXA, உங்கள் மன ஆரோக்கிய உதவியாளர் AI। நான் உங்களுக்கு உதவ இங்கே இருக்கிறேன்। நீங்கள் எப்படி இருக்கிறீர்கள்? 🤗",
        'te': "నమస్కారం! నేను AUDEXA, మీ మానసిక ఆరోగ్య సహాయక AI। నేను మీకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను। మీరు ఎలా ఉన్నారు? 🤗",
        'gu': "નમસ્તે! હું AUDEXA છું, તમારી માનસિક આરોગ્ય સહાયક AI। હું તમારી મદદ માટે અહીં છું। તમે કેવી રીતે છો? 🤗",
        'pa': "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ AUDEXA ਹਾਂ, ਤੁਹਾਡੀ ਮਾਨਸਿਕ ਸਿਹਤ ਸਹਾਇਕ AI। ਮੈਂ ਤੁਹਾਡੀ ਮਦਦ ਲਈ ਇੱਥੇ ਹਾਂ। ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ? 🤗",
        'kn': "ನಮಸ್ಕಾರ! ನಾನು AUDEXA, ನಿಮ್ಮ ಮಾನಸಿಕ ಆರೋಗ್ಯ ಸಹಾಯಕ AI। ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿದ್ದೇನೆ। ನೀವು ಹೇಗಿದ್ದೀರಿ? 🤗",
        'ml': "നമസ്കാരം! ഞാൻ AUDEXA ആണ്, നിങ്ങളുടെ മാനസികാരോഗ്യ സഹായി AI। നിങ്ങളെ സഹായിക്കാൻ ഞാൻ ഇവിടെയുണ്ട്। നിങ്ങൾ എങ്ങനെയാണ്? 🤗",
        'ur': "السلام علیکم! میں AUDEXA ہوں، آپ کا ذہنی صحت کا معاون AI۔ میں آپ کی مدد کے لیے یہاں ہوں۔ آپ کیسے ہیں؟ 🤗",
        'es': "¡Hola! Soy AUDEXA, tu asistente de IA para salud mental. Estoy aquí para ayudarte. ¿Cómo estás? 🤗",
        'fr': "Bonjour! Je suis AUDEXA, votre assistant IA pour la santé mentale. Je suis là pour vous aider. Comment allez-vous? 🤗",
        'de': "Hallo! Ich bin AUDEXA, Ihr KI-Assistent für psychische Gesundheit. Ich bin hier, um Ihnen zu helfen. Wie geht es Ihnen? 🤗",
        'it': "Ciao! Sono AUDEXA, il tuo assistente IA per la salute mentale. Sono qui per aiutarti. Come stai? 🤗",
        'pt': "Olá! Eu sou AUDEXA, seu assistente de IA para saúde mental. Estou aqui para ajudá-lo. Como você está? 🤗",
        'ru': "Привет! Я AUDEXA, ваш ИИ-помощник по психическому здоровью. Я здесь, чтобы помочь вам. Как дела? 🤗",
        'ja': "こんにちは！私はAUDEXA、あなたのメンタルヘルスAIアシスタントです。お手伝いするためにここにいます。お元気ですか？ 🤗",
        'ko': "안녕하세요! 저는 AUDEXA, 당신의 정신건강 AI 어시스턴트입니다. 도움을 드리기 위해 여기 있습니다. 어떻게 지내세요? 🤗",
        'zh': "你好！我是AUDEXA，您的心理健康AI助手。我在这里帮助您。您怎么样？ 🤗",
        'ar': "مرحبا! أنا AUDEXA، مساعد الذكاء الاصطناعي لصحتك العقلية. أنا هنا لمساعدتك. كيف حالك؟ 🤗",
        'en': "Hey! I'm AUDEXA, your friendly AI assistant. I'm here to help with mental health, career stuff, and even music recommendations! What's on your mind today? 🤗"
    }
    
    return welcome_messages.get(language, welcome_messages['en'])

class GeminiBot:
    def __init__(self, id, language="en"):
        self.id = id
        self.language = language
        self.file_name = f"{str(self.id)}.json"
        welcome_msg = get_welcome_message(self.language)
        self.session = {
            "start": True,
            "data": welcome_msg,
            "log": [
                {
                    "role": "system",
                    "content": """You are AUDEXA, a friendly and conversational AI for mental health support, career guidance, and music recommendations.

Response Style:
- Provide comprehensive, detailed responses when appropriate.
- Use clear, professional language while remaining warm and encouraging.
- Include helpful explanations and context.
- Use numbered bullets (1. 2. 3.) when giving specific steps or lists.
- Provide thorough information to help users understand topics better.
- Be informative and educational while maintaining a supportive tone.

Music Recommendations:
- When users ask for music, first ask about their current mood in a caring way.
- Based on their mood, suggest 2-3 short, relevant music recommendations with Spotify and YouTube links.
- Always provide both Spotify and YouTube links for each recommendation.
- Keep tone supportive and positive.
- Always add an encouraging line like "I hope this lifts your mood!" or "This might help you feel calmer!"
- Keep music suggestions brief and conversational.

Link Format Examples:
- Spotify: https://open.spotify.com/track/[track-id] or https://open.spotify.com/playlist/[playlist-id]
- YouTube: https://youtube.com/watch?v=[video-id] or https://youtube.com/playlist?list=[playlist-id]

Safety:
- If self-harm or danger is mentioned, provide crisis resources immediately and keep responses calm and brief.

Example format:
"Here's what I suggest: [brief advice]. 

1. First step
2. Second step

What's your biggest concern about this?"

Music recommendation example:
"Here are some calming songs for you:

1. 'Weightless' by Marconi Union
   Spotify: https://open.spotify.com/track/2U6dF1uI7pmTQ1L8YJqBIS
   YouTube: https://youtube.com/watch?v=UfcAVejslrU

2. 'Clair de Lune' by Debussy
   Spotify: https://open.spotify.com/track/1Ird9j4pHx8k8lK6JLOd5D
   YouTube: https://youtube.com/watch?v=CvFH_6DNRCY

This might help you feel calmer! How are you feeling now?"

You are not a replacement for professional care.""",
                },
                {
                    "role": "assistant",
                    "content": welcome_msg,
                },
            ],
        }

        try:
            with open(self.file_name) as outfile:
                data = json.load(outfile)
            outfile.close()
            self.session = data
        except Exception:
            with open(self.file_name, "w") as outfile:
                json.dump(self.session, outfile)
            outfile.close()

    def bot(self, input_query):

        if self.session["start"]:

            self.session["start"] = False
            with open(self.file_name, "w") as outfile:
                json.dump(self.session, outfile)
            outfile.close()
            return get_welcome_message(self.language)

        # Configure Gemini
        if not GEMINI_API_KEY:
            return "I apologize, but the Gemini API key is not configured. Please set GEMINI_KEY to use Google Gemini."
        
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Build conversation history for Gemini
            conversation_history = []
            for message in self.session["log"]:
                if message["role"] == "user":
                    conversation_history.append(f"USER: {message['content']}")
                elif message["role"] == "assistant":
                    conversation_history.append(f"ASSISTANT: {message['content']}")
            
            # Add current user query
            conversation_history.append(f"USER: {input_query}")
            
            # Check for career guidance keywords and enhance response
            career_enhancement = self._get_career_enhancement(input_query)
            
            # Check for music recommendation keywords and enhance response
            music_enhancement = self._get_music_enhancement(input_query)
            
            # Create full prompt
            system_prompt = self.session["log"][0]["content"]
            full_prompt = f"{system_prompt}\n\n" + "\n".join(conversation_history) + "\n\nASSISTANT:"
            
            # Generate response
            response = model.generate_content(full_prompt)
            res = getattr(response, "text", "") or "I couldn't generate a response. Could you rephrase that?"
            
            # Add career guidance enhancement if applicable
            if career_enhancement:
                res += career_enhancement
            
            # Add music enhancement if applicable
            if music_enhancement:
                res += music_enhancement
            
        except Exception as e:
            res = f"I apologize, but there was an error processing your request: {str(e)}"

        self.session["log"].append({"role": "user", "content": input_query})
        self.session["log"].append({"role": "assistant", "content": res})
        self.session["data"] += res + " \n "
        with open(self.file_name, "w") as jsonFile:
            json.dump(self.session, jsonFile)
        jsonFile.close()

        return res

    def _get_career_enhancement(self, user_input: str) -> str:
        """Get career guidance enhancement based on user input"""
        user_input_lower = user_input.lower()
        enhancement = ""
        
        # Career assessment questions
        if any(keyword in user_input_lower for keyword in ["career assessment", "what should i do", "career path", "career choice"]):
            questions = career_guidance.get_career_assessment_questions()
            enhancement += "\n\nCareer check-in — consider:\n"
            for i, question in enumerate(questions[:3], 1):
                enhancement += f"{i}. {question}\n"
        
        # Resume help
        if any(keyword in user_input_lower for keyword in ["resume", "cv", "curriculum vitae"]):
            tips = career_guidance.get_career_resources("resume_tips")
            enhancement += "\n\nResume — quick tips:\n"
            for i, tip in enumerate(tips[:3], 1):
                enhancement += f"{i}. {tip}\n"
        
        # Interview preparation
        if any(keyword in user_input_lower for keyword in ["interview", "interviewing", "job interview"]):
            tips = career_guidance.get_career_resources("interview_preparation")
            enhancement += "\n\nInterview — do this:\n"
            for i, tip in enumerate(tips[:3], 1):
                enhancement += f"{i}. {tip}\n"
        
        # Job search
        if any(keyword in user_input_lower for keyword in ["job search", "finding a job", "looking for work"]):
            platforms = career_guidance.get_career_resources("job_search_platforms")
            enhancement += "\n\nTry these platforms:\n"
            for i, platform in enumerate(platforms[:3], 1):
                enhancement += f"{i}. {platform}\n"
        
        # Skills development
        if any(keyword in user_input_lower for keyword in ["skills", "learning", "training", "development"]):
            platforms = career_guidance.get_career_resources("skill_development")
            enhancement += "\n\nLevel up — learn here:\n"
            for i, platform in enumerate(platforms[:3], 1):
                enhancement += f"{i}. {platform}\n"
        
        # Salary negotiation
        if any(keyword in user_input_lower for keyword in ["salary", "negotiation", "pay", "compensation"]):
            tips = career_guidance.get_salary_negotiation_tips()
            enhancement += "\n\nNegotiation — keep in mind:\n"
            for i, tip in enumerate(tips[:3], 1):
                enhancement += f"{i}. {tip}\n"
        
        # Work-life balance
        if any(keyword in user_input_lower for keyword in ["work life balance", "work-life balance", "burnout", "stress at work"]):
            tips = career_guidance.get_work_life_balance_tips()
            enhancement += "\n\nBalance — quick ideas:\n"
            for i, tip in enumerate(tips[:3], 1):
                enhancement += f"{i}. {tip}\n"
        
        # Industry insights
        for industry in ["technology", "healthcare", "finance", "marketing"]:
            if industry in user_input_lower:
                insights = career_guidance.get_industry_insights(industry)
                if "message" not in insights:
                    enhancement += f"\n\n{industry.title()} — quick view:\n"
                    enhancement += f"Roles: {', '.join(insights['trending_roles'][:3])}\n"
                    enhancement += f"Skills: {', '.join(insights['in_demand_skills'][:3])}\n"
                    enhancement += f"Pay: {insights['salary_range']}\n"
                    enhancement += f"Outlook: {insights['growth_prospects']}\n"
                break
        
        return enhancement

    def _get_music_enhancement(self, user_input: str) -> str:
        """Get music recommendations based on user input"""
        user_input_lower = user_input.lower()
        enhancement = ""
        
        # Music recommendation keywords - expanded list
        music_keywords = ["music", "song", "songs", "playlist", "recommend music", "music recommendation", "what music", "suggest music", "play music", "listen to music", "music suggestions", "recommend songs", "suggest songs", "music for", "songs for", "playlist for", "music to", "songs to", "listen", "play", "audio", "soundtrack", "melody", "tune", "track", "album", "artist", "band", "singer"]
        
        if any(keyword in user_input_lower for keyword in music_keywords):
            print(f"Music keywords detected in: {user_input_lower}")  # Debug print
            # Check for mood indicators
            if any(mood in user_input_lower for mood in ["sad", "depressed", "down", "blue", "upset", "crying"]):
                enhancement += "\n\nHere are some uplifting songs for you:\n\n"
                enhancement += "1. 'Here Comes the Sun' by The Beatles\n"
                enhancement += "   Spotify: https://open.spotify.com/track/6dGnYIeXmHdcikdzNNDMm2\n"
                enhancement += "   YouTube: https://youtube.com/watch?v=KQetemT1sWc\n\n"
                enhancement += "2. 'Don't Stop Believin'' by Journey\n"
                enhancement += "   Spotify: https://open.spotify.com/track/4bHsxqR3GMrXTxEPLuK5ue\n"
                enhancement += "   YouTube: https://youtube.com/watch?v=VcjzHMhBtf0\n\n"
                enhancement += "3. 'Good as Hell' by Lizzo\n"
                enhancement += "   Spotify: https://open.spotify.com/track/6KgBpzTuTRPebChN0VTyzV\n"
                enhancement += "   YouTube: https://youtube.com/watch?v=8iU8LPEa4X0\n\n"
                enhancement += "I hope this lifts your mood! How are you feeling now?"
                
            elif any(mood in user_input_lower for mood in ["stressed", "anxious", "worried", "tense", "overwhelmed"]):
                enhancement += "\n\nHere are some calming songs for you:\n\n"
                enhancement += "1. 'Weightless' by Marconi Union\n"
                enhancement += "   Spotify: https://open.spotify.com/track/2U6dF1uI7pmTQ1L8YJqBIS\n"
                enhancement += "   YouTube: https://youtube.com/watch?v=UfcAVejslrU\n\n"
                enhancement += "2. 'Clair de Lune' by Debussy\n"
                enhancement += "   Spotify: https://open.spotify.com/track/1Ird9j4pHx8k8lK6JLOd5D\n"
                enhancement += "   YouTube: https://youtube.com/watch?v=CvFH_6DNRCY\n\n"
                enhancement += "3. 'River Flows in You' by Yiruma\n"
                enhancement += "   Spotify: https://open.spotify.com/track/7yUbfq42KWz1ICZJhU2pTx\n"
                enhancement += "   YouTube: https://youtube.com/watch?v=7maJOI3QMu0\n\n"
                enhancement += "This might help you feel calmer! What's been stressing you out lately?"
                
            elif any(mood in user_input_lower for mood in ["happy", "excited", "energetic", "pumped", "motivated"]):
                enhancement += "\n\nHere are some energetic songs for you:\n\n"
                enhancement += "1. 'Happy' by Pharrell Williams\n"
                enhancement += "   Spotify: https://open.spotify.com/track/6NPVjNh8XhuoY4IF3y9j8N\n"
                enhancement += "   YouTube: https://youtube.com/watch?v=ZbZSe6N_BXs\n\n"
                enhancement += "2. 'Can't Stop the Feeling!' by Justin Timberlake\n"
                enhancement += "   Spotify: https://open.spotify.com/track/1WkMMavIMc4JZ8cfMmxHkI\n"
                enhancement += "   YouTube: https://youtube.com/watch?v=ru0K8uYEZWw\n\n"
                enhancement += "3. 'Uptown Funk' by Mark Ronson ft. Bruno Mars\n"
                enhancement += "   Spotify: https://open.spotify.com/track/32OlwWuMpZ6b0aN2RZOeMS\n"
                enhancement += "   YouTube: https://youtube.com/watch?v=OPf0YbXqDm0\n\n"
                enhancement += "Perfect for your good mood! What's making you feel so great today?"
                
            else:
                # General music recommendation - provide immediate suggestions
                enhancement += "\n\nI'd love to help with music! Here are some great options:\n\n"
                enhancement += "1. 'Weightless' by Marconi Union (for relaxation)\n"
                enhancement += "   Spotify: https://open.spotify.com/track/2U6dF1uI7pmTQ1L8YJqBIS\n"
                enhancement += "   YouTube: https://youtube.com/watch?v=UfcAVejslrU\n\n"
                enhancement += "2. 'Happy' by Pharrell Williams (for energy)\n"
                enhancement += "   Spotify: https://open.spotify.com/track/6NPVjNh8XhuoY4IF3y9j8N\n"
                enhancement += "   YouTube: https://youtube.com/watch?v=ZbZSe6N_BXs\n\n"
                enhancement += "3. 'Here Comes the Sun' by The Beatles (for comfort)\n"
                enhancement += "   Spotify: https://open.spotify.com/track/6dGnYIeXmHdcikdzNNDMm2\n"
                enhancement += "   YouTube: https://youtube.com/watch?v=KQetemT1sWc\n\n"
                enhancement += "How are you feeling? I can suggest more specific songs based on your mood!"
        
        return enhancement


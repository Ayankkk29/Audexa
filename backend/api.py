import re
import os
from flask import Blueprint, request, render_template
from backend.config import Config
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# Optimized sentiment analysis with Cohere and enhanced fallback
try:
    import cohere  # type: ignore
    from cohere.responses.classify import Example  # type: ignore
    COHERE_AVAILABLE = True
except Exception:
    cohere = None  # type: ignore
    COHERE_AVAILABLE = False

    class Example:  # fallback shim to satisfy examples list construction
        def __init__(self, text: str, label: str):
            self.text = text
            self.label = label

# Pre-compiled word lists for faster sentiment analysis
NEGATIVE_WORDS = {
    'sad', 'depressed', 'anxious', 'worried', 'scared', 'angry', 'hopeless', 'lonely', 
    'pain', 'suicidal', 'panic', 'stressed', 'overwhelmed', 'frustrated', 'tired', 
    'exhausted', 'hurt', 'upset', 'crying', 'terrible', 'awful', 'hate', 'can\'t', 
    'won\'t', 'never', 'always', 'everything', 'nothing', 'bad', 'horrible', 'worst',
    'disappointed', 'annoyed', 'irritated', 'mad', 'furious', 'devastated', 'broken',
    'empty', 'lost', 'confused', 'helpless', 'worthless', 'useless', 'failure',
    'sick', 'ill', 'unwell', 'miserable', 'suffering', 'struggling', 'difficult', 'hard',
    'impossible', 'can\'t handle', 'too much', 'overwhelming', 'nightmare', 'disaster'
}

POSITIVE_WORDS = {
    'happy', 'better', 'good', 'great', 'excited', 'hopeful', 'proud', 'calm', 
    'peaceful', 'motivated', 'confident', 'amazing', 'wonderful', 'fantastic', 
    'love', 'enjoy', 'grateful', 'thankful', 'blessed', 'lucky', 'success', 
    'accomplished', 'relieved', 'content', 'excellent', 'perfect', 'awesome',
    'brilliant', 'outstanding', 'incredible', 'marvelous', 'delighted', 'thrilled',
    'ecstatic', 'joyful', 'cheerful', 'optimistic', 'positive', 'energetic',
    'refreshed', 'renewed', 'inspired', 'determined', 'focused', 'clear',
    'satisfied', 'fulfilled', 'complete', 'whole', 'healthy', 'strong', 'powerful'
}

api = Blueprint(
    "api",
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static",
    static_url_path="/static",
)

# Initialize Cohere client with error handling
cohere_client = None
if COHERE_AVAILABLE:
    cohere_api_key = os.getenv("COHERE_API_KEY")
    if cohere_api_key:
        try:
            cohere_client = cohere.Client(cohere_api_key)
            print("✅ Cohere sentiment analysis initialized successfully")
        except Exception as e:
            print(f"⚠️ Cohere initialization failed: {e}")
            cohere_client = None
    else:
        print("⚠️ COHERE_KEY not found in environment variables")
else:
    print("⚠️ Cohere library not available, using fallback sentiment analysis")

def analyze_sentiment_fast(text: str) -> str:
    """Fast sentiment analysis using pre-compiled word sets"""
    text_lower = text.lower()
    words = set(text_lower.split())
    
    negative_count = len(words.intersection(NEGATIVE_WORDS))
    positive_count = len(words.intersection(POSITIVE_WORDS))
    
    if negative_count > positive_count:
        return "negative"
    elif positive_count > negative_count:
        return "positive"
    else:
        return "neutral"

def optimize_for_voice(text: str, max_length: int = 200) -> str:
    """Optimize text for faster voice response by shortening and making more conversational"""
    if len(text) <= max_length:
        return text
    
    # Split into sentences and take the most important ones
    sentences = text.split('. ')
    if len(sentences) <= 2:
        return text[:max_length] + "..."
    
    # Take first 2 sentences and truncate if needed
    optimized = '. '.join(sentences[:2])
    if len(optimized) > max_length:
        optimized = optimized[:max_length-3] + "..."
    
    return optimized



@api.route("/", methods=["GET"])
def home():
    now = datetime.now()
    timestamp = str(now.hour) + ":" + str(now.minute)
    
    # Get language parameter from query string, default to 'en'
    language = request.args.get('language', 'en')
    welcome_message = get_welcome_message(language)
    
    return render_template("chat.html", timestamp=timestamp, welcome_message=welcome_message, language=language)





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

def detect_language_from_text(text: str) -> str:
    """Enhanced language detection from text for auto-detection"""
    text_lower = text.lower()
    
    # Check for specific language words first (more accurate)
    language_indicators = {
        'hi': ['है', 'हूं', 'हैं', 'मैं', 'आप', 'कैसे', 'क्या', 'हैं', 'में', 'को', 'से', 'पर', 'के', 'का', 'की', 'हो', 'था', 'थी', 'थे'],
        'bn': ['আমি', 'আপনি', 'কিভাবে', 'কি', 'হয়', 'এবং', 'বা', 'কিন্তু', 'যদি', 'তবে', 'হয়তো', 'নাকি', 'কেন', 'কখন', 'কোথায়'],
        'ta': ['நான்', 'நீங்கள்', 'எப்படி', 'என்ன', 'ஆக', 'மற்றும்', 'அல்லது', 'ஆனால்', 'என்றால்', 'பின்னர்', 'ஒருவேளை', 'ஏன்', 'எப்போது', 'எங்கே'],
        'te': ['నేను', 'మీరు', 'ఎలా', 'ఏమి', 'అవుతుంది', 'మరియు', 'లేదా', 'కానీ', 'అయితే', 'అప్పుడు', 'బహుశా', 'ఎందుకు', 'ఎప్పుడు', 'ఎక్కడ'],
        'gu': ['હું', 'તમે', 'કેવી રીતે', 'શું', 'છે', 'અને', 'અથવા', 'પરંતુ', 'જો', 'તો', 'કદાચ', 'શા માટે', 'ક્યારે', 'ક્યાં'],
        'pa': ['ਮੈਂ', 'ਤੁਸੀਂ', 'ਕਿਵੇਂ', 'ਕੀ', 'ਹੈ', 'ਅਤੇ', 'ਜਾਂ', 'ਪਰ', 'ਜੇ', 'ਤਾਂ', 'ਸ਼ਾਇਦ', 'ਕਿਉਂ', 'ਕਦੋਂ', 'ਕਿੱਥੇ'],
        'kn': ['ನಾನು', 'ನೀವು', 'ಹೇಗೆ', 'ಏನು', 'ಆಗುತ್ತದೆ', 'ಮತ್ತು', 'ಅಥವಾ', 'ಆದರೆ', 'ಒಂದು ವೇಳೆ', 'ನಂತರ', 'ಬಹುಶಃ', 'ಏಕೆ', 'ಯಾವಾಗ', 'ಎಲ್ಲಿ'],
        'ml': ['ഞാൻ', 'നിങ്ങൾ', 'എങ്ങനെ', 'എന്ത്', 'ആകുന്നു', 'ഒപ്പം', 'അല്ലെങ്കിൽ', 'പക്ഷേ', 'എങ്കിൽ', 'പിന്നെ', 'ഒരുപക്ഷേ', 'എന്തുകൊണ്ട്', 'എപ്പോൾ', 'എവിടെ'],
        'ur': ['میں', 'آپ', 'کیسے', 'کیا', 'ہے', 'اور', 'یا', 'لیکن', 'اگر', 'تو', 'شاید', 'کیوں', 'کب', 'کہاں'],
        'es': ['hola', 'gracias', 'por favor', 'sí', 'no', 'buenos', 'días', 'noche', 'cómo', 'estás', 'soy', 'tengo', 'quiero', 'necesito', 'ayuda'],
        'fr': ['bonjour', 'merci', 's\'il vous plaît', 'oui', 'non', 'comment', 'allez-vous', 'je suis', 'j\'ai', 'je veux', 'j\'ai besoin', 'aide'],
        'de': ['hallo', 'danke', 'bitte', 'ja', 'nein', 'wie', 'geht', 'es', 'ich bin', 'ich habe', 'ich will', 'ich brauche', 'hilfe'],
        'it': ['ciao', 'grazie', 'per favore', 'sì', 'no', 'come', 'stai', 'sono', 'ho', 'voglio', 'ho bisogno', 'aiuto'],
        'pt': ['olá', 'obrigado', 'por favor', 'sim', 'não', 'como', 'está', 'sou', 'tenho', 'quero', 'preciso', 'ajuda'],
        'ru': ['привет', 'спасибо', 'пожалуйста', 'да', 'нет', 'как', 'дела', 'я', 'у меня', 'хочу', 'нужно', 'помощь'],
        'ja': ['こんにちは', 'ありがとう', 'お願いします', 'はい', 'いいえ', 'どう', 'です', '私は', '持っています', '欲しい', '必要', '助け'],
        'ko': ['안녕하세요', '감사합니다', '부탁드립니다', '네', '아니요', '어떻게', '입니다', '저는', '가지고', '원해요', '필요해요', '도움'],
        'zh': ['你好', '谢谢', '请', '是', '不', '怎么', '是', '我', '有', '想要', '需要', '帮助'],
        'ar': ['مرحبا', 'شكرا', 'من فضلك', 'نعم', 'لا', 'كيف', 'هو', 'أنا', 'لدي', 'أريد', 'أحتاج', 'مساعدة']
    }
    
    # Check for language indicators
    for lang_code, indicators in language_indicators.items():
        if any(indicator in text_lower for indicator in indicators):
            return lang_code
    
    # Fallback to script-based detection
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
    else:
        return 'en'  # Default to English

def get_gemini_response(query: str, messages: list) -> str:
    """Optimized Gemini response generation with faster processing"""
    # Configure on demand so updated .env is respected even after reloads
    api_key = Config.GEMINI_KEY or os.getenv("GEMINI_KEY")
    if not api_key:
        return "I apologize, but the Gemini API key is not configured. Please set GEMINI_KEY to use Google Gemini."
    
    try:
        genai.configure(api_key=api_key)
        
        # Optimized system prompt for faster processing
        system_prefix = (
            "You are AUDEXA, a compassionate mental health AI assistant. "
            "Provide helpful, evidence-based guidance. Be warm and supportive."
        )
        
        # Build conversation history more efficiently
        history_parts = []
        for m in messages[-3:]:  # Only use last 3 messages for faster processing
            role = m.get("role")
            content = m.get("content")
            if role and content:
                history_parts.append(f"{role.upper()}: {content}")
        
        history_text = "\n".join(history_parts) if history_parts else ""
        full_prompt = f"{system_prefix}\n\n{history_text}\n\nUSER: {query}\nASSISTANT:"

        # Use working model configuration
        model = genai.GenerativeModel("gemini-2.0-flash")
        result = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1000,  # Limit response length for faster processing
                temperature=0.7,
                top_p=0.8,
                top_k=40
            )
        )
        
        response_text = getattr(result, "text", "") or ""
        print(f"✅ Gemini response generated successfully ({len(response_text)} chars)")
        return response_text
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Gemini API error: {error_msg}")
        
        # Optimized error handling with specific messages
        if "quota" in error_msg.lower() or "429" in error_msg or "ResourceExhausted" in error_msg:
            return "I'm currently experiencing high demand and my AI quota has been reached for today. I'm still here to help with my fallback responses! What's on your mind?"
        elif "api key" in error_msg.lower() or "authentication" in error_msg.lower() or "expired" in error_msg.lower():
            return "I'm having trouble with my AI service right now. Let me help you with my built-in responses instead!"
        else:
            return "I'm experiencing some technical difficulties with my AI service. I'm still here to help with my fallback responses! What can I assist you with?"




examples = [
    # Negative emotions and distress
    Example("I'm feeling really down today", "negative"),
    Example("I'm struggling to find motivation", "negative"),
    Example("I've been feeling anxious lately", "negative"),
    Example("I'm finding it hard to sleep at night", "negative"),
    Example("I'm feeling overwhelmed with stress", "negative"),
    Example("I'm feeling depressed", "negative"),
    Example("I'm having panic attacks", "negative"),
    Example("I'm feeling suicidal", "negative"),
    Example("I'm in pain", "negative"),
    Example("I'm feeling hopeless", "negative"),
    Example("I'm having trouble eating", "negative"),
    Example("I'm feeling lonely", "negative"),
    Example("I'm scared about my health", "negative"),
    Example("I'm worried about my future", "negative"),
    Example("I'm feeling angry all the time", "negative"),
    
    # Positive emotions and progress
    Example("I practiced mindfulness and felt better", "positive"),
    Example("I talked to a friend and it helped", "positive"),
    Example("I enjoyed spending time in nature", "positive"),
    Example("I accomplished a small goal today", "positive"),
    Example("I'm grateful for the support I have", "positive"),
    Example("I'm feeling hopeful", "positive"),
    Example("I'm making progress", "positive"),
    Example("I'm feeling stronger", "positive"),
    Example("I'm taking care of myself", "positive"),
    Example("I'm feeling calm", "positive"),
    Example("I'm feeling confident", "positive"),
    Example("I'm feeling happy", "positive"),
    Example("I'm feeling peaceful", "positive"),
    Example("I'm feeling motivated", "positive"),
    Example("I'm feeling proud of myself", "positive"),
    
    # Neutral/informational
    Example("I'm taking things one step at a time", "neutral"),
    Example("I'm working on managing my emotions", "neutral"),
    Example("I'm exploring different coping strategies", "neutral"),
    Example("I'm learning to prioritize self-care", "neutral"),
    Example("I'm seeking professional help to improve", "neutral"),
    Example("What are some relaxation techniques?", "neutral"),
    Example("How can I improve my sleep?", "neutral"),
    Example("What should I do about my symptoms?", "neutral"),
    Example("Can you explain this condition?", "neutral"),
    Example("What are the treatment options?", "neutral"),
    Example("How long will recovery take?", "neutral"),
    Example("What are the side effects?", "neutral"),
    Example("Should I see a doctor?", "neutral"),
    Example("What tests do I need?", "neutral"),
    Example("How can I prevent this?", "neutral"),
]

@api.route("/response")
def response():
    query = request.args.get("msg")
    questions = request.args.get("questions")
    answers = request.args.get("answers")
    lang = request.args.get("lang", "auto")

    questions = questions.split("|")[:-2]
    answers = answers.split("|")[:-1]

    messages = [
        {
            "role": "system",
            "content": "You are a compassionate medical chatbot here to provide support and accurate advice for health concerns. Your main goal is to offer helpful advice to users seeking assistance with their medical queries. If urgent or severe, advise seeking immediate medical help. Remember, your name is AUDEXA. Now, please answer my question:",
        }
    ]
    for question, answer in zip(questions, answers):
        messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": answer})

    # Get the user's message
    user_message = query

    # Optimized sentiment analysis - try Cohere first, fallback to fast analysis
    sentiment_label = "neutral"
    
    if cohere_client:
        try:
            # Use Cohere for more accurate sentiment analysis
            sentiment_response = cohere_client.classify(inputs=[user_message], examples=examples)
            classification_result = sentiment_response[0]
            sentiment_prediction = classification_result.prediction
            sentiment_confidence = classification_result.confidence
            
            # Use prediction if confidence is high enough
            if sentiment_confidence > 0.3:
                if "positive" in sentiment_prediction.lower():
                    sentiment_label = "positive"
                elif "negative" in sentiment_prediction.lower():
                    sentiment_label = "negative"
                else:
                    sentiment_label = "neutral"
                print(f"✅ Cohere sentiment: {sentiment_label} (confidence: {sentiment_confidence:.2f})")
            else:
                # Low confidence, use fast fallback
                sentiment_label = analyze_sentiment_fast(user_message)
                print(f"⚠️ Low Cohere confidence, using fast analysis: {sentiment_label}")
                
        except Exception as e:
            # Cohere failed, use fast fallback
            sentiment_label = analyze_sentiment_fast(user_message)
            print(f"⚠️ Cohere failed ({e}), using fast analysis: {sentiment_label}")
    else:
        # No Cohere client, use fast analysis
        sentiment_label = analyze_sentiment_fast(user_message)
        print(f"⚡ Fast sentiment analysis: {sentiment_label}")

    # Get Gemini response
    answer = ""
    print(f"User query: {query}")
    
    try:
        print("Attempting Gemini response...")
        lang_note = ""
        # Enhanced language mapping for better AI understanding
        lang_map = {
            'en': 'English',
            'hi': 'Hindi (हिन्दी)',
            'bn': 'Bengali (বাংলা)',
            'ta': 'Tamil (தமிழ்)',
            'te': 'Telugu (తెలుగు)',
            'mr': 'Marathi (मराठी)',
            'gu': 'Gujarati (ગુજરાતી)',
            'pa': 'Punjabi (ਪੰਜਾਬੀ)',
            'kn': 'Kannada (ಕನ್ನಡ)',
            'ml': 'Malayalam (മലയാളം)',
            'ur': 'Urdu (اردو)',
            'es': 'Spanish (Español)',
            'fr': 'French (Français)',
            'de': 'German (Deutsch)',
            'it': 'Italian (Italiano)',
            'pt': 'Portuguese (Português)',
            'ru': 'Russian (Русский)',
            'ja': 'Japanese (日本語)',
            'ko': 'Korean (한국어)',
            'zh': 'Chinese (中文)',
            'ar': 'Arabic (العربية)'
        }
        
        if lang and lang != "auto":
            lang_name = lang_map.get(lang, lang)
            lang_note = f" IMPORTANT: Respond ONLY in {lang_name}. Do not use English. Keep your response to 2-3 sentences maximum, be warm and conversational, and always end with a follow-up question or encouragement in {lang_name}."
        else:
            # Auto-detect language from the query
            detected_lang = detect_language_from_text(query)
            print(f"Auto-detected language: {detected_lang}")
            if detected_lang != 'en':
                lang_name = lang_map.get(detected_lang, detected_lang)
                lang_note = f" IMPORTANT: I detected this message is in {lang_name}. Respond ONLY in {lang_name}. Do not use English. Keep your response to 2-3 sentences maximum, be warm and conversational, and always end with a follow-up question or encouragement in {lang_name}."
            else:
                lang_note = " Respond in English. Keep your response to 2-3 sentences maximum, be warm and conversational, and always end with a follow-up question or encouragement."
        
        answer = get_gemini_response(query + lang_note, messages)
    except Exception as e:
        print(f"AI model failed: {e}")
        # Use fallback response when AI models fail
        answer = get_fallback_response(query)
    
    # If we still don't have an answer, use fallback
    if not answer or "error" in answer.lower() or "unable" in answer.lower() or "quota" in answer.lower() or "credit" in answer.lower():
        print("Using fallback response due to AI model issues")
        answer = get_fallback_response(query)
    
    # Optimize answer for voice response if needed
    voice_optimized_answer = optimize_for_voice(answer) if answer else ""
    
    print(f"Final answer length: {len(answer) if answer else 0}")
    print(f"Voice optimized length: {len(voice_optimized_answer)}")
    print(f"Answer preview: {answer[:100] if answer else 'None'}...")

    # Create a popup message based on sentiment
    if sentiment_label == "positive":
        popup_message = f"🎉 I can sense you're feeling good today! I'll keep the positive energy flowing and offer encouragement to maintain your great mood."
    elif sentiment_label == "negative":
        popup_message = f"💙 I notice you might be going through a tough time. I'm here with extra care and support to help you feel better."
    else:
        popup_message = f"ℹ️ I'm here to help with whatever you need. Let's work together on your health and wellness goals."
    
    # Add fallback system notification if AI models are unavailable
    if "error" in answer.lower() or "unable" in answer.lower() or "quota" in answer.lower() or "credit" in answer.lower():
        popup_message += "\n\n⚠️ Note: AI models are currently unavailable. You're receiving responses from AUDEXA's fallback system with pre-programmed medical guidance."

    return {
        "answer": answer,
        "voice_answer": voice_optimized_answer,  # Optimized version for voice
        "popup_message": popup_message,
        "sentiment": sentiment_label
    }




@api.route("/test_mic", methods=["GET"])
def test_mic():
    """Simple endpoint to test if the server can receive audio"""
    return "Microphone test endpoint is working. Try recording some audio."

@api.route("/voice", methods=["POST"])
def voice():
    # Lazy import to avoid heavy dependency at app startup
    try:
        import whisper  # type: ignore
    except ImportError:
        return "Speech-to-text is unavailable: whisper is not installed on the server."

    try:
        DEVICE = "cpu"
        
        # Check if audio file is provided
        if "audio_data" not in request.files:
            return "No audio file provided"
            
        f = request.files["audio_data"]
        if f.filename == "":
            return "No audio file selected"
        
        # Save the audio file with a unique name
        import os
        import time
        audio_filename = f"audio_{int(time.time())}.webm"
        f.save(audio_filename)
        
        # Check file size and content
        file_size = os.path.getsize(audio_filename)
        print(f"Audio file saved: {audio_filename}, size: {file_size} bytes")
        
        if file_size < 800:  # Less than ~0.8KB
            print("Warning: Audio file seems too small, might be empty or corrupted")
            return "Audio recording too short or empty. Please speak clearly for at least 2-3 seconds and ensure your microphone is working."
        
        # Convert audio to WAV for better Whisper compatibility
        try:
            from pydub import AudioSegment
            print(f"Converting {audio_filename} to WAV format...")
            
            # Detect file format from extension
            file_extension = audio_filename.split('.')[-1].lower()
            if file_extension in ['webm', 'mp4', 'm4a', 'ogg']:
                audio = AudioSegment.from_file(audio_filename, format=file_extension)
            else:
                # Try to auto-detect format
                audio = AudioSegment.from_file(audio_filename)
            
            # Analyze audio properties
            print(f"Audio duration: {len(audio)}ms")
            print(f"Audio frame rate: {audio.frame_rate}Hz")
            print(f"Audio channels: {audio.channels}")
            print(f"Audio sample width: {audio.sample_width} bytes")
            print(f"Audio volume: {audio.dBFS:.1f} dBFS")
            
            # Check if audio is too short
            if len(audio) < 700:  # Less than ~0.7 second
                print("Audio too short for reliable transcription")
                return "Audio recording too short. Please speak for at least 2-3 seconds."
            
            # Check if audio is too quiet (likely silence) - adjusted threshold
            if audio.dBFS < -70 or audio.dBFS == float('-inf'):
                print("Audio too quiet or no audio detected")
                return "No speech detected. Please check:\n1. Microphone permissions are granted\n2. Microphone is not muted\n3. Speak louder and closer to microphone\n4. Try using the 'Browser STT' button instead"
            
            # Normalize audio volume if it's too quiet - more aggressive normalization
            if audio.dBFS < -35:
                print(f"Audio is quiet ({audio.dBFS:.1f} dBFS), normalizing...")
                # More aggressive volume boost for quiet audio
                volume_boost = min(45, max(25, -audio.dBFS - 15))  # Dynamic boost based on current volume
                audio = audio + volume_boost
                print(f"Applied {volume_boost}dB boost, new volume: {audio.dBFS:.1f} dBFS")
            
            wav_filename = audio_filename.rsplit('.', 1)[0] + '.wav'
            audio.export(wav_filename, format="wav", parameters=["-ar", "16000", "-ac", "1"])
            print(f"Converted to {wav_filename}")
            
            # Use the WAV file for transcription
            audio_filename = wav_filename
        except Exception as conversion_error:
            print(f"Audio conversion failed: Decoding failed. ffmpeg returned error code: 3199971767")
            print(f"Output from ffmpeg/avlib:\n{conversion_error}")
            # Check if it's a file format issue
            if "Invalid data" in str(conversion_error) or "EBML header parsing failed" in str(conversion_error):
                return "Audio file appears to be corrupted. Please try recording again with a clear voice."
            # Continue with original file if conversion fails
        
        # Try to load whisper model
        model = whisper.load_model("base", device=DEVICE)
        print("Whisper model loaded successfully")
        
        # Initialize transcribed_text variable
        transcribed_text = ""
        
        # Try to transcribe the audio with FFmpeg workaround
        try:
            # First try normal transcription with optimized parameters for quiet audio
            print("Attempting normal transcription...")
            # Enhanced language support for speech-to-text
            lang = request.form.get("language", "auto")
            
            # Language mapping for Whisper (more comprehensive)
            whisper_lang_map = {
                'hi': 'hi',      # Hindi
                'bn': 'bn',      # Bengali
                'ta': 'ta',      # Tamil
                'te': 'te',      # Telugu
                'gu': 'gu',      # Gujarati
                'pa': 'pa',      # Punjabi
                'kn': 'kn',      # Kannada
                'ml': 'ml',      # Malayalam
                'ur': 'ur',      # Urdu
                'zh': 'zh',      # Chinese
                'ja': 'ja',      # Japanese
                'ko': 'ko',      # Korean
                'ru': 'ru',      # Russian
                'es': 'es',      # Spanish
                'fr': 'fr',      # French
                'de': 'de',      # German
                'it': 'it',      # Italian
                'pt': 'pt',      # Portuguese
                'ar': 'ar',      # Arabic
                'en': 'en'       # English
            }
            
            # Get the appropriate language code for Whisper
            if lang == "auto":
                # For auto-detection, let Whisper handle it
                whisper_lang = None
                print("Using Whisper auto-detection for language")
            else:
                whisper_lang = whisper_lang_map.get(lang, lang)
                print(f"Using specified language for Whisper: {whisper_lang}")
            
            print(f"Language parameter: {lang}, Whisper language: {whisper_lang if whisper_lang else 'auto-detect'}")
            
            task_kwargs = {
                "language": whisper_lang,
                "task": "transcribe",
                "verbose": True,
                "condition_on_previous_text": False,
                "temperature": 0.0,
                "compression_ratio_threshold": 2.4,
                "logprob_threshold": -1.0,
                "no_speech_threshold": 0.3  # More lenient for multilingual speech
            }
            result = model.transcribe(
                audio_filename,
                **task_kwargs
            )
            print(f"Transcription result type: {type(result)}")
            print(f"Transcription result keys: {result.keys() if hasattr(result, 'keys') else 'No keys'}")
            print(f"Transcription result: {result}")
            transcribed_text = result.get("text", "")
            print(f"Transcription successful: {transcribed_text[:50] if transcribed_text else 'Empty text'}...")
        except Exception as transcribe_error:
            print(f"Normal transcription failed: {transcribe_error}")
            # If FFmpeg is missing, try to work around it
            if "FileNotFoundError" in str(transcribe_error) or "WinError 2" in str(transcribe_error):
                try:
                    print("Trying librosa fallback...")
                    # Try to use whisper with a different approach
                    import numpy as np
                    import librosa
                    
                    # Load audio with librosa instead of FFmpeg
                    audio_data, sr = librosa.load(audio_filename, sr=16000)
                    print(f"Audio loaded with librosa: {len(audio_data)} samples at {sr}Hz")
                    result = model.transcribe(audio_data)
                    print(f"Librosa result type: {type(result)}")
                    print(f"Librosa result keys: {result.keys() if hasattr(result, 'keys') else 'No keys'}")
                    print(f"Librosa result: {result}")
                    transcribed_text = result.get("text", "")
                    print(f"Librosa transcription successful: {transcribed_text[:50] if transcribed_text else 'Empty text'}...")
                except Exception as librosa_error:
                    print(f"Librosa fallback failed: {librosa_error}")
                    return "Speech-to-text is temporarily unavailable: Audio processing tools are not properly installed. Please use text input for now."
            else:
                return f"Speech-to-text error: {str(transcribe_error)}"
        
        # Clean up the temporary files
        # Find the original file by looking for files with the same base name
        base_name = audio_filename.rsplit('.', 1)[0]
        original_extensions = ['webm', 'mp4', 'm4a', 'ogg']
        
        for ext in original_extensions:
            original_filename = f"{base_name}.{ext}"
            if os.path.exists(original_filename):
                os.remove(original_filename)
                print(f"Cleaned up original file: {original_filename}")
                break
        
        if os.path.exists(audio_filename):
            os.remove(audio_filename)
            print(f"Cleaned up audio file: {audio_filename}")
        
        # Check if we got any transcription
        if not transcribed_text or transcribed_text.strip() == "":
            print("No transcription text received from WAV file, trying original audio...")
            
            # Try with original audio file as fallback
            try:
                original_file = None
                for ext in ['webm', 'mp4', 'm4a', 'ogg']:
                    test_file = f"{base_name}.{ext}"
                    if os.path.exists(test_file):
                        original_file = test_file
                        break
                
                if original_file:
                    print(f"Trying transcription with original file: {original_file}")
                    result = model.transcribe(original_file, **task_kwargs)
                    transcribed_text = result.get("text", "")
                    print(f"Original file transcription: {transcribed_text[:50] if transcribed_text else 'Empty text'}...")
            except Exception as fallback_error:
                print(f"Fallback transcription failed: {fallback_error}")
        
        # Final check
        if not transcribed_text or transcribed_text.strip() == "":
            print("No transcription text received from any method")
            
            # Try one more time with different parameters and multiple language attempts
            try:
                print("Trying final transcription attempt with different parameters...")
                
                # Try with auto-detection first
                result = model.transcribe(
                    audio_filename,
                    language=None,  # Let Whisper auto-detect
                    task="transcribe",
                    verbose=False,
                    condition_on_previous_text=False,
                    temperature=0.0,
                    compression_ratio_threshold=2.4,
                    logprob_threshold=-1.0,
                    no_speech_threshold=0.3  # More lenient threshold
                )
                transcribed_text = result.get("text", "").strip()
                print(f"Auto-detect transcription: {transcribed_text[:50] if transcribed_text else 'Empty text'}...")
                
                # If still no text, try with common languages
                if not transcribed_text:
                    print("Trying with common languages...")
                    common_languages = ['hi', 'en', 'es', 'fr', 'de', 'zh', 'ja', 'ko', 'ar', 'ru']
                    for lang_code in common_languages:
                        try:
                            result = model.transcribe(
                                audio_filename,
                                language=lang_code,
                                task="transcribe",
                                verbose=False,
                                condition_on_previous_text=False,
                                temperature=0.0,
                                compression_ratio_threshold=2.4,
                                logprob_threshold=-1.0,
                                no_speech_threshold=0.3
                            )
                            temp_text = result.get("text", "").strip()
                            if temp_text:
                                transcribed_text = temp_text
                                print(f"Found text with language {lang_code}: {transcribed_text[:50]}...")
                                break
                        except Exception as lang_error:
                            print(f"Failed with language {lang_code}: {lang_error}")
                            continue
                
                print(f"Final attempt transcription: {transcribed_text[:50] if transcribed_text else 'Empty text'}...")
            except Exception as final_error:
                print(f"Final transcription attempt failed: {final_error}")
            
            # If still no text, return a more helpful message
            if not transcribed_text or transcribed_text.strip() == "":
                return "I couldn't detect any speech in your recording. Please try:\n1. Speaking more clearly and loudly\n2. Recording for at least 3-5 seconds\n3. Checking your microphone permissions\n4. Speaking closer to your microphone\n5. Using the text input instead"
        
        print(f"Final transcription: '{transcribed_text}'")
        return transcribed_text.strip()
        
    except Exception as e:
        print(f"Voice route error: {e}")
        return f"Speech-to-text error: {str(e)}"


@api.route("/text_to_speech", methods=["POST"])
def text_to_speech():
    """Optimized text-to-speech with faster response times"""
    try:
        from flask import jsonify, send_file
        import tempfile
        import os
        import time
        
        start_time = time.time()
        
        # Get text from request
        data = request.get_json()
        text = data.get('text', '')
        language = data.get('language', 'en')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Optimized language mapping for TTS
        language_map = {
            'hi': 'hi', 'bn': 'bn', 'ta': 'ta', 'te': 'te', 'gu': 'gu', 'pa': 'pa',
            'kn': 'kn', 'ml': 'ml', 'ur': 'ur', 'zh': 'zh', 'ja': 'ja', 'ko': 'ko',
            'ru': 'ru', 'es': 'es', 'fr': 'fr', 'de': 'de', 'it': 'it', 'pt': 'pt',
            'ar': 'ar', 'en': 'en'
        }
        
        tts_lang = language_map.get(language, 'en')
        
        # For faster response, limit text length and use browser TTS for long texts
        if len(text) > 200:
            print(f"⚡ Long text detected ({len(text)} chars), using browser TTS for speed")
            return jsonify({
                "text": text,
                "language": tts_lang,
                "use_browser_tts": True,
                "message": f"Using browser TTS for faster response in {tts_lang}"
            })
        
        # Try optimized gTTS with faster settings
        try:
            from gtts import gTTS
            
            # Create TTS with optimized settings for speed
            tts = gTTS(
                text=text, 
                lang=tts_lang, 
                slow=False,  # Fast speech
                tld='com'    # Use faster server
            )
            
            # Create temporary file with optimized settings
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.close()
            
            # Save audio to temporary file
            tts.save(temp_file.name)
            
            generation_time = time.time() - start_time
            print(f"⚡ TTS generated in {generation_time:.2f}s for {tts_lang}: {text[:30]}...")
            
            # Return the audio file
            return send_file(
                temp_file.name,
                as_attachment=True,
                download_name=f'response_{tts_lang}.mp3',
                mimetype='audio/mpeg'
            )
            
        except ImportError:
            # Fallback: return text for browser TTS
            return jsonify({
                "text": text,
                "language": tts_lang,
                "use_browser_tts": True,
                "message": f"Server TTS not available, using browser TTS in {tts_lang}"
            })
        except Exception as tts_error:
            print(f"⚠️ TTS error for {tts_lang}: {tts_error}")
            # Fast fallback to English
            try:
                tts = gTTS(text=text, lang='en', slow=False, tld='com')
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                temp_file.close()
                tts.save(temp_file.name)
                
                generation_time = time.time() - start_time
                print(f"⚡ Fallback TTS in {generation_time:.2f}s: {text[:30]}...")
                
                return send_file(
                    temp_file.name,
                    as_attachment=True,
                    download_name='response_en.mp3',
                    mimetype='audio/mpeg'
                )
            except Exception as fallback_error:
                print(f"❌ Fallback TTS failed: {fallback_error}")
                return jsonify({
                    "text": text,
                    "language": "en",
                    "use_browser_tts": True,
                    "message": "TTS not available, using browser TTS"
                })
            
    except Exception as e:
        print(f"TTS error: {e}")
        return jsonify({"error": f"Text-to-speech error: {str(e)}"}), 500


def get_response(query: str, messages: list) -> str:
    # Backward compatibility wrapper: always use Gemini now
    return get_gemini_response(query, messages)


def get_fallback_response(query: str) -> str:
    """
    Enhanced fallback rule-based chatbot when AI models are unavailable.
    Provides comprehensive mental health guidance, prevention strategies, and support.
    """
    query_lower = query.lower()
    
    # Mental health responses with prevention strategies
    if any(word in query_lower for word in ['anxious', 'anxiety', 'worried', 'stress', 'stressed']):
        return """😰 **ANXIETY GUIDE** 😰

**STEP 1: QUICK CALMING**
• 4-7-8 Breathing: Inhale 4, hold 7, exhale 8
• 5-4-3-2-1 Grounding: 5 things you see, 4 touch, 3 hear
• Progressive Relaxation: Tense then relax muscles
• Butterfly Hug: Cross arms, tap shoulders

**STEP 2: DAILY PREVENTION**
• Morning meditation (10 min)
• Daily exercise (30 min)
• Regular sleep schedule
• Set boundaries, say "no"
• Take breaks from screens
• Stay hydrated, eat regularly
• Limit caffeine & alcohol

**STEP 3: COGNITIVE TECHNIQUES**
• Challenge negative thoughts
• Practice gratitude journaling
• Break tasks into small steps
• Use time management tools

**STEP 4: GET HELP IF**
• Symptoms last 2+ weeks
• Affects daily activities
• Physical symptoms
• Thoughts of self-harm

**Crisis: 988 | Text: HOME to 741741 | Emergency: 911**"""

    elif any(word in query_lower for word in ['sad', 'depressed', 'down', 'hopeless', 'lonely']):
        return """😔 **DEPRESSION GUIDE** 😔

**STEP 1: IMMEDIATE HELP**
• Reach out to someone you trust
• Self-care: bath, music, enjoyable activities
• Keep basic daily routine
• Gentle movement (10-min walk)
• Mindfulness breathing (5 min)

**STEP 2: DAILY PRACTICES**
• Morning gratitude (3 things thankful for)
• Daily exercise (30 min total)
• Consistent sleep (7-9 hours)
• Regular meals (limit processed foods)
• Mood tracking journal

**STEP 3: COGNITIVE TECHNIQUES**
• Challenge negative thoughts
• Practice self-compassion
• Set small daily goals
• Break tasks into steps

**STEP 4: GET HELP IF**
• Thoughts of self-harm
• Severe symptoms
• Lasts 2+ weeks
• Can't care for self

**Crisis: 988 | Text: HOME to 741741 | Emergency: 911**"""

    elif any(word in query_lower for word in ['sleep', 'insomnia', 'tired', 'exhausted']):
        return """🌙 **SLEEP GUIDE** 🌙

**STEP 1: QUICK FIXES**
• 4-7-8 Breathing: Inhale 4, hold 7, exhale 8
• Progressive Relaxation: Tense then relax muscles
• Grounding: 5 things you see, 4 you touch, 3 you hear

**STEP 2: DAILY RULES**
• Same bedtime & wake time daily
• 7-9 hours sleep
• No screens 1 hour before bed
• Cool, dark, quiet room (65-68°F)
• Exercise daily (finish 3-4 hours before bed)
• No caffeine after 2 PM

**STEP 3: BEDTIME ROUTINE**
1. Warm bath/shower
2. Read physical book
3. Calming music
4. Gentle stretching
5. Write worries down
6. Dim lights

**STEP 4: GET HELP IF**
• Problems last 3+ weeks
• Excessive daytime sleepiness
• Sleep affects daily life
• Snoring/gasping/leg movements

**Professional Help:**
• Sleep specialist
• CBT-I therapy
• Sleep study
• Medication evaluation"""

    elif any(word in query_lower for word in ['pain', 'hurt', 'ache', 'sore']):
        return """I'm sorry you're experiencing pain. Here are some general guidelines:

1. **Immediate Relief**:
   - Rest the affected area
   - Apply ice for acute injuries (first 48 hours)
   - Apply heat for chronic pain or muscle tension
   - Gentle stretching if appropriate

2. **Pain Management**:
   - Over-the-counter pain relievers (follow dosage instructions)
   - Deep breathing exercises
   - Progressive muscle relaxation
   - Distraction techniques (reading, music, etc.)

3. **When to Seek Medical Attention**:
   - Severe or worsening pain
   - Pain accompanied by fever, swelling, or redness
   - Pain that interferes with daily activities
   - Pain that doesn't improve with rest

**Note**: This is general advice. For specific pain conditions, please consult a healthcare provider."""

    elif any(word in query_lower for word in ['exercise', 'workout', 'fitness', 'physical']):
        return """Great question about exercise! Here are some general guidelines:

1. **Getting Started**:
   - Start slowly and gradually increase intensity
   - Aim for 150 minutes of moderate exercise per week
   - Include both cardio and strength training
   - Listen to your body and don't overdo it

2. **Types of Exercise**:
   - **Cardio**: Walking, swimming, cycling, dancing
   - **Strength**: Bodyweight exercises, resistance bands, weights
   - **Flexibility**: Stretching, yoga, tai chi
   - **Balance**: Standing on one leg, heel-to-toe walking

3. **Safety Tips**:
   - Warm up before exercise
   - Stay hydrated
   - Stop if you feel pain or dizziness
   - Consult a doctor before starting if you have health concerns

4. **Motivation**:
   - Find activities you enjoy
   - Exercise with friends or family
   - Set realistic goals
   - Track your progress

Remember: Any movement is better than none! Start where you are and build from there."""

    elif any(word in query_lower for word in ['diet', 'nutrition', 'food', 'eating', 'healthy']):
        return """Here are some general nutrition guidelines for better health:

1. **Balanced Meals**:
   - Include protein, healthy fats, and complex carbohydrates
   - Fill half your plate with colorful vegetables and fruits
   - Choose whole grains over refined grains
   - Include lean protein sources

2. **Hydration**:
   - Drink water throughout the day
   - Aim for 8-10 glasses daily (more if active)
   - Limit sugary drinks and excessive caffeine

3. **Healthy Eating Habits**:
   - Eat slowly and mindfully
   - Listen to hunger and fullness cues
   - Plan meals ahead when possible
   - Cook at home more often

4. **Foods to Include**:
   - Leafy greens and colorful vegetables
   - Berries and other fruits
   - Nuts, seeds, and legumes
   - Fatty fish for omega-3s

5. **Foods to Limit**:
   - Processed foods and added sugars
   - Excessive salt and saturated fats
   - Refined carbohydrates

**Note**: Individual nutritional needs vary. For personalized advice, consider consulting a registered dietitian."""

    elif any(word in query_lower for word in ['headache', 'migraine', 'head pain']):
        return """Headaches can be really uncomfortable. Here are some strategies that might help:

1. **Immediate Relief**:
   - Rest in a quiet, dark room
   - Apply cold or warm compress to your head/neck
   - Gentle massage of temples and neck
   - Deep breathing exercises

2. **Lifestyle Factors**:
   - Stay hydrated throughout the day
   - Get adequate sleep
   - Manage stress levels
   - Take regular breaks from screen time
   - Maintain good posture

3. **When to Seek Medical Attention**:
   - Severe headache that's different from usual
   - Headache with fever, stiff neck, or confusion
   - Headache after head injury
   - Headache that worsens with movement
   - Headache with vision changes

4. **Prevention**:
   - Identify and avoid triggers (foods, stress, lack of sleep)
   - Regular exercise and relaxation techniques
   - Consistent sleep schedule
   - Regular meals to avoid low blood sugar

If headaches are frequent or severe, please consult a healthcare provider."""

    # Mental health prevention and wellness
    elif any(word in query_lower for word in ['mental health', 'prevention', 'wellness', 'coping', 'therapy', 'counseling']):
        return """Excellent question about mental health prevention and wellness! Let me provide you with comprehensive strategies to maintain and improve your mental well-being.

**MENTAL HEALTH PREVENTION STRATEGIES:**

1. **Daily Wellness Practices**:
   - **Morning Routine**: Start with 10 minutes of meditation, gratitude journaling, or gentle stretching
   - **Mindful Moments**: Take 3 deep breaths every hour, practice mindful eating, notice your surroundings
   - **Physical Activity**: Aim for 30 minutes of movement daily (walking, yoga, dancing, swimming)
   - **Sleep Hygiene**: Maintain consistent 7-9 hour sleep schedule, avoid screens before bed

2. **Stress Management Techniques**:
   - **Breathing Exercises**: 4-7-8 breathing, box breathing, or diaphragmatic breathing
   - **Progressive Muscle Relaxation**: Tense and release each muscle group systematically
   - **Mindfulness Meditation**: Start with 5-10 minutes daily, use apps like Headspace or Calm
   - **Time Management**: Prioritize tasks, learn to say no, set realistic expectations

3. **Emotional Regulation Skills**:
   - **Identify Triggers**: Keep a mood journal to recognize patterns
   - **Cognitive Reframing**: Challenge negative thoughts with evidence
   - **Self-Compassion**: Treat yourself with the kindness you'd offer a friend
   - **Emotional Expression**: Journal, talk to trusted others, or use creative outlets

4. **Social Connection Building**:
   - **Maintain Relationships**: Regular check-ins with friends and family
   - **Join Communities**: Clubs, groups, or online communities of shared interests
   - **Volunteer**: Helping others can improve your own mental well-being
   - **Professional Support**: Consider therapy for ongoing support and skill development

5. **Lifestyle Modifications**:
   - **Nutrition**: Eat regular, balanced meals, limit processed foods and sugar
   - **Hydration**: Drink adequate water throughout the day
   - **Limit Substances**: Reduce caffeine, alcohol, and avoid recreational drugs
   - **Screen Time**: Set boundaries for technology use, especially social media

**EARLY WARNING SIGNS TO MONITOR:**
- Changes in sleep patterns (too much or too little)
- Appetite changes or weight fluctuations
- Loss of interest in previously enjoyed activities
- Difficulty concentrating or making decisions
- Increased irritability or mood swings
- Physical symptoms without clear cause (headaches, stomach issues)
- Social withdrawal or isolation
- Feelings of hopelessness or worthlessness

**PREVENTION CHECKLIST:**
□ Practice daily stress management techniques
□ Maintain regular sleep schedule
□ Exercise regularly
□ Eat balanced meals
□ Stay connected with others
□ Practice gratitude and positive thinking
□ Set and maintain healthy boundaries
□ Seek help when needed
□ Learn and practice coping skills
□ Regular mental health check-ins

**WHEN TO SEEK PROFESSIONAL HELP:**
- Symptoms persist for more than 2 weeks
- Difficulty functioning in daily life
- Thoughts of self-harm or suicide
- Substance use to cope with emotions
- Relationship difficulties affecting mental health
- Trauma or significant life changes

**Professional Help Options:**
- Individual therapy (CBT, DBT, EMDR, etc.)
- Group therapy or support groups
- Psychiatry for medication evaluation
- Crisis intervention services
- Online therapy platforms

**Crisis Resources:**
- National Suicide Prevention Lifeline: 988 (24/7)
- Crisis Text Line: Text HOME to 741741
- Emergency: 911
- Local mental health crisis hotlines

**Remember**: Mental health prevention is an ongoing practice, not a one-time fix. Small, consistent actions build resilience over time. You're building a foundation for long-term mental well-being!"""

    # General health and wellness
    elif any(word in query_lower for word in ['health', 'wellness', 'well-being', 'healthy']):
        return """Your health is your greatest asset! Here's a comprehensive guide to maintaining and improving your overall well-being:

**PILLARS OF HEALTH:**

1. **Physical Health**:
   - **Exercise**: 150 minutes moderate activity weekly (walking, swimming, cycling)
   - **Strength Training**: 2-3 times per week (bodyweight exercises, weights)
   - **Flexibility**: Daily stretching or yoga
   - **Sleep**: 7-9 hours nightly, consistent schedule
   - **Nutrition**: Balanced meals, plenty of water, limit processed foods

2. **Mental Health**:
   - **Stress Management**: Meditation, deep breathing, time management
   - **Mental Stimulation**: Reading, puzzles, learning new skills
   - **Emotional Expression**: Journaling, talking with trusted people
   - **Professional Support**: Therapy when needed

3. **Social Health**:
   - **Meaningful Connections**: Regular contact with friends and family
   - **Community Involvement**: Volunteering, clubs, groups
   - **Healthy Boundaries**: Learn to say no, protect your energy
   - **Communication Skills**: Active listening, expressing needs

4. **Spiritual Health**:
   - **Purpose**: Identify your values and what gives life meaning
   - **Mindfulness**: Present-moment awareness, gratitude practice
   - **Nature Connection**: Spend time outdoors regularly
   - **Reflection**: Regular self-assessment and goal setting

**DAILY HEALTH HABITS:**
- Morning routine (hydration, movement, intention setting)
- Regular meal times with balanced nutrition
- Movement breaks throughout the day
- Evening wind-down routine
- Consistent sleep schedule

**PREVENTIVE CARE:**
- Annual physical exams
- Regular dental checkups
- Vision and hearing tests
- Mental health check-ins
- Vaccinations and screenings

**HEALTH MONITORING:**
- Track sleep patterns
- Monitor energy levels
- Notice mood changes
- Watch for physical symptoms
- Regular health assessments

**Remember**: Health is a journey, not a destination. Small, consistent actions compound over time to create significant improvements in your overall well-being!"""

    # PTSD and trauma responses
    elif any(word in query_lower for word in ['ptsd', 'trauma', 'flashback', 'nightmare', 'triggered', 'abuse', 'assault']):
        return """I'm so sorry you're dealing with trauma. You're incredibly brave for reaching out, and healing is absolutely possible. Here are some strategies that may help:

**IMMEDIATE COPING STRATEGIES:**

1. **Grounding Techniques**:
   - **5-4-3-2-1 Method**: 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste
   - **Box Breathing**: Inhale 4, hold 4, exhale 4, hold 4
   - **Temperature Change**: Hold ice cubes, splash cold water on face
   - **Progressive Muscle Relaxation**: Tense and release each muscle group

2. **Flashback Management**:
   - Remind yourself: "This is a memory, not happening now"
   - Use grounding techniques immediately
   - Focus on your current surroundings
   - Practice self-compassion and patience

3. **Nightmare Prevention**:
   - Establish calming bedtime routine
   - Avoid screens 1 hour before bed
   - Keep bedroom cool, dark, and comfortable
   - Practice relaxation techniques before sleep

**HEALING STRATEGIES:**

1. **Professional Support**:
   - **Trauma-Informed Therapy**: EMDR, CBT, DBT, or somatic therapy
   - **Support Groups**: Connect with others who understand
   - **Psychiatry**: Consider medication if recommended
   - **Crisis Support**: 24/7 helplines when needed

2. **Self-Care Practices**:
   - **Routine**: Maintain daily structure and predictability
   - **Physical Health**: Regular exercise, nutrition, sleep
   - **Creative Expression**: Art, music, writing, movement
   - **Nature Connection**: Spend time outdoors safely

3. **Safety Planning**:
   - Identify triggers and warning signs
   - Create coping strategies for each trigger
   - Build support network of trusted people
   - Develop emergency contact list

**IMPORTANT REMINDERS:**
- Healing takes time and is not linear
- You are not defined by your trauma
- It's okay to have difficult days
- Professional help is a sign of strength
- You deserve support and care

**Crisis Resources:**
- National Sexual Assault Hotline: 1-800-656-4673
- National Domestic Violence Hotline: 1-800-799-7233
- Crisis Text Line: Text HOME to 741741
- National Suicide Prevention Lifeline: 988
- Emergency: 911

**Remember**: You are not alone, and healing is possible. Take things one day at a time, and be gentle with yourself throughout this process."""

    # Default response for other queries
    else:
        return """Thanks for reaching out! I'm here to help with mental health, wellness, and general health questions. I can offer support with:

**MENTAL HEALTH TOPICS:**
- Anxiety and stress management
- Depression and mood support
- Sleep issues and insomnia
- Trauma and PTSD
- Grief and loss
- Relationship challenges
- Self-care and coping strategies

**PHYSICAL HEALTH TOPICS:**
- Exercise and fitness guidance
- Nutrition and healthy eating
- Pain management
- Headaches and migraines
- General wellness practices
- Preventive health measures

**WELLNESS STRATEGIES:**
- Mindfulness and meditation
- Breathing exercises
- Relaxation techniques
- Goal setting and motivation
- Habit formation
- Work-life balance

**HOW I CAN HELP:**
- Provide evidence-based information
- Offer practical coping strategies
- Suggest professional resources when needed
- Support your wellness journey
- Answer health-related questions

**IMPORTANT NOTE:**
While I can provide general health information and support, I'm not a replacement for professional medical or mental health care. For serious health concerns, please consult with qualified healthcare providers.

What specific area would you like to explore together? I'm here to provide guidance and support on your wellness journey!"""

# ListenAI Setup Guide

## Required API Keys

To run ListenAI properly, you need to set up the following API keys:

### 1. Google Gemini API Key
- Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
- Sign in with your Google account
- Click "Create API Key"
- Copy the generated API key

### 2. Cohere API Key (Optional - for sentiment analysis)
- Go to [Cohere](https://cohere.ai/)
- Sign up for an account
- Get your API key from the dashboard


## Setup Steps

### Step 1: Create .env file
Create a file named `.env` in the root directory with the following content:

```bash
# Flask Configuration
FLASK_DEBUG=True
FLASK_APP=app.py
FLASK_RUN_PORT=5000

# Google Gemini API Key (REQUIRED)
GEMINI_KEY=your_actual_gemini_api_key_here

# Cohere API Key (Optional)
COHERE_API_KEY=your_cohere_api_key_here

### Step 2: Replace placeholder values
- Replace `your_actual_gemini_api_key_here` with your real Gemini API key
- Replace other placeholder values if you have those services

### Step 3: Run the application
```bash
python app.py
```

## Important Notes

- **GEMINI_KEY is REQUIRED** - Without this, the AI chatbot will not work
- The .env file should never be committed to version control
- Keep your API keys secure and private
- Free tier limits may apply to some services

## Troubleshooting

If you see "Gemini API key is not configured" error:
1. Make sure you created the `.env` file
2. Check that the file is named exactly `.env` (not `.env.txt`)
3. Verify the API key is correct
4. Restart the application after making changes

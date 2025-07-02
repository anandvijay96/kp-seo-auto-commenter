import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold


# Configure Gemini API key (supports both GOOGLE_API_KEY and GEMINI_API_KEY)
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Google Gemini API key not set in environment.")

genai.configure(api_key=api_key)

# Set up the Gemini model for free tier
GEMINI_MODEL = "gemini-1.5-flash-latest"

def get_gemini_model():
    return genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        },
        system_instruction="You are a helpful AI assistant."
    )

def get_gemini_response(messages):
    try:
        model = get_gemini_model()
        response = model.generate_content(messages, stream=False)
        return response.text
    except Exception as e:
        return f"Gemini API error: {e}"

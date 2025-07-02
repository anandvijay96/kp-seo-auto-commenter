import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from app.core.config import settings

# Configure the Gemini client with the API key from settings
if not settings.GEMINI_API_KEY:
    raise ValueError("Google Gemini API key not set in environment.")

genai.configure(api_key=settings.GEMINI_API_KEY)

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

async def stream_gemini_response(messages: list):
    """
    Calls the Gemini API with streaming enabled and yields response chunks asynchronously.
    """
    try:
        model = get_gemini_model()
        # Use generate_content_async for asynchronous streaming
        response_stream = await model.generate_content_async(messages, stream=True)
        async for chunk in response_stream:
            # Ensure that we only yield non-empty text parts
            if chunk.text:
                yield chunk.text
    except Exception as e:
        # In case of an API error, yield a formatted error message
        yield f"Gemini API error: {e}"

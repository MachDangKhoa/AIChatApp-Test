"""
gemini_service.py
-----------------
Handles text-based conversations with Gemini and provides
a shared client configuration for other services (image, CSV).
"""

import google.generativeai as genai
from utils.config import GEMINI_API_KEY, GEMINI_MODEL

# ------------------------------------------------------------
# ✅ Configure Gemini Client (runs once globally)
# ------------------------------------------------------------
genai.configure(api_key=GEMINI_API_KEY)


def get_model():
    """
    Get a configured Gemini model instance.

    Returns:
        genai.GenerativeModel: Pre-configured Gemini model ready for inference.
    """
    return genai.GenerativeModel(GEMINI_MODEL)


# ============================================================
# 💬 TEXT CHAT — multi-turn or single-turn conversation
# ============================================================
def ask_gemini_text(messages: list[dict]) -> str:
    """
    Send a text prompt to Gemini and return the model's response.

    Args:
        prompt (str): User's message or query.

    Returns:
        str: Gemini's generated text response.
    """
    try:
        model = get_model()
        gemini_messages = [
            {"role": msg["role"], "parts": [{"text": msg["content"]}]}
            for msg in messages
        ]
        response = model.generate_content(gemini_messages)

        return response.text.strip() if response and response.text else "(No response from Gemini)"

    except Exception as e:
        print(f"[GeminiService] Text query failed: {e}")
        return f"❌ Error while generating text: {e}"


async def ask_gemini_text_streaming(messages: list[dict]) -> str:
    """
    Send a text prompt to Gemini and stream the model's response as chunks.

    Args:
        messages (list[dict]): List of messages for multi-turn conversation.

    Yields:
        str: Each chunk of the generated text from Gemini.
    """
    try:
        model = get_model()
        gemini_messages = [
            {"role": msg["role"], "parts": [{"text": msg["content"]}]}
            for msg in messages
        ]
        response = model.generate_content(gemini_messages, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text.strip()  # Yield each chunk
    except Exception as e:
        print(f"[GeminiService] Text streaming query failed: {e}")
        yield f"❌ Error while generating text: {e}"  # Yield error as chunk
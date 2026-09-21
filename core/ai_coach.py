"""
Growth OS - Socratic AI Sparring Coach Engine
Engages the student in rigorous guided dialogue without giving away solutions.
References: Groq and Gemini integrations from Jarvis.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load .env
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    JARVIS_ENV = Path(r"C:\Users\v\Desktop\Jarvis\.env")
    if JARVIS_ENV.exists():
        load_dotenv(JARVIS_ENV)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

SOCRATIC_SYSTEM_PROMPT = """You are an elite IIT-JEE Advanced Professor and Cognitive Mentor.
Your mission is to rigorously build the student's problem-solving intellect and intuition.

CRITICAL PEDAGOGICAL RULES:
1. NEVER provide the final numerical answer, direct formula substitution, or full algebraic derivation outright.
2. If the student shares a problem or image, diagnose their conceptual roadblock and ask 1 to 2 sharp, targeted guiding questions.
3. Guide them toward the fundamental physical principles (e.g., Conservation laws, Torque about Instantaneous Axis, Le Chatelier shifts, Symmetry arguments).
4. If their reasoning is flawed, construct a simple thought experiment or counter-case showing why that assumption fails.
5. Format mathematical expressions with clear LaTeX ($...$ or $$...$$).
6. Keep answers concise, direct, intellectually demanding, and encouraging."""

def chat_socratic_coach(messages: List[Dict[str, str]], image_path: Optional[str] = None) -> str:
    """
    Sends chat history to Gemini or Groq with strict Socratic coaching system prompt.
    """
    # 1. Try Gemini Vision if image is attached
    if image_path and Path(image_path).exists() and GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            from PIL import Image

            genai.configure(api_key=GEMINI_API_KEY)
            img = Image.open(image_path)

            user_query = messages[-1]["content"] if messages else "Analyze this problem."
            full_prompt = f"{SOCRATIC_SYSTEM_PROMPT}\n\nStudent asks: {user_query}"

            for m_name in ["gemini-2.5-flash", "gemini-1.5-flash"]:
                try:
                    model = genai.GenerativeModel(m_name)
                    response = model.generate_content([full_prompt, img])
                    if response and response.text:
                        return response.text.strip()
                except Exception:
                    continue
        except Exception as e:
            print(f"[AICoach] Gemini vision fallback: {e}")

    # 2. Try Groq (Ultra-fast LLM inference)
    if GROQ_API_KEY:
        try:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)

            groq_messages = [{"role": "system", "content": SOCRATIC_SYSTEM_PROMPT}]
            for msg in messages:
                groq_messages.append({"role": msg["role"], "content": msg["content"]})

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=groq_messages,
                temperature=0.6,
                max_tokens=800,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"[AICoach] Groq error, trying Gemini text: {e}")

    # 3. Fallback to Gemini Text
    if GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")

            conversation_text = f"{SOCRATIC_SYSTEM_PROMPT}\n\nConversation:\n"
            for msg in messages:
                conversation_text += f"{msg['role'].upper()}: {msg['content']}\n"
            conversation_text += "MENTOR:"

            response = model.generate_content(conversation_text)
            return response.text.strip()
        except Exception as e:
            return f"AI Mentor error: {e}"

    return "No API key configured. Please check your GEMINI_API_KEY or GROQ_API_KEY in .env."

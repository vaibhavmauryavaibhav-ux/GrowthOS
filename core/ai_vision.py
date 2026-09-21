"""
Growth OS - AI Vision & LaTeX Transcription Engine
Extracts mathematical problem text, LaTeX formulas, subject classification, and core solutions.
References: Gemini Vision multimodal integration from Jarvis.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
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

def analyze_snip_with_vision(image_path: Path) -> Dict[str, Any]:
    """
    Uses Gemini Multimodal Vision to inspect the snipped problem image,
    transcribe mathematical equations to LaTeX, and provide a high-yield solution.
    """
    if not image_path or not Path(image_path).exists():
        return {"error": "Image file not found"}

    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY not found in .env"}

    try:
        import google.generativeai as genai
        from PIL import Image

        genai.configure(api_key=GEMINI_API_KEY)
        img = Image.open(image_path)

        prompt = """You are an elite IIT-JEE Advanced Academic AI.
Analyze this academic problem/diagram image and extract the contents into structured JSON.

Return ONLY a valid JSON object with EXACTLY this structure (no markdown fences, no raw text):
{
  "subject": "Physics" | "Chemistry" | "Mathematics",
  "topic": "Specific chapter or subtopic name",
  "question": "Exact problem statement with clean LaTeX formatting for all formulas using $...$",
  "solution": "Concise step-by-step solution, core physical/chemical law applied, and final answer",
  "tags": ["Subject", "Topic", "Formula Name or Question Type"]
}"""

        # Try gemini-2.5-flash or fallback
        model = None
        for m_name in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-pro-vision"]:
            try:
                model = genai.GenerativeModel(m_name)
                response = model.generate_content([prompt, img])
                text = response.text.strip()
                # Clean up if markdown fences returned
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
                data = json.loads(text)
                return data
            except Exception as e:
                print(f"[AIVision] Model {m_name} notice: {e}")
                continue

        return {"error": "All vision models failed to parse image"}

    except Exception as e:
        return {"error": str(e)}

"""
Grok & Multimodal AI Agent for Cognitive Growth OS
Provides Socratic problem analysis, vision-based diagram inspection, and learning diagnostics.
"""

import os
import base64
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import urllib.request
    import json
except ImportError:
    pass

class GrowthAIAgent:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.x.ai/v1", model: str = "grok-2-vision-1212"):
        self.api_key = api_key or os.getenv("GROK_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
        self.base_url = base_url.rstrip("/")
        self.model = model

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_problem_snippet(self, image_path: str, user_query: str = "") -> str:
        """
        Sends screenshot of a problem/diagram to Grok Vision with Socratic JEE guidance.
        """
        if not self.is_configured():
            return ("[AI Agent Notice] Grok API key not configured. Set GROK_API_KEY environment variable "
                    "or configure in settings.yaml to enable instant AI vision sparring.")

        b64_image = self._encode_image(image_path)
        prompt = user_query or (
            "Analyze this academic problem. Act as an expert Socratic coach for JEE Advanced / high-cognition problem solving. "
            "DO NOT reveal the full solution or final answer directly. Instead:\n"
            "1. Identify the core underlying principles and theorems.\n"
            "2. Highlight the critical boundary conditions or constraints.\n"
            "3. Provide a guiding Socratic hint to unblock the student's reasoning."
        )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64_image}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.3
        }

        return self._send_request(payload)

    def socratic_sparring(self, topic: str, user_thought: str) -> str:
        """Text-based Socratic challenge on a concept or derivation."""
        if not self.is_configured():
            return "[AI Agent Notice] GROK_API_KEY is not set."

        prompt = (
            f"Subject/Concept: {topic}\n"
            f"Student's explanation or attempt: '{user_thought}'\n\n"
            "Evaluate the student's conceptual rigor from first principles. "
            "Point out any hand-waving, invalid assumptions, or domain limitations. Ask one precise follow-up question."
        )

        payload = {
            "model": "grok-2-1212" if "vision" in self.model else self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4
        }
        return self._send_request(payload)

    def _send_request(self, payload: Dict[str, Any]) -> str:
        req_url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        try:
            req = urllib.request.Request(req_url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[AI API Error] Failed to connect: {str(e)}"

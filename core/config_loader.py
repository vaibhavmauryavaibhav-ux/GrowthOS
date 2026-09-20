"""
Configuration Loader for Cognitive Growth OS
Provides safe loading with fallback if PyYAML is not installed in the environment.
"""

import os
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG = {
    "focus": {
        "default_mode": "auto",
        "idle_timeout_seconds": 240,
        "monk_mode_enabled": False
    },
    "auto_mode_patterns": [
        "*pw.live*",
        "*pw.live/*",
        "*physicswallah*",
        "*unacademy*",
        "*allen.in*",
        "*resonance.ac.in*",
        "*neetprep*",
        "*chemguide*",
        "*libretexts*",
        "*.pdf*",
        "*zathura*",
        "*xournalpp*",
        "*obsidian*"
    ],
    "monk_mode_blacklist": [
        "youtube.com/shorts",
        "instagram.com",
        "reddit.com",
        "twitter.com",
        "x.com",
        "discord.com",
        "twitch.tv",
        "netflix.com"
    ],
    "question_trainer": {
        "default_question_count": 20,
        "default_time_per_question_seconds": 150,
        "mode": "paced",
        "alert_audio_enabled": True
    },
    "spaced_repetition": {
        "default_review_time_seconds": 60,
        "problem_review_time_seconds": 180,
        "target_retention": 0.90,
        "daily_new_card_limit": 50
    },
    "ai": {
        "provider": "grok",
        "api_key_env": "GROK_API_KEY",
        "base_url": "https://api.x.ai/v1",
        "model": "grok-2-vision-1212",
        "socratic_mode": True
    }
}

CONFIG_PATH = Path(__file__).parent.parent / "config" / "settings.yaml"

def load_settings() -> Dict[str, Any]:
    """Loads settings.yaml if yaml module is installed, otherwise falls back to defaults or simple parsing."""
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()

    try:
        import yaml
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                merged = DEFAULT_CONFIG.copy()
                merged.update(data)
                return merged
    except ImportError:
        # Fallback: simple line parser for patterns if yaml module isn't installed
        cfg = DEFAULT_CONFIG.copy()
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
            patterns = []
            in_auto_patterns = False
            for line in lines:
                striped = line.strip()
                if striped.startswith("auto_mode_patterns:"):
                    in_auto_patterns = True
                    continue
                if in_auto_patterns:
                    if striped.startswith("-"):
                        val = striped.lstrip("-").strip().strip('"').strip("'")
                        patterns.append(val)
                    elif striped and not striped.startswith("#"):
                        in_auto_patterns = False
            if patterns:
                cfg["auto_mode_patterns"] = patterns
        except Exception:
            pass
        return cfg
    except Exception as e:
        print(f"[ConfigLoader] Notice: {e}, using default configuration.")

    return DEFAULT_CONFIG.copy()

"""
Quick Capture Tool: Screenshot Directly to Spaced Recall
Keybinding: Super + Shift + S
Instantly snips a region of the screen (equation, mechanism, problem) and registers it into the FSRS Spaced Recall Engine.
"""

import sys
import os
import time
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from core.db import add_recall_card

CAPTURES_DIR = Path.home() / ".growth_os" / "captures"

def capture_screen_snippet(save_path: Path) -> bool:
    """Captures a region of the screen across Wayland (grim+slurp) or cross-platform PIL."""
    save_path.parent.mkdir(parents=True, exist_ok=True)

    if sys.platform.startswith("linux"):
        try:
            # Wayland grim + slurp
            cmd = f"slurp | grim -g - '{save_path}'"
            res = subprocess.run(cmd, shell=True)
            return res.returncode == 0 and save_path.exists()
        except Exception:
            pass

    # Fallback using PIL / Pillow or screencapture
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        img.save(save_path)
        return True
    except Exception as e:
        print(f"[QuickCapture] Screenshot error: {e}")
        return False

def snap_to_recall(title: Optional[str] = None, prompt_text: str = "", 
                   answer_text: str = "", card_type: str = "diagram") -> Optional[int]:
    """Snips the screen and instantly adds it to Spaced Repetition queue."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recall_snip_{timestamp}.png"
    filepath = CAPTURES_DIR / filename

    print("[QuickCapture] Select screen region to capture...")
    success = capture_screen_snippet(filepath)
    if not success or not filepath.exists():
        print("[QuickCapture] Snippet cancelled or failed.")
        return None

    card_title = title or f"Visual Recall #{timestamp[-6:]}"
    card_id = add_recall_card(
        title=card_title,
        prompt_text=prompt_text or "Active Recall Drill: Re-derive or solve what is shown in the image.",
        image_path=str(filepath.resolve()),
        answer_text=answer_text,
        card_type=card_type
    )

    print(f"[QUICK CAPTURE SUCCESS] Snippet saved and queued for spaced review (Card ID: {card_id})")
    return card_id

if __name__ == "__main__":
    snap_to_recall()

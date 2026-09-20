"""
Mistake Logger Tool
Keybinding: Super + M
Records study & mock test mistakes and instantly creates an active-recall flashcard.
"""

import sys
import argparse
from pathlib import Path
from core.db import log_mistake, get_mistakes
from tools.quick_capture import capture_screen_snippet, CAPTURES_DIR
from datetime import datetime

def log_new_mistake(subject: str, topic: str, error_type: str, notes: str = "", 
                    attach_screenshot: bool = False) -> int:
    screenshot_path = ""
    if attach_screenshot:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = CAPTURES_DIR / f"mistake_{timestamp}.png"
        if capture_screen_snippet(filepath):
            screenshot_path = str(filepath.resolve())

    mistake_id = log_mistake(
        subject=subject,
        topic=topic,
        error_type=error_type,
        notes=notes,
        screenshot_path=screenshot_path
    )
    print(f"[MISTAKE LOGGED] #{mistake_id} recorded in {subject} ({topic}). Queued for Spaced Re-test!")
    return mistake_id

def interactive_cli():
    print("\n" + "="*45)
    print("       GROWTH OS : MISTAKE LEDGER")
    print("="*45)
    subject = input("Subject (Physics/Chemistry/Math/Other): ").strip() or "General"
    topic = input("Topic/Chapter (e.g. Rotational Dynamics): ").strip() or "General"
    print("\nError Categories:")
    print("  1. Concept Blindspot (didn't know theory/edge-case)")
    print("  2. Pattern Recognition Failure (didn't identify technique)")
    print("  3. Execution Error (calculation slip, silly mistake)")
    print("  4. Time-Pressure Panic (rushed, misread question)")
    choice = input("Select Error Category (1-4) [1]: ").strip() or "1"
    
    cat_map = {
        "1": "Concept Blindspot",
        "2": "Pattern Recognition Failure",
        "3": "Execution / Silly Slip",
        "4": "Time-Pressure Panic"
    }
    error_type = cat_map.get(choice, "Concept Blindspot")
    notes = input("Key takeaway / What to do differently: ").strip()
    snap = input("Attach screen snippet of problem? (y/n) [n]: ").strip().lower() == "y"

    log_new_mistake(subject, topic, error_type, notes, attach_screenshot=snap)

if __name__ == "__main__":
    interactive_cli()

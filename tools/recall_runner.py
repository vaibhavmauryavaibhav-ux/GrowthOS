"""
Timed Active Recall Runner
Keybinding: Super + R
Pulls due cards/mistakes from the FSRS engine and enforces strict timed retrieval.
"""

import time
import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.db import get_due_recall_cards, update_card_fsrs
from core.fsrs_engine import FSRSEngine
from core.plugin_manager import plugin_manager

fsrs = FSRSEngine(target_retention=0.90)

def open_image_viewer(image_path: str):
    """Opens image in default OS viewer without blocking."""
    if not image_path or not Path(image_path).exists():
        return
    if sys.platform.startswith("linux"):
        subprocess.Popen(["xdg-open", image_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif sys.platform == "win32":
        os.startfile(image_path)

def run_recall_session(max_cards: int = 15):
    due_cards = get_due_recall_cards()
    if not due_cards:
        print("\n[SPACED RECALL] All caught up! No cards currently due for review.")
        return

    cards_to_review = due_cards[:max_cards]
    print("\n" + "="*50)
    print(f"      ACTIVE RECALL DRILL : {len(cards_to_review)} CARDS DUE")
    print("="*50)

    for i, card in enumerate(cards_to_review, 1):
        print(f"\n[{i}/{len(cards_to_review)}] {card['title']}")
        print(f"Prompt: {card['prompt_text']}")

        if card["image_path"]:
            print(f"[Image attached]: {card['image_path']}")
            open_image_viewer(card["image_path"])

        # Timed Retrieval Countdown
        time_limit = 180 if card.get("card_type") == "mistake" else 60
        print(f"\n[TIMER] Active Retrieval Timer: {time_limit} seconds. Solve/recall now...")

        start_t = time.time()
        input("Press [Enter] when ready to reveal solution/answer...")
        elapsed = round(time.time() - start_t, 1)

        if card["answer_text"]:
            print(f"\n[ANSWER/SOLUTION]:\n{card['answer_text']}")
        print(f"[TIME] Time taken: {elapsed}s (Allotted: {time_limit}s)")

        # User FSRS rating
        print("\nRate your recall difficulty:")
        print("  1 = Again  (Blanked / Complete lapse)")
        print("  2 = Hard   (Recalled with severe effort / slight errors)")
        print("  3 = Good   (Solid, accurate recall)")
        print("  4 = Easy   (Immediate, effortless mastery)")

        while True:
            rating_input = input("Rating (1-4) [3]: ").strip() or "3"
            if rating_input in ["1", "2", "3", "4"]:
                rating = int(rating_input)
                break

        # Process with FSRS engine
        result = fsrs.process_review(card, rating)
        update_card_fsrs(
            card_id=card["id"],
            difficulty=result["difficulty"],
            stability=result["stability"],
            reps=result["reps"],
            lapses=result["lapses"],
            state=result["state"],
            next_review_iso=result["next_review"]
        )

        plugin_manager.dispatch("on_recall_completed", card, rating)
        print(f"[OK] Card updated! Next review in {result['interval_days']} days.\n" + "-"*40)

    print("\n[DRILL COMPLETED] Excellent mental conditioning. Working memory consolidated.")

if __name__ == "__main__":
    run_recall_session()

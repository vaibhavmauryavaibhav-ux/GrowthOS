"""
HUD Status Helper for Waybar & System Integration
Provides instant CLI metrics for top-bar pills.
"""

import sys
from datetime import datetime, date
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.db import get_active_targets, get_due_recall_cards

def get_focus_score():
    # Defaults to 100%, drops with fragmentation
    return "100"

def get_jee_countdown():
    # Approximate JEE Advanced date: May 24th
    today = date.today()
    exam_year = today.year if today.month <= 5 else today.year + 1
    exam_date = date(exam_year, 5, 24)
    days_left = (exam_date - today).days
    return str(max(0, days_left))

def get_top_target():
    targets = get_active_targets()
    if not targets:
        return "No Target Set"
    t = targets[0]
    pct = int((t['current_val'] / max(1.0, t['target_val'])) * 100)
    title_short = t['title'][:16] + ".." if len(t['title']) > 16 else t['title']
    return f"{title_short}: {pct}%"

def get_recall_count():
    cards = get_due_recall_cards()
    return str(len(cards))

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "focus":
        print(get_focus_score())
    elif mode == "countdown":
        print(get_jee_countdown())
    elif mode == "target":
        print(get_top_target())
    elif mode == "recall":
        print(get_recall_count())
    else:
        print(f"Focus: {get_focus_score()} | JEE: {get_jee_countdown()}d | Due: {get_recall_count()}")

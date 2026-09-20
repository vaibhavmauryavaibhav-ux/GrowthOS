"""
Growth OS : Standalone Runner & Command Center
Launches the Focus HUD, Observer Daemon, and displays system status.
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from hud.focus_hud import FocusHUD
from core.db import init_db, get_active_targets, get_due_recall_cards, get_mistakes
from tools.mistake_logger import interactive_cli
from tools.recall_runner import run_recall_session
from tools.quick_capture import snap_to_recall

def main():
    parser = argparse.ArgumentParser(description="Growth OS Command Runner")
    parser.add_argument("--hud", action="store_true", help="Launch persistent Focus HUD overlay")
    parser.add_argument("--mistake", action="store_true", help="Log a mistake into the ledger")
    parser.add_argument("--recall", action="store_true", help="Start timed active recall drill")
    parser.add_argument("--snip", action="store_true", help="Snip screen directly to spaced recall")
    parser.add_argument("--status", action="store_true", help="Show current targets and due cards")

    args = parser.parse_args()
    init_db()

    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    if args.mistake:
        interactive_cli()
    elif args.recall:
        run_recall_session()
    elif args.snip:
        snap_to_recall()
    elif args.status:
        targets = get_active_targets()
        due_cards = get_due_recall_cards()
        mistakes = get_mistakes(limit=5)
        print("\n" + "="*45)
        print("          GROWTH OS STATUS")
        print("="*45)
        print(f"[TARGETS] Active: {len(targets)}")
        for t in targets:
            pct = int((t['current_val'] / max(1.0, t['target_val'])) * 100)
            print(f"   - {t['title']}: {t['current_val']}/{t['target_val']} ({pct}%)")
        print(f"[RECALL] Cards Due for Spaced Recall: {len(due_cards)}")
        print(f"[MISTAKES] Total Mistakes Analyzed: {len(mistakes)}")
        print("="*45 + "\n")
    else:
        # Default action: launch the Focus HUD
        print("[+] Launching Growth OS Focus HUD...")
        app = FocusHUD()
        app.mainloop()

if __name__ == "__main__":
    main()

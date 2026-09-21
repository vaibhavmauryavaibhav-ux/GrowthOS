"""
Growth OS - Automated Database Backup & Anki / Excel Export Engine
Protects your academic data with automated snapshots and provides 1-click CSV/Anki exports.
"""

import sys
import os
import shutil
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.db import DB_PATH, get_all_recall_cards, get_mistakes

BACKUP_DIR = Path.home() / ".growth_os" / "backups"
EXPORT_DIR = Path.home() / ".growth_os" / "exports"

for d in [BACKUP_DIR, EXPORT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def create_database_snapshot() -> Path:
    """Creates a timestamped backup of the SQLite database."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"growth_os_backup_{ts}.db"
    if DB_PATH.exists():
        shutil.copy2(DB_PATH, backup_file)
        # Keep only the last 15 backups
        all_backups = sorted(BACKUP_DIR.glob("growth_os_backup_*.db"), key=os.path.getmtime, reverse=True)
        for old in all_backups[15:]:
            try:
                old.unlink()
            except Exception:
                pass
    return backup_file

def export_to_anki_tsv() -> Path:
    """Exports all flashcards to a tab-separated file for 1-click import into Anki."""
    cards = get_all_recall_cards()
    out_file = EXPORT_DIR / "anki_cards_export.tsv"
    with open(out_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        for c in cards:
            q = c.get("prompt_text") or c.get("title", "")
            a = c.get("answer_text", "")
            tags = c.get("card_type", "JEE")
            writer.writerow([q, a, tags])
    return out_file

def export_mistakes_to_csv() -> Path:
    """Exports mistake ledger into a CSV spreadsheet for Excel or Google Sheets."""
    mistakes = get_mistakes()
    out_file = EXPORT_DIR / "mistake_ledger_export.csv"
    with open(out_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Subject", "Topic", "Error Type", "Notes", "Date"])
        for m in mistakes:
            writer.writerow([
                m["id"],
                m["subject"],
                m["topic"],
                m["error_type"],
                m.get("notes", ""),
                m.get("date_logged", "")
            ])
    return out_file

def run_full_backup_and_export() -> Dict[str, str]:
    """Runs database snapshot, Anki TSV export, and Excel CSV export in one go."""
    db_backup = create_database_snapshot()
    anki_tsv = export_to_anki_tsv()
    mistake_csv = export_mistakes_to_csv()
    return {
        "db_backup": str(db_backup),
        "anki_tsv": str(anki_tsv),
        "mistake_csv": str(mistake_csv),
        "export_dir": str(EXPORT_DIR)
    }

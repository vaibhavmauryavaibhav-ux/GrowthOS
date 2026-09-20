"""
Daily Streak & Milestone Plugin
Tracks question solving velocity, daily streaks, and triggers milestone celebrations.
"""

from datetime import datetime, timezone
from pathlib import Path
import json
from plugins.base_plugin import GrowthOSPlugin

STREAK_FILE = Path.home() / ".growth_os" / "streak_data.json"

class DailyStreakPlugin(GrowthOSPlugin):
    name = "Daily Streak & Velocity Tracker"
    version = "1.0.0"
    description = "Tracks question counts, daily streaks, and sends milestone cues."

    def on_load(self):
        self.data = self._load_data()

    def _load_data(self):
        if STREAK_FILE.exists():
            try:
                with open(STREAK_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"streak_days": 1, "last_date": "", "today_count": 0}

    def _save_data(self):
        STREAK_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STREAK_FILE, "w") as f:
            json.dump(self.data, f)

    def on_question_solved(self, question_data):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.data["last_date"] != today:
            self.data["last_date"] = today
            self.data["today_count"] = 0
            self.data["streak_days"] += 1

        self.data["today_count"] += 1
        count = self.data["today_count"]
        self._save_data()

        # Check milestones
        if count in [10, 25, 50, 100]:
            print(f"[MILESTONE REACHED] You have solved {count} problems today! Streak: {self.data['streak_days']} days!")

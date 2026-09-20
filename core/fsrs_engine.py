"""
Free Spaced Repetition Scheduler (FSRS) Engine
Calculates memory stability, item difficulty, and next optimal review intervals.
"""

import math
from datetime import datetime, timedelta, timezone
from typing import Tuple, Dict, Any

# Standard FSRS 4.5 Parameters (optimized for fast learning & high retention)
DEFAULT_W = [
    0.4072, 1.1827, 3.1262, 15.4722,  # Initial stabilities for Again, Hard, Good, Easy
    7.2102,                             # Initial difficulty intercept
    0.5316,                             # Difficulty modifier
    1.0651,                             # Difficulty update factor
    0.0234,                             # Stability increase decay
    1.6160,                             # Stability recall exponent
    0.1544,                             # Hard penalty
    1.0819,                             # Easy bonus
    1.9813,                             # Lapse stability factor
    0.0953,                             # Lapse stability power
    0.2975,                             # Lapse difficulty adjustment
    0.3421,                             # Retrievability stability factor
]

class FSRSEngine:
    def __init__(self, target_retention: float = 0.90):
        self.target_retention = target_retention
        self.w = DEFAULT_W

    def get_initial_stability(self, rating: int) -> float:
        """Rating: 1=Again, 2=Hard, 3=Good, 4=Easy"""
        rating = max(1, min(4, rating))
        return max(0.1, self.w[rating - 1])

    def get_initial_difficulty(self, rating: int) -> float:
        """Rating: 1=Again, 2=Hard, 3=Good, 4=Easy"""
        rating = max(1, min(4, rating))
        d0 = self.w[4] - (rating - 3) * self.w[5]
        return max(1.0, min(10.0, d0))

    def next_difficulty(self, d: float, rating: int) -> float:
        rating = max(1, min(4, rating))
        next_d = d - self.w[6] * (rating - 3)
        # Mean reversion towards initial difficulty
        mean_reversion = self.w[7] * self.get_initial_difficulty(3) + (1 - self.w[7]) * next_d
        return max(1.0, min(10.0, mean_reversion))

    def calculate_retrievability(self, elapsed_days: float, stability: float) -> float:
        if stability <= 0.0:
            return 0.0
        return (1.0 + elapsed_days / (9.0 * stability)) ** -1

    def next_stability_recall(self, d: float, s: float, r: float, rating: int) -> float:
        hard_penalty = self.w[9] if rating == 2 else 1.0
        easy_bonus = self.w[10] if rating == 4 else 1.0
        s_inc = math.exp(self.w[8]) * (11.0 - d) * (s ** -self.w[9]) * (math.exp((1.0 - r) * self.w[14]) - 1.0) * hard_penalty * easy_bonus
        return max(0.1, s * (1.0 + s_inc))

    def next_stability_lapse(self, d: float, s: float, r: float) -> float:
        s_lapse = self.w[11] * (d ** -self.w[12]) * (((s + 1.0) ** self.w[13]) - 1.0) * math.exp((1.0 - r) * self.w[14])
        return max(0.1, min(s, s_lapse))

    def calculate_interval(self, stability: float) -> float:
        """Returns optimal interval in days for target retention (default 0.90)"""
        interval = (9.0 * stability) * ((1.0 / self.target_retention) - 1.0)
        return max(0.04, interval) # Minimum ~1 hour

    def process_review(self, card: Dict[str, Any], rating: int, now: datetime = None) -> Dict[str, Any]:
        """
        Processes a review rating (1=Again, 2=Hard, 3=Good, 4=Easy)
        Returns updated FSRS parameters and next_review ISO timestamp.
        """
        now = now or datetime.now(timezone.utc)
        reps = card.get("reps", 0)
        lapses = card.get("lapses", 0)
        current_s = card.get("stability", 0.5)
        current_d = card.get("difficulty", 5.0)
        state = card.get("state", "new")
        last_review_str = card.get("last_review")

        # Calculate elapsed days since last review
        if last_review_str:
            try:
                last_dt = datetime.fromisoformat(last_review_str)
                elapsed_days = max(0.001, (now - last_dt).total_seconds() / 86400.0)
            except Exception:
                elapsed_days = 1.0
        else:
            elapsed_days = 0.5

        if state == "new" or reps == 0:
            new_s = self.get_initial_stability(rating)
            new_d = self.get_initial_difficulty(rating)
            reps = 1
            lapses = 1 if rating == 1 else 0
            new_state = "relearning" if rating == 1 else "review"
        else:
            r = self.calculate_retrievability(elapsed_days, current_s)
            new_d = self.next_difficulty(current_d, rating)
            if rating == 1:
                # Failed recall (Lapse)
                new_s = self.next_stability_lapse(new_d, current_s, r)
                lapses += 1
                new_state = "relearning"
            else:
                new_s = self.next_stability_recall(new_d, current_s, r, rating)
                reps += 1
                new_state = "review"

        interval_days = self.calculate_interval(new_s)
        
        # If rating is 1 (Again), review soon (e.g. 10 minutes to 1 hour)
        if rating == 1:
            interval_seconds = 600 # 10 minutes
        else:
            interval_seconds = int(interval_days * 86400)

        next_review_dt = now + timedelta(seconds=interval_seconds)

        return {
            "card_id": card["id"],
            "difficulty": round(new_d, 3),
            "stability": round(new_s, 3),
            "reps": reps,
            "lapses": lapses,
            "state": new_state,
            "next_review": next_review_dt.isoformat(),
            "interval_days": round(interval_days, 2)
        }

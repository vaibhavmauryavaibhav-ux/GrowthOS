"""
Growth OS Automated Test Suite
Verifies Database CRUD, FSRS Engine, Wildcard Pattern Matching,
Question Trainer state transitions, and Plugin Hook Dispatch.
"""

import sys
import os
import unittest
from pathlib import Path
from datetime import datetime, timezone

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Use an isolated test database
os.environ["GROWTH_OS_DB_PATH"] = str(PROJECT_ROOT / "scratch" / "test_growth_os.db")

from core.db import (
    init_db, add_target, update_target_progress, get_active_targets,
    log_mistake, get_mistakes, add_recall_card, get_due_recall_cards,
    start_session, end_session
)
from core.fsrs_engine import FSRSEngine
from daemons.observer import WindowObserver
from daemons.question_trainer import QuestionTrainer
from core.plugin_manager import plugin_manager

class TestGrowthOS(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_01_generic_targets(self):
        """Verify adding and updating generic targets (percentages & counts)."""
        target_id = add_target(
            title="Revise 40% of Thermodynamics",
            target_type="percent",
            target_val=40.0,
            unit="%"
        )
        self.assertIsNotNone(target_id)

        # Progress increment
        updated = update_target_progress(target_id, increment=25.0)
        self.assertEqual(updated["current_val"], 25.0)
        self.assertEqual(updated["completed"], 0)

        # Complete target
        updated_2 = update_target_progress(target_id, increment=20.0)
        self.assertEqual(updated_2["current_val"], 45.0)
        self.assertEqual(updated_2["completed"], 1)

    def test_02_mistake_ledger_and_recall_sync(self):
        """Verify logging a mistake automatically creates a Spaced Recall card."""
        mistake_id = log_mistake(
            subject="Physics",
            topic="Rotational Dynamics",
            error_type="Concept Blindspot",
            notes="Forgot to consider friction direction during angular deceleration"
        )
        self.assertIsNotNone(mistake_id)

        mistakes = get_mistakes(limit=1)
        self.assertEqual(len(mistakes), 1)
        self.assertEqual(mistakes[0]["subject"], "Physics")
        self.assertIsNotNone(mistakes[0]["recall_card_id"])

        # Check that a due recall card was created
        due_cards = get_due_recall_cards()
        self.assertTrue(any("Rotational Dynamics" in c["title"] for c in due_cards))

    def test_03_fsrs_engine_calculations(self):
        """Verify FSRS calculates reasonable intervals and handles ratings."""
        fsrs = FSRSEngine(target_retention=0.90)
        card = {
            "id": 999,
            "difficulty": 5.0,
            "stability": 0.5,
            "reps": 0,
            "lapses": 0,
            "state": "new",
            "last_review": None
        }

        # First review with Good (3)
        res = fsrs.process_review(card, rating=3)
        self.assertEqual(res["reps"], 1)
        self.assertEqual(res["state"], "review")
        self.assertGreater(res["stability"], 0.5)
        self.assertGreater(res["interval_days"], 0.1)

        # Subsequent lapse with Again (1)
        card_reviewed = {
            "id": 999,
            "difficulty": res["difficulty"],
            "stability": res["stability"],
            "reps": 1,
            "lapses": 0,
            "state": "review",
            "last_review": datetime.now(timezone.utc).isoformat()
        }
        res_lapse = fsrs.process_review(card_reviewed, rating=1)
        self.assertEqual(res_lapse["lapses"], 1)
        self.assertEqual(res_lapse["state"], "relearning")

    def test_04_window_observer_pattern_matching(self):
        """Verify wildcard matching for auto mode whitelist."""
        observer = WindowObserver()
        observer.patterns = ["*pw.live*", "*neetprep*", "*.pdf*"]

        # Positive matches
        self.assertIsNotNone(observer.matches_auto_pattern("Physics Wallah - https://pw.live/study/batch/123"))
        self.assertIsNotNone(observer.matches_auto_pattern("NEETPrep Question Bank"))
        self.assertIsNotNone(observer.matches_auto_pattern("HC_Verma_Concepts_of_Physics.pdf - Zathura"))

        # Negative non-matches
        self.assertIsNone(observer.matches_auto_pattern("YouTube Shorts - Feed"))
        self.assertIsNone(observer.matches_auto_pattern("Discord | General Chat"))

    def test_05_question_trainer_state_transitions(self):
        """Verify Question Trainer per-question countdown and +1 increment."""
        trainer = QuestionTrainer()
        trainer.start_session(mode="paced", total_questions=5, time_per_question=60)
        self.assertTrue(trainer.is_active)
        self.assertEqual(trainer.current_question, 1)

        # Solve question 1
        res1 = trainer.next_question(is_correct=True, notes="Quick solve")
        self.assertEqual(res1["status"], "ongoing")
        self.assertEqual(trainer.questions_solved, 1)
        self.assertEqual(trainer.current_question, 2)

        # Solve rest to complete
        trainer.next_question(is_correct=True)
        trainer.next_question(is_correct=True)
        trainer.next_question(is_correct=True)
        res5 = trainer.next_question(is_correct=True)
        self.assertEqual(res5["status"], "completed")
        self.assertFalse(trainer.is_active)

    def test_06_plugin_manager_dispatch(self):
        """Verify plugin manager loads extensions and dispatches events safely."""
        self.assertGreater(len(plugin_manager.plugins), 0)
        # Should not throw any exceptions
        plugin_manager.dispatch("on_question_solved", {
            "session_id": 1,
            "question_number": 10,
            "time_spent_seconds": 45.0,
            "is_correct": True
        })

if __name__ == "__main__":
    unittest.main()

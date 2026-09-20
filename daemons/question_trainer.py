"""
Timed Question Solving Trainer Engine
Implements per-question paced countdowns and open-ended stopwatch with +1 counter.
"""

import time
from typing import Dict, Any, Optional
from core.db import start_session, end_session, log_question_solved, update_target_progress, get_active_targets
from core.plugin_manager import plugin_manager

class QuestionTrainer:
    def __init__(self):
        self.is_active = False
        self.mode = "paced" # "paced" or "open"
        self.total_questions = 20
        self.time_per_question = 150 # seconds (2.5 mins)
        self.current_question = 1
        self.session_id: Optional[int] = None
        
        self.session_start_time = 0.0
        self.question_start_time = 0.0
        self.questions_solved = 0
        self.associated_target_id: Optional[int] = None

    def start_session(self, mode: str = "paced", total_questions: int = 20, 
                      time_per_question: int = 150, target_id: Optional[int] = None):
        """Initializes a new training session."""
        self.is_active = True
        self.mode = mode
        self.total_questions = max(1, total_questions)
        self.time_per_question = max(10, time_per_question)
        self.current_question = 1
        self.questions_solved = 0
        self.associated_target_id = target_id

        now = time.time()
        self.session_start_time = now
        self.question_start_time = now

        self.session_id = start_session(mode=f"trainer_{mode}")
        plugin_manager.dispatch("on_session_start", {
            "session_id": self.session_id,
            "mode": self.mode,
            "total_questions": self.total_questions
        })

    def next_question(self, is_correct: bool = True, notes: str = "") -> Dict[str, Any]:
        """Triggered on '+1' hotkey or HUD button. Logs question and advances."""
        if not self.is_active:
            return {"status": "inactive"}

        now = time.time()
        time_spent = round(now - self.question_start_time, 1)
        self.questions_solved += 1

        # Log to database
        log_id = log_question_solved(
            session_id=self.session_id,
            question_number=self.current_question,
            time_spent_seconds=time_spent,
            is_correct=is_correct,
            notes=notes
        )

        # Update associated daily target if configured
        if self.associated_target_id:
            update_target_progress(self.associated_target_id, increment=1.0)
        else:
            # Auto-increment first count-based target if active
            targets = get_active_targets()
            for t in targets:
                if t["target_type"] == "count":
                    update_target_progress(t["id"], increment=1.0)
                    break

        # Dispatch event to plugins (streak tracker, etc.)
        plugin_manager.dispatch("on_question_solved", {
            "session_id": self.session_id,
            "question_number": self.current_question,
            "time_spent_seconds": time_spent,
            "is_correct": is_correct,
            "total_solved_session": self.questions_solved
        })

        self.current_question += 1
        self.question_start_time = now # reset timer for next question

        is_completed = (self.mode == "paced" and self.questions_solved >= self.total_questions)
        if is_completed:
            self.stop_session()

        return {
            "status": "completed" if is_completed else "ongoing",
            "solved": self.questions_solved,
            "time_spent": time_spent
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns live state for HUD rendering."""
        if not self.is_active:
            return {
                "is_active": False,
                "display_text": "Trainer: Idle"
            }

        now = time.time()
        total_elapsed = int(now - self.session_start_time)
        q_elapsed = int(now - self.question_start_time)

        if self.mode == "paced":
            q_remaining = max(0, self.time_per_question - q_elapsed)
            mins_rem = q_remaining // 60
            secs_rem = q_remaining % 60
            time_str = f"{mins_rem:02d}:{secs_rem:02d}"
            display = f"Q: {self.current_question}/{self.total_questions} | ⏳ {time_str}"
            is_overtime = (q_remaining == 0)
        else:
            # Open mode
            mins_tot = total_elapsed // 60
            secs_tot = total_elapsed % 60
            time_str = f"{mins_tot:02d}:{secs_tot:02d}"
            display = f"⏱ {time_str} | Solved: {self.questions_solved}"
            is_overtime = False

        return {
            "is_active": True,
            "mode": self.mode,
            "current_question": self.current_question,
            "total_questions": self.total_questions,
            "solved_count": self.questions_solved,
            "question_elapsed": q_elapsed,
            "total_elapsed": total_elapsed,
            "display_text": display,
            "is_overtime": is_overtime
        }

    def stop_session(self):
        """Concludes the training block."""
        if not self.is_active:
            return
        self.is_active = False
        duration = round(time.time() - self.session_start_time, 1)
        if self.session_id:
            end_session(self.session_id, duration_seconds=duration, questions_solved=self.questions_solved)
            plugin_manager.dispatch("on_session_end", {
                "session_id": self.session_id,
                "duration_seconds": duration,
                "questions_solved": self.questions_solved
            })
        self.session_id = None

# Global instance for HUD & hotkeys
question_trainer = QuestionTrainer()

"""
Non-Removable Focus HUD
Cyberpunk dark-themed persistent overlay supporting Auto Mode, Manual War Mode, 
Question Solving Trainer (+1 & Paced countdown), Targets, and Quick Tools.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
from pathlib import Path

from daemons.observer import WindowObserver
from daemons.question_trainer import question_trainer
from daemons.monk_guardian import monk_guardian
from core.db import get_active_targets, get_due_recall_cards, add_target, update_target_progress
from tools.quick_capture import snap_to_recall
from tools.mistake_logger import interactive_cli
from tools.recall_runner import run_recall_session

class FocusHUD(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("GROWTH OS : FOCUS HUD")
        self.geometry("460x520+30+40") # Positioned conveniently at top-left
        self.attributes("-topmost", True) # Always on top
        self.configure(bg="#0d1117")

        # Styling
        self.font_title = ("Segoe UI", 12, "bold")
        self.font_main = ("Segoe UI", 10)
        self.font_timer = ("Consolas", 20, "bold")
        self.font_badge = ("Segoe UI", 9, "bold")

        self.observer = WindowObserver()
        self.is_running = True

        self._build_ui()
        self._start_observer_thread()

    def _build_ui(self):
        # 1. Header & Mode Switcher
        header_frame = tk.Frame(self, bg="#161b22", pady=8, padx=12)
        header_frame.pack(fill="x")

        self.lbl_title = tk.Label(header_frame, text="⚡ GROWTH OS", font=self.font_title, fg="#58a6ff", bg="#161b22")
        self.lbl_title.pack(side="left")

        self.btn_mode_toggle = tk.Button(
            header_frame, text="MODE: AUTO [ON]", font=self.font_badge,
            bg="#238636", fg="white", activebackground="#2ea043", relief="flat", padx=8,
            command=self._toggle_mode
        )
        self.btn_mode_toggle.pack(side="right")

        # 2. Status Banner (Active Window / Pattern)
        self.lbl_status = tk.Label(
            self, text="Scanning active window...", font=self.font_main,
            fg="#8b949e", bg="#0d1117", pady=4
        )
        self.lbl_status.pack(fill="x")

        # 3. Question Trainer Section
        trainer_card = tk.LabelFrame(
            self, text=" 🎯 Timed Question Trainer ", font=self.font_badge,
            fg="#7ee787", bg="#161b22", padx=10, pady=8
        )
        trainer_card.pack(fill="x", padx=12, pady=6)

        # Question Trainer Timer Display
        self.lbl_trainer_display = tk.Label(
            trainer_card, text="Trainer: Idle", font=self.font_timer,
            fg="#f0f6fc", bg="#161b22"
        )
        self.lbl_trainer_display.pack(pady=4)

        # Controls row
        ctrl_row = tk.Frame(trainer_card, bg="#161b22")
        ctrl_row.pack(fill="x", pady=4)

        self.btn_plus_one = tk.Button(
            ctrl_row, text="🔥 +1 SOLVED (NEXT)", font=("Segoe UI", 11, "bold"),
            bg="#1f6feb", fg="white", activebackground="#388bfd", relief="flat", padx=12, pady=4,
            command=self._handle_plus_one
        )
        self.btn_plus_one.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_start_trainer = tk.Button(
            ctrl_row, text="Start Paced (20Q)", font=self.font_badge,
            bg="#30363d", fg="#c9d1d9", relief="flat", padx=8,
            command=self._start_trainer_prompt
        )
        self.btn_start_trainer.pack(side="right", padx=2)

        # 4. Daily Targets Section
        targets_card = tk.LabelFrame(
            self, text=" 📌 Active Target / Daily Wins ", font=self.font_badge,
            fg="#a371f7", bg="#161b22", padx=10, pady=6
        )
        targets_card.pack(fill="x", padx=12, pady=4)

        self.lbl_target_info = tk.Label(
            targets_card, text="No active target set", font=self.font_main,
            fg="#c9d1d9", bg="#161b22", justify="left"
        )
        self.lbl_target_info.pack(anchor="w")

        btn_add_target = tk.Button(
            targets_card, text="+ Set New Target", font=("Segoe UI", 8),
            bg="#21262d", fg="#8b949e", relief="flat", command=self._prompt_new_target
        )
        btn_add_target.pack(anchor="e", pady=2)

        # 5. Quick Action Toolbox
        tools_frame = tk.Frame(self, bg="#0d1117", pady=6)
        tools_frame.pack(fill="x", padx=12)

        btn_snip = tk.Button(
            tools_frame, text="📷 Snip to Recall", font=self.font_badge,
            bg="#238636", fg="white", relief="flat", padx=6, pady=4,
            command=self._trigger_snip
        )
        btn_snip.pack(side="left", expand=True, fill="x", padx=2)

        btn_mistake = tk.Button(
            tools_frame, text="📘 Log Mistake", font=self.font_badge,
            bg="#da3633", fg="white", relief="flat", padx=6, pady=4,
            command=self._trigger_mistake
        )
        btn_mistake.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_recall = tk.Button(
            tools_frame, text="🧠 Recall Drill (0)", font=self.font_badge,
            bg="#8957e5", fg="white", relief="flat", padx=6, pady=4,
            command=self._trigger_recall
        )
        self.btn_recall.pack(side="left", expand=True, fill="x", padx=2)

        # Refresh initial data
        self._refresh_targets_display()

    def _toggle_mode(self):
        self.observer.is_auto_mode = not self.observer.is_auto_mode
        if self.observer.is_auto_mode:
            self.btn_mode_toggle.config(text="MODE: AUTO [ON]", bg="#238636")
        else:
            self.btn_mode_toggle.config(text="MODE: MANUAL", bg="#8957e5")

    def _start_trainer_prompt(self):
        if question_trainer.is_active:
            question_trainer.stop_session()
            self.btn_start_trainer.config(text="Start Paced")
        else:
            # Default to 20 questions, 150s per question
            question_trainer.start_session(mode="paced", total_questions=20, time_per_question=150)
            self.btn_start_trainer.config(text="Stop Trainer")

    def _handle_plus_one(self):
        if not question_trainer.is_active:
            # Auto-start open mode if user just hits +1
            question_trainer.start_session(mode="open")
        question_trainer.next_question(is_correct=True)
        self._refresh_targets_display()

    def _prompt_new_target(self):
        # Quick modal to add a generic target
        win = tk.Toplevel(self)
        win.title("Set New Target")
        win.geometry("320x220")
        win.configure(bg="#161b22")
        win.attributes("-topmost", True)

        tk.Label(win, text="Target Description:", fg="white", bg="#161b22").pack(pady=4)
        entry_title = tk.Entry(win, width=30)
        entry_title.insert(0, "Revise 40% of Thermodynamics")
        entry_title.pack(pady=2)

        tk.Label(win, text="Target Goal Number:", fg="white", bg="#161b22").pack(pady=4)
        entry_val = tk.Entry(win, width=10)
        entry_val.insert(0, "40")
        entry_val.pack(pady=2)

        def save():
            title = entry_title.get().strip()
            val = float(entry_val.get().strip() or "100")
            add_target(title, target_type="count" if "problem" in title.lower() else "percent", target_val=val)
            self._refresh_targets_display()
            win.destroy()

        tk.Button(win, text="Save Target", bg="#238636", fg="white", command=save).pack(pady=10)

    def _refresh_targets_display(self):
        targets = get_active_targets()
        if targets:
            t = targets[0]
            pct = int((t['current_val'] / max(1.0, t['target_val'])) * 100)
            self.lbl_target_info.config(
                text=f"{t['title']}\nProgress: {t['current_val']}/{t['target_val']} ({pct}%)"
            )
        else:
            self.lbl_target_info.config(text="No active target. Click '+ Set New Target' to create one.")

        due_count = len(get_due_recall_cards())
        self.btn_recall.config(text=f"🧠 Recall Drill ({due_count})")

    def _trigger_snip(self):
        self.withdraw() # hide HUD momentarily to snip
        time.sleep(0.3)
        snap_to_recall()
        self.deiconify()
        self._refresh_targets_display()

    def _trigger_mistake(self):
        threading.Thread(target=interactive_cli, daemon=True).start()

    def _trigger_recall(self):
        threading.Thread(target=run_recall_session, daemon=True).start()

    def _start_observer_thread(self):
        def loop():
            while self.is_running:
                try:
                    res = self.observer.tick()
                    status_text = f"Window: {res['window_title'][:36]}..."
                    if res['matched_pattern']:
                        status_text = f"🎯 Auto Tracking: [{res['matched_pattern']}]"

                    # Question trainer status
                    q_status = question_trainer.get_status()
                    
                    # Update UI in main thread
                    self.after(0, self._update_ui_state, status_text, res['matched_pattern'], q_status)
                except Exception as e:
                    pass
                time.sleep(1.0)

        threading.Thread(target=loop, daemon=True).start()

    def _update_ui_state(self, status_text, matched_pattern, q_status):
        self.lbl_status.config(text=status_text)
        if matched_pattern:
            self.lbl_status.config(fg="#7ee787")
        else:
            self.lbl_status.config(fg="#8b949e")

        if q_status["is_active"]:
            self.lbl_trainer_display.config(text=q_status["display_text"])
            if q_status.get("is_overtime"):
                self.lbl_trainer_display.config(fg="#f85149")
            else:
                self.lbl_trainer_display.config(fg="#58a6ff")
        else:
            self.lbl_trainer_display.config(text="Trainer: Idle", fg="#8b949e")

if __name__ == "__main__":
    app = FocusHUD()
    app.mainloop()

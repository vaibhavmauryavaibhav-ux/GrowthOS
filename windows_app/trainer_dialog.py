"""
Growth OS for Windows - Question Solving Trainer Dialog
Implements paced countdowns and stopwatch mode with +1 question increment hotkey.
"""

import sys
import os
import time
import winsound
from pathlib import Path
from typing import Optional

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut

from core.db import log_question_solved, get_active_targets, update_target_progress
from windows_app.styles import DIALOG_STYLE, COLOR_CYAN, COLOR_GREEN, COLOR_RED, COLOR_MAUVE

class QuestionTrainerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Timed Question Trainer - Growth OS")
        self.setStyleSheet(DIALOG_STYLE)
        self.resize(500, 380)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.time_per_q = 150 # 2.5 minutes
        self.q_time_left = self.time_per_q
        self.solved_count = 0
        self.target_count = 20
        self.is_running = False

        self.targets = get_active_targets()
        self.current_target_id: Optional[int] = self.targets[0]["id"] if self.targets else None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("⏱ Timed Question Solving Trainer")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        # Target Selector
        target_row = QHBoxLayout()
        t_lbl = QLabel("Associated Target:")
        self.target_box = QComboBox()
        if self.targets:
            for t in self.targets:
                self.target_box.addItem(f"{t['title']} ({int(t['current_val'])}/{int(t['target_val'])})", t['id'])
        else:
            self.target_box.addItem("No active target set", None)
        target_row.addWidget(t_lbl)
        target_row.addWidget(self.target_box)
        layout.addLayout(target_row)

        # Big Countdown Display
        self.timer_display = QLabel("02:30")
        self.timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_display.setStyleSheet(f"font-size: 48px; font-weight: bold; color: {COLOR_CYAN}; font-family: 'Consolas', monospace;")
        layout.addWidget(self.timer_display)

        # Solved Counter
        self.solved_display = QLabel(f"Solved: 0 / {self.target_count}")
        self.solved_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.solved_display.setStyleSheet("font-size: 16px; font-weight: 600; color: #b4befe;")
        layout.addWidget(self.solved_display)

        # Progress bar
        self.bar = QProgressBar()
        self.bar.setRange(0, self.time_per_q)
        self.bar.setValue(self.time_per_q)
        self.bar.setTextVisible(False)
        layout.addWidget(self.bar)

        # Actions
        btn_layout = QHBoxLayout()

        self.next_q_btn = QPushButton("+1 Solved [Space]")
        self.next_q_btn.setProperty("class", "primary-btn")
        self.next_q_btn.clicked.connect(self.record_solved)
        btn_layout.addWidget(self.next_q_btn)

        self.toggle_btn = QPushButton("Start Session")
        self.toggle_btn.setProperty("class", "secondary-btn")
        self.toggle_btn.clicked.connect(self.toggle_session)
        btn_layout.addWidget(self.toggle_btn)

        layout.addLayout(btn_layout)

        # Shortcut for Space
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.record_solved)

    def toggle_session(self):
        if not self.is_running:
            self.is_running = True
            self.toggle_btn.setText("Pause")
            self.timer.start(1000)
        else:
            self.is_running = False
            self.toggle_btn.setText("Resume")
            self.timer.stop()

    def _on_tick(self):
        if self.q_time_left > 0:
            self.q_time_left -= 1
        mins = self.q_time_left // 60
        secs = self.q_time_left % 60
        self.timer_display.setText(f"{mins:02d}:{secs:02d}")
        self.bar.setValue(self.q_time_left)

        if self.q_time_left <= 15:
            self.timer_display.setStyleSheet(f"font-size: 48px; font-weight: bold; color: {COLOR_RED}; font-family: 'Consolas', monospace;")
        else:
            self.timer_display.setStyleSheet(f"font-size: 48px; font-weight: bold; color: {COLOR_CYAN}; font-family: 'Consolas', monospace;")

    def record_solved(self):
        if not self.is_running:
            self.toggle_session()

        self.solved_count += 1
        self.solved_display.setText(f"Solved: {self.solved_count} / {self.target_count}")

        # Update target in DB
        tgt_data = self.target_box.currentData()
        if tgt_data:
            update_target_progress(tgt_data, 1.0)
            log_question_solved(target_id=tgt_data, time_taken=self.time_per_q - self.q_time_left, is_correct=True)

        try:
            winsound.MessageBeep(winsound.MB_OK)
        except Exception:
            pass

        # Reset per-question countdown
        self.q_time_left = self.time_per_q
        self.bar.setValue(self.time_per_q)
        self.timer_display.setText(f"{self.time_per_q // 60:02d}:{self.time_per_q % 60:02d}")

def open_trainer_dialog():
    dlg = QuestionTrainerDialog()
    dlg.exec()

"""
Growth OS for Windows - Timed Active Recall Drill Dialog
Keybinding: Alt + Shift + R
Enforces strict timed retrieval for due cards using the FSRS 4.5 spaced repetition scheduler.
"""

import sys
import os
import winsound
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QScrollArea, QWidget, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut

from core.db import get_due_recall_cards, update_card_fsrs
from core.fsrs_engine import FSRSEngine
from windows_app.styles import DIALOG_STYLE, COLOR_CYAN, COLOR_RED, COLOR_GREEN, COLOR_PEACH, COLOR_TEXT, COLOR_MANTLE

fsrs = FSRSEngine(target_retention=0.90)

class RecallDrillDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Timed Active Recall Drill - Growth OS")
        self.setStyleSheet(DIALOG_STYLE)
        self.resize(640, 560)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.cards = get_due_recall_cards()
        self.current_idx = 0
        self.time_left = 60
        self.max_time = 60
        self.is_answer_revealed = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)

        self._build_ui()
        self._load_current_card()

    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(14)
        self.main_layout.setContentsMargins(24, 24, 24, 24)

        # Header row: Title + Counter
        top_row = QHBoxLayout()
        self.header_lbl = QLabel("🧠 Timed Active Recall Drill")
        self.header_lbl.setObjectName("HeaderTitle")
        
        self.counter_lbl = QLabel("Card 0/0")
        self.counter_lbl.setStyleSheet("color: #b4befe; font-weight: bold; font-size: 13px;")

        top_row.addWidget(self.header_lbl)
        top_row.addStretch()
        top_row.addWidget(self.counter_lbl)
        self.main_layout.addLayout(top_row)

        # Countdown Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.max_time)
        self.progress_bar.setValue(self.max_time)
        self.progress_bar.setFormat("⏱ %v s remaining")
        self.main_layout.addWidget(self.progress_bar)

        # Scrollable Content Area for Question and Answer
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: 1px solid #313244; border-radius: 10px; background-color: #181825; }")
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(12)
        self.content_layout.setContentsMargins(16, 16, 16, 16)

        self.tags_lbl = QLabel("")
        self.tags_lbl.setStyleSheet("color: #89dceb; font-weight: bold; font-size: 11px;")
        self.content_layout.addWidget(self.tags_lbl)

        self.question_lbl = QLabel("")
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setStyleSheet("color: #cdd6f4; font-size: 15px; font-weight: 600;")
        self.content_layout.addWidget(self.question_lbl)

        # Image preview
        self.img_lbl = QLabel()
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_lbl.hide()
        self.content_layout.addWidget(self.img_lbl)

        # Separator line
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setStyleSheet("color: #45475a;")
        self.separator.hide()
        self.content_layout.addWidget(self.separator)

        # Answer Section
        self.answer_lbl = QLabel("")
        self.answer_lbl.setWordWrap(True)
        self.answer_lbl.setStyleSheet("color: #a6e3a1; font-size: 14px; font-weight: 500;")
        self.answer_lbl.hide()
        self.content_layout.addWidget(self.answer_lbl)

        self.content_layout.addStretch()
        self.scroll.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll)

        # Action Buttons Layout
        self.actions_layout = QHBoxLayout()

        self.reveal_btn = QPushButton("Reveal Solution [Space]")
        self.reveal_btn.setProperty("class", "primary-btn")
        self.reveal_btn.clicked.connect(self._reveal_answer)
        self.actions_layout.addWidget(self.reveal_btn)

        # FSRS Rating Buttons
        self.rating_widget = QWidget()
        rating_layout = QHBoxLayout(self.rating_widget)
        rating_layout.setContentsMargins(0, 0, 0, 0)
        rating_layout.setSpacing(8)

        self.btn_again = QPushButton("1: Again")
        self.btn_again.setProperty("class", "rating-again")
        self.btn_again.clicked.connect(lambda: self._rate_card(1))

        self.btn_hard = QPushButton("2: Hard")
        self.btn_hard.setProperty("class", "rating-hard")
        self.btn_hard.clicked.connect(lambda: self._rate_card(2))

        self.btn_good = QPushButton("3: Good")
        self.btn_good.setProperty("class", "rating-good")
        self.btn_good.clicked.connect(lambda: self._rate_card(3))

        self.btn_easy = QPushButton("4: Easy")
        self.btn_easy.setProperty("class", "rating-easy")
        self.btn_easy.clicked.connect(lambda: self._rate_card(4))

        rating_layout.addWidget(self.btn_again)
        rating_layout.addWidget(self.btn_hard)
        rating_layout.addWidget(self.btn_good)
        rating_layout.addWidget(self.btn_easy)
        self.rating_widget.hide()
        self.actions_layout.addWidget(self.rating_widget)

        self.main_layout.addLayout(self.actions_layout)

        # Keyboard shortcuts
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self._on_space_pressed)
        QShortcut(QKeySequence("1"), self, lambda: self._rate_card(1) if self.is_answer_revealed else None)
        QShortcut(QKeySequence("2"), self, lambda: self._rate_card(2) if self.is_answer_revealed else None)
        QShortcut(QKeySequence("3"), self, lambda: self._rate_card(3) if self.is_answer_revealed else None)
        QShortcut(QKeySequence("4"), self, lambda: self._rate_card(4) if self.is_answer_revealed else None)

    def _load_current_card(self):
        if not self.cards or self.current_idx >= len(self.cards):
            self._show_completion()
            return

        card = self.cards[self.current_idx]
        self.counter_lbl.setText(f"Card {self.current_idx + 1} / {len(self.cards)}")
        self.tags_lbl.setText(f"🏷 {card.get('tags', 'General').upper()}")
        self.question_lbl.setText(card.get("question", "No question text"))

        img_path = card.get("image_path")
        if img_path and Path(img_path).exists():
            pix = QPixmap(str(img_path))
            if not pix.isNull():
                scaled = pix.scaled(560, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.img_lbl.setPixmap(scaled)
                self.img_lbl.show()
            else:
                self.img_lbl.hide()
        else:
            self.img_lbl.hide()

        self.answer_lbl.setText(f"💡 Solution / Takeaway:\n{card.get('answer', 'Self-recalled item')}")
        self.answer_lbl.hide()
        self.separator.hide()

        self.is_answer_revealed = False
        self.reveal_btn.show()
        self.rating_widget.hide()

        # Timer setup
        self.time_left = 60
        self.progress_bar.setRange(0, self.time_left)
        self.progress_bar.setValue(self.time_left)
        self.progress_bar.setStyleSheet("")
        self.timer.start(1000)

    def _on_tick(self):
        self.time_left -= 1
        self.progress_bar.setValue(self.time_left)
        if self.time_left <= 10:
            self.progress_bar.setStyleSheet(f"QProgressBar::chunk {{ background: {COLOR_RED}; }}")
        if self.time_left <= 0:
            self.timer.stop()
            self._reveal_answer()

    def _on_space_pressed(self):
        if not self.is_answer_revealed:
            self._reveal_answer()

    def _reveal_answer(self):
        self.timer.stop()
        self.is_answer_revealed = True
        self.separator.show()
        self.answer_lbl.show()
        self.reveal_btn.hide()
        self.rating_widget.show()

    def _rate_card(self, rating: int):
        if not self.is_answer_revealed:
            return

        card = self.cards[self.current_idx]
        card_id = card["id"]

        card_dict = {
            "stability": card.get("stability", 1.0),
            "difficulty": card.get("difficulty", 5.0),
            "reps": card.get("reps", 0),
            "lapses": card.get("lapses", 0),
            "last_review": card.get("last_review")
        }

        updated = fsrs.schedule_review(card_dict, rating)
        update_card_fsrs(card_id, updated)

        try:
            winsound.MessageBeep(winsound.MB_OK)
        except Exception:
            pass

        self.current_idx += 1
        self._load_current_card()

    def _show_completion(self):
        self.timer.stop()
        self.counter_lbl.setText("Completed")
        self.progress_bar.hide()
        self.tags_lbl.setText("🎉 DRILL COMPLETE")
        self.question_lbl.setText("Outstanding work! All due items for this session have been reviewed using FSRS spaced repetition.")
        self.img_lbl.hide()
        self.separator.hide()
        self.answer_lbl.hide()
        self.reveal_btn.setText("Close Drill")
        self.reveal_btn.show()
        self.reveal_btn.clicked.disconnect()
        self.reveal_btn.clicked.connect(self.accept)
        self.rating_widget.hide()

def open_recall_dialog():
    dlg = RecallDrillDialog()
    dlg.exec()

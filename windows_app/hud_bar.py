"""
Growth OS for Windows - Floating Cognitive Top Bar (HUD Bar)
Presents real-time exam telemetry, countdowns, targets, and 1-click access to all cognitive tools.
"""

import sys
import os
from datetime import date
from pathlib import Path
from typing import Optional

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFrame,
    QApplication, QMenu
)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QCursor, QAction

from core.db import get_active_targets, get_due_recall_cards, update_target_progress, log_question_solved
from daemons.monk_guardian import monk_guardian
from windows_app.win_observer import windows_observer
from windows_app.styles import (
    HUD_BAR_STYLE, apply_windows_acrylic,
    COLOR_CYAN, COLOR_LAVENDER, COLOR_GREEN, COLOR_RED, COLOR_YELLOW
)
from windows_app.snipper import trigger_snipper
from windows_app.mistake_dialog import open_mistake_dialog
from windows_app.recall_dialog import open_recall_dialog
from windows_app.trainer_dialog import open_trainer_dialog

class HudBar(QWidget):
    """Floating Acrylic Top Bar docked to the top-center of the screen."""
    def __init__(self):
        super().__init__()
        self.setObjectName("HudBar")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(HUD_BAR_STYLE)

        self.drag_position = QPoint()
        self.is_collapsed = False
        self.expanded_width = 820
        self.bar_height = 42

        self._build_ui()
        self._position_top_center()

        # Update Timers
        self.telemetry_timer = QTimer(self)
        self.telemetry_timer.timeout.connect(self.update_telemetry)
        self.telemetry_timer.start(2000)

        # Initial data update
        self.update_telemetry()

    def showEvent(self, event):
        super().showEvent(event)
        apply_windows_acrylic(int(self.winId()))

    def _build_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(12, 4, 12, 4)
        self.main_layout.setSpacing(8)

        # 1. Branding / Grip
        self.brand_lbl = QLabel("⚡")
        self.brand_lbl.setStyleSheet(f"font-size: 15px; color: {COLOR_CYAN}; font-weight: bold;")
        self.brand_lbl.setToolTip("Growth OS Dynamic Island (Drag to move)")
        self.main_layout.addWidget(self.brand_lbl)

        # Container for content when expanded
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)

        # 2. Focus Pill
        self.focus_pill = QFrame()
        self.focus_pill.setProperty("class", "pill")
        focus_box = QHBoxLayout(self.focus_pill)
        focus_box.setContentsMargins(4, 2, 4, 2)
        self.focus_lbl = QLabel("FOCUS: 100%")
        self.focus_lbl.setStyleSheet(f"color: {COLOR_CYAN}; font-weight: bold;")
        focus_box.addWidget(self.focus_lbl)
        self.content_layout.addWidget(self.focus_pill)

        # 3. JEE Countdown Pill
        self.jee_pill = QFrame()
        self.jee_pill.setProperty("class", "pill")
        jee_box = QHBoxLayout(self.jee_pill)
        jee_box.setContentsMargins(4, 2, 4, 2)
        self.jee_lbl = QLabel("⏳ JEE: --d")
        self.jee_lbl.setStyleSheet(f"color: {COLOR_LAVENDER}; font-weight: bold;")
        jee_box.addWidget(self.jee_lbl)
        self.content_layout.addWidget(self.jee_pill)

        # 4. Target Pill
        self.target_pill = QFrame()
        self.target_pill.setProperty("class", "pill")
        tgt_box = QHBoxLayout(self.target_pill)
        tgt_box.setContentsMargins(4, 2, 4, 2)
        self.target_lbl = QLabel("🎯 TARGET: --")
        self.target_lbl.setStyleSheet("color: #fab387; font-weight: bold;")
        tgt_box.addWidget(self.target_lbl)
        self.content_layout.addWidget(self.target_pill)

        # 5. Due Cards Button
        self.due_btn = QPushButton("🧠 DUE: 0")
        self.due_btn.setProperty("class", "pill-btn")
        self.due_btn.setToolTip("Click to launch Timed Active Recall Drill [Alt+Shift+R]")
        self.due_btn.clicked.connect(open_recall_dialog)
        self.content_layout.addWidget(self.due_btn)

        # 6. Snip Button
        self.snip_btn = QPushButton("✂️ SNIP")
        self.snip_btn.setProperty("class", "pill-btn")
        self.snip_btn.setToolTip("Capture screen region to Spaced Recall [Alt+Shift+S]")
        self.snip_btn.clicked.connect(trigger_snipper)
        self.content_layout.addWidget(self.snip_btn)

        # 7. Mistake Button
        self.mistake_btn = QPushButton("📝 MISTAKE")
        self.mistake_btn.setProperty("class", "pill-btn")
        self.mistake_btn.setToolTip("Log an academic error into ledger [Alt+Shift+M]")
        self.mistake_btn.clicked.connect(open_mistake_dialog)
        self.content_layout.addWidget(self.mistake_btn)

        # 8. +1 Solved Button
        self.plus_btn = QPushButton("+1")
        self.plus_btn.setProperty("class", "pill-btn")
        self.plus_btn.setStyleSheet(f"color: {COLOR_GREEN}; font-weight: bold;")
        self.plus_btn.setToolTip("Record 1 solved problem [Alt+Shift+Right]")
        self.plus_btn.clicked.connect(self.quick_increment_solved)
        self.content_layout.addWidget(self.plus_btn)

        # 9. Monk Mode Button
        self.monk_btn = QPushButton("🔒 MONK")
        self.monk_btn.setProperty("class", "pill-btn")
        self.monk_btn.setToolTip("Toggle distraction firewall lock [Alt+Shift+W]")
        self.monk_btn.clicked.connect(self.toggle_monk_mode)
        self.content_layout.addWidget(self.monk_btn)

        self.main_layout.addWidget(self.content_widget)

        # 10. Collapse Toggle Button
        self.collapse_btn = QPushButton("―")
        self.collapse_btn.setFixedSize(20, 20)
        self.collapse_btn.setStyleSheet("border: none; color: #a6adc8; font-weight: bold; background: transparent;")
        self.collapse_btn.setToolTip("Collapse / Expand HUD Bar")
        self.collapse_btn.clicked.connect(self.toggle_collapse)
        self.main_layout.addWidget(self.collapse_btn)

    def _position_top_center(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.expanded_width) // 2
        y = 12
        self.setGeometry(x, y, self.expanded_width, self.bar_height)

    def toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.content_widget.hide()
            self.collapse_btn.setText("+")
            self.resize(60, self.bar_height)
        else:
            self.content_widget.show()
            self.collapse_btn.setText("―")
            self.resize(self.expanded_width, self.bar_height)

    def update_telemetry(self):
        # 1. Focus Score
        score = windows_observer.evaluate_focus()
        self.focus_lbl.setText(f"FOCUS: {score}%")
        if score < 70:
            self.focus_lbl.setStyleSheet(f"color: {COLOR_RED}; font-weight: bold;")
        else:
            self.focus_lbl.setStyleSheet(f"color: {COLOR_CYAN}; font-weight: bold;")

        # 2. JEE Countdown
        today = date.today()
        exam_year = today.year if today.month <= 5 else today.year + 1
        exam_date = date(exam_year, 5, 24)
        days_left = max(0, (exam_date - today).days)
        self.jee_lbl.setText(f"⏳ JEE: {days_left}d")

        # 3. Top Active Target
        targets = get_active_targets()
        if targets:
            t = targets[0]
            pct = int((t['current_val'] / max(1.0, t['target_val'])) * 100)
            title = t['title'][:14] + ".." if len(t['title']) > 14 else t['title']
            self.target_lbl.setText(f"🎯 {title}: {pct}%")
        else:
            self.target_lbl.setText("🎯 TARGET: None")

        # 4. Due Flashcards
        due_cards = get_due_recall_cards()
        self.due_btn.setText(f"🧠 DUE: {len(due_cards)}")

        # 5. Monk Mode Status
        if monk_guardian.is_locked:
            self.monk_btn.setText("🔒 LOCKED")
            self.monk_btn.setProperty("class", "pill-btn monk-active")
        else:
            self.monk_btn.setText("🔒 MONK")
            self.monk_btn.setProperty("class", "pill-btn")
        self.monk_btn.style().polish(self.monk_btn)

    def quick_increment_solved(self):
        targets = get_active_targets()
        if targets:
            update_target_progress(targets[0]['id'], 1.0)
            log_question_solved(target_id=targets[0]['id'], is_correct=True)
        self.update_telemetry()

    def toggle_monk_mode(self):
        if not monk_guardian.is_locked:
            monk_guardian.enable_lockdown()
        else:
            monk_guardian.disable_lockdown()
        self.update_telemetry()

    # Drag window handling
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

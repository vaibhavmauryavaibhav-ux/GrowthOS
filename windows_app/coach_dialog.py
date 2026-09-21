"""
Growth OS for Windows - Socratic AI Sparring Coach Modal
Keybinding: Alt + Shift + D
Interactive mentor that diagnoses roadblocks and asks guiding questions without spoiling solutions.
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QScrollArea, QWidget, QFrame, QFileDialog, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut

from windows_app.styles import DIALOG_STYLE, COLOR_CYAN, COLOR_GREEN, COLOR_LAVENDER, COLOR_MANTLE, COLOR_BASE, COLOR_SURFACE0
from core.ai_coach import chat_socratic_coach

CAPTURES_DIR = Path.home() / ".growth_os" / "captures"

class CoachWorker(QThread):
    response_ready = pyqtSignal(str)

    def __init__(self, messages: List[Dict[str, str]], image_path: Optional[str]):
        super().__init__()
        self.messages = messages
        self.image_path = image_path

    def run(self):
        reply = chat_socratic_coach(self.messages, self.image_path)
        self.response_ready.emit(reply)

class CoachDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Socratic AI Sparring Coach - Growth OS")
        self.setStyleSheet(DIALOG_STYLE)
        self.resize(650, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.messages = []
        self.attached_image: Optional[str] = None

        self._build_ui()
        self._add_mentor_message(
            "Greetings, Scholar. Present the problem you are battling with, or explain where your analysis broke down. "
            "I will not spoil the answer for you—we will dismantle the concept together."
        )

        # Check for recent capture to suggest attachment
        recent_caps = sorted(CAPTURES_DIR.glob("*.png"), key=os.path.getmtime, reverse=True)
        if recent_caps:
            self.attached_image = str(recent_caps[0])
            self._update_attach_badge()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header
        header = QLabel("🤖 Socratic AI Sparring Coach")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        sub_desc = QLabel("Rigorous JEE Advanced intuition builder. It diagnoses traps and guides you to discover the solution.")
        sub_desc.setStyleSheet("color: #a6adc8; font-size: 11px;")
        layout.addWidget(sub_desc)

        # Scroll Area for Chat
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: 1px solid #313244; border-radius: 10px; background-color: #181825; }")

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setSpacing(12)
        self.chat_layout.setContentsMargins(14, 14, 14, 14)
        self.chat_layout.addStretch()

        self.scroll.setWidget(self.chat_container)
        layout.addWidget(self.scroll)

        # Attached Image Badge
        self.attach_row = QHBoxLayout()
        self.attach_badge = QLabel("")
        self.attach_badge.setStyleSheet(f"background-color: {COLOR_MANTLE}; border: 1px solid rgba(137, 220, 235, 100); border-radius: 6px; padding: 4px 8px; color: {COLOR_CYAN}; font-size: 11px;")
        self.attach_badge.hide()

        self.detach_btn = QPushButton("✕")
        self.detach_btn.setFixedSize(20, 20)
        self.detach_btn.setStyleSheet("border: none; color: #f38ba8; font-weight: bold; background: transparent;")
        self.detach_btn.clicked.connect(self._detach_image)
        self.detach_btn.hide()

        self.attach_file_btn = QPushButton("📎 Attach Image/Snip")
        self.attach_file_btn.setProperty("class", "secondary-btn")
        self.attach_file_btn.setStyleSheet("padding: 4px 10px; font-size: 11px;")
        self.attach_file_btn.clicked.connect(self._choose_image)

        self.attach_row.addWidget(self.attach_file_btn)
        self.attach_row.addWidget(self.attach_badge)
        self.attach_row.addWidget(self.detach_btn)
        self.attach_row.addStretch()
        layout.addLayout(self.attach_row)

        # Input Row
        input_row = QHBoxLayout()
        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("Explain where you are stuck, or press Enter to send...")
        self.input_edit.setFixedHeight(75)

        self.send_btn = QPushButton("⚡ Spar")
        self.send_btn.setProperty("class", "primary-btn")
        self.send_btn.setFixedSize(90, 75)
        self.send_btn.clicked.connect(self.send_message)

        input_row.addWidget(self.input_edit)
        input_row.addWidget(self.send_btn)
        layout.addLayout(input_row)

    def _choose_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Problem Image", str(CAPTURES_DIR), "Images (*.png *.jpg *.jpeg)")
        if path:
            self.attached_image = path
            self._update_attach_badge()

    def _detach_image(self):
        self.attached_image = None
        self._update_attach_badge()

    def _update_attach_badge(self):
        if self.attached_image and Path(self.attached_image).exists():
            name = Path(self.attached_image).name
            self.attach_badge.setText(f"📎 Attached: {name}")
            self.attach_badge.show()
            self.detach_btn.show()
        else:
            self.attach_badge.hide()
            self.detach_btn.hide()

    def _add_user_message(self, text: str):
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lbl.setStyleSheet(f"""
            background-color: rgba(137, 220, 235, 30);
            border: 1px solid rgba(137, 220, 235, 100);
            border-radius: 10px;
            padding: 10px 14px;
            color: #ffffff;
            font-size: 13px;
        """)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, lbl)
        self.messages.append({"role": "user", "content": text})
        self._scroll_to_bottom()

    def _add_mentor_message(self, text: str):
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lbl.setStyleSheet(f"""
            background-color: {COLOR_MANTLE};
            border-left: 3px solid {COLOR_GREEN};
            border-radius: 8px;
            padding: 10px 14px;
            color: #cdd6f4;
            font-size: 13px;
        """)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, lbl)
        self.messages.append({"role": "assistant", "content": text})
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        )

    def send_message(self):
        text = self.input_edit.toPlainText().strip()
        if not text and not self.attached_image:
            return

        user_text = text if text else "Please inspect this attached problem diagram."
        self._add_user_message(user_text)
        self.input_edit.clear()

        self.send_btn.setEnabled(False)
        self.send_btn.setText("Thinking...")

        self.worker = CoachWorker(self.messages, self.attached_image)
        self.worker.response_ready.connect(self._on_response_ready)
        self.worker.start()

    def _on_response_ready(self, reply: str):
        self.send_btn.setEnabled(True)
        self.send_btn.setText("⚡ Spar")
        self._add_mentor_message(reply)

def open_coach_dialog():
    dlg = CoachDialog()
    dlg.exec()

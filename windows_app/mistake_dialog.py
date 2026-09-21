"""
Growth OS for Windows - Academic Mistake Ledger Modal
Keybinding: Alt + Shift + M
Logs mock-test and practice errors into SQLite with automatic FSRS card generation.
"""

import sys
import os
import winsound
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QComboBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt

from core.db import log_mistake
from windows_app.styles import DIALOG_STYLE

CAPTURES_DIR = Path.home() / ".growth_os" / "captures"

class MistakeLedgerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Academic Mistake Ledger - Growth OS")
        self.setStyleSheet(DIALOG_STYLE)
        self.resize(520, 480)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(22, 22, 22, 22)

        header = QLabel("📝 Academic Mistake Ledger")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        sub_desc = QLabel("Analyze your error root-cause. It will be scheduled for active spaced review.")
        sub_desc.setStyleSheet("color: #a6adc8; font-size: 11px;")
        layout.addWidget(sub_desc)

        # Subject & Topic
        row1 = QHBoxLayout()
        self.subject_box = QComboBox()
        self.subject_box.addItems(["Physics", "Chemistry", "Mathematics"])
        self.subject_box.setFixedWidth(130)

        self.topic_edit = QLineEdit()
        self.topic_edit.setPlaceholderText("Topic (e.g. Thermodynamics, Definite Integrals)")

        row1.addWidget(self.subject_box)
        row1.addWidget(self.topic_edit)
        layout.addLayout(row1)

        # Error Type
        row2 = QHBoxLayout()
        err_lbl = QLabel("Error Cause:")
        err_lbl.setFixedWidth(80)
        self.error_type_box = QComboBox()
        self.error_type_box.addItems([
            "Conceptual Gap (Didn't understand mechanism/theorem)",
            "Calculation Error (Arithmetic or sign mistake)",
            "Question Misread (Overlooked constraint or 'NOT')",
            "Time Pressure / Rushed Panic",
            "Formula Recall Lapse (Forgot exact relation)"
        ])
        row2.addWidget(err_lbl)
        row2.addWidget(self.error_type_box)
        layout.addLayout(row2)

        # Retrospective Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Retrospective / Core Trap:\nWhy did you make this mistake? What is the correct mental model to remember next time?")
        self.notes_edit.setMinimumHeight(120)
        layout.addWidget(self.notes_edit)

        # Attach Screenshot Checkbox
        self.attach_check = QCheckBox("Attach most recent screenshot from captures")
        self.attach_check.setStyleSheet("color: #cdd6f4;")
        # Check if any captures exist
        recent_caps = sorted(CAPTURES_DIR.glob("*.png"), key=os.path.getmtime, reverse=True)
        if recent_caps:
            self.attach_check.setChecked(True)
            self.latest_cap = recent_caps[0]
            self.attach_check.setText(f"Attach latest screenshot ({self.latest_cap.name})")
        else:
            self.attach_check.setEnabled(False)
            self.latest_cap = None
        layout.addWidget(self.attach_check)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondary-btn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Log Mistake & Schedule Recall")
        save_btn.setProperty("class", "primary-btn")
        save_btn.clicked.connect(self.save_mistake)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def save_mistake(self):
        topic = self.topic_edit.text().strip()
        if not topic:
            QMessageBox.warning(self, "Missing Topic", "Please specify the topic of the mistake.")
            return

        subject = self.subject_box.currentText()
        error_type = self.error_type_box.currentText().split(" (")[0]
        notes = self.notes_edit.toPlainText().strip()
        
        screenshot_path = ""
        if self.attach_check.isChecked() and self.latest_cap and self.latest_cap.exists():
            screenshot_path = str(self.latest_cap)

        log_mistake(
            subject=subject,
            topic=topic,
            error_type=error_type,
            notes=notes,
            screenshot_path=screenshot_path
        )

        try:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass

        self.accept()

def open_mistake_dialog():
    dlg = MistakeLedgerDialog()
    dlg.exec()

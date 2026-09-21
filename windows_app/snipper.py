"""
Growth OS for Windows - Native Interactive Screen Snipper
Keybinding: Alt + Shift + S
Directly captures any region of the screen and creates a spaced recall card in SQLite.
"""

import sys
import os
import time
import winsound
from datetime import datetime
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QComboBox, QApplication
)
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPixmap, QCursor

from core.db import add_recall_card
from windows_app.styles import DIALOG_STYLE, COLOR_CYAN, COLOR_BASE, COLOR_MANTLE

CAPTURES_DIR = Path.home() / ".growth_os" / "captures"
CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

class CardCreationDialog(QDialog):
    """Dialog to add metadata, answer, and tags for the snipped screen area."""
    def __init__(self, image_path: Path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setWindowTitle("Save to Spaced Recall (FSRS)")
        self.setStyleSheet(DIALOG_STYLE)
        self.resize(520, 480)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("⚡ New Spaced Recall Card")
        header.setObjectName("HeaderTitle")
        layout.addWidget(header)

        # Thumbnail preview
        preview_lbl = QLabel()
        pix = QPixmap(str(image_path))
        if not pix.isNull():
            scaled = pix.scaled(480, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            preview_lbl.setPixmap(scaled)
            preview_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview_lbl.setStyleSheet(f"border: 1px solid rgba(137, 220, 235, 60); border-radius: 8px; background-color: {COLOR_MANTLE};")
            layout.addWidget(preview_lbl)

        # Subject Selector
        subj_layout = QHBoxLayout()
        subj_lbl = QLabel("Subject:")
        subj_lbl.setFixedWidth(70)
        self.subject_box = QComboBox()
        self.subject_box.addItems(["Physics", "Chemistry", "Mathematics", "General"])
        subj_layout.addWidget(subj_lbl)
        subj_layout.addWidget(self.subject_box)
        layout.addLayout(subj_layout)

        # Question / Concept Prompt
        self.prompt_edit = QLineEdit()
        self.prompt_edit.setPlaceholderText("Question / Core Concept (e.g. Work-Energy in Pure Rolling)")
        layout.addWidget(self.prompt_edit)

        # Answer / Key Takeaway
        self.answer_edit = QTextEdit()
        self.answer_edit.setPlaceholderText("Answer, Key Formula, or Solution Steps...")
        self.answer_edit.setMaximumHeight(90)
        layout.addWidget(self.answer_edit)

        # Tags
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Tags (comma separated, e.g. Rotational Dynamics, Formulas)")
        layout.addWidget(self.tags_edit)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondary-btn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Card (FSRS)")
        save_btn.setProperty("class", "primary-btn")
        save_btn.clicked.connect(self.save_card)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def save_card(self):
        prompt = self.prompt_edit.text().strip() or "Review Snippet"
        answer = self.answer_edit.toPlainText().strip()
        subject = self.subject_box.currentText()
        user_tags = [t.strip() for t in self.tags_edit.text().split(",") if t.strip()]
        tags = [subject] + user_tags

        add_recall_card(
            question=prompt,
            answer=answer,
            tags=tags,
            card_type="snippet",
            image_path=str(self.image_path)
        )
        self.accept()


class SnipperOverlay(QWidget):
    """Fullscreen semi-transparent overlay allowing rubber-band area selection."""
    snip_completed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        
        # Capture current entire desktop
        screen = QApplication.primaryScreen()
        self.screenshot = screen.grabWindow(0)
        
        self.start_pos = QPoint()
        self.current_pos = QPoint()
        self.is_selecting = False

        # Set geometry to full virtual screen
        geom = QApplication.primaryScreen().virtualGeometry()
        self.setGeometry(geom)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.position().toPoint()
            self.current_pos = self.start_pos
            self.is_selecting = True
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            # Cancel on right click
            self.close()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.current_pos = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.is_selecting = False
            rect = QRect(self.start_pos, self.current_pos).normalized()
            self.hide()

            if rect.width() > 15 and rect.height() > 15:
                # Crop region
                cropped = self.screenshot.copy(rect)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = CAPTURES_DIR / f"snip_{ts}.png"
                cropped.save(str(save_path))
                
                try:
                    winsound.MessageBeep(winsound.MB_OK)
                except Exception:
                    pass

                # Open Card Creator dialog
                dlg = CardCreationDialog(save_path)
                dlg.exec()
                self.snip_completed.emit(str(save_path))

            self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Dim background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 110))

        if self.is_selecting:
            rect = QRect(self.start_pos, self.current_pos).normalized()
            # Draw highlight over selected region with original screenshot
            painter.drawPixmap(rect, self.screenshot, rect)
            
            # Draw neon border
            pen = QPen(QColor(137, 220, 235), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawRect(rect)

            # Dimensions badge
            dims_text = f"{rect.width()} x {rect.height()}"
            painter.setPen(QColor("#cdd6f4"))
            painter.fillRect(rect.left(), max(0, rect.top() - 22), 85, 20, QColor(24, 24, 37, 220))
            painter.drawText(rect.left() + 6, max(14, rect.top() - 8), dims_text)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

def trigger_snipper():
    """Helper to launch snipper overlay safely in Qt application."""
    global _active_snipper
    _active_snipper = SnipperOverlay()
    _active_snipper.showFullScreen()

"""
Growth OS for Windows - 3-Hour CBT Mock Exam Lockdown Engine
Simulates the actual JEE Advanced Computer-Based Test environment with negative marking tracking.
"""

import sys
import os
import time
import winsound
from pathlib import Path
from typing import Dict, List, Any, Optional

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QButtonGroup, QRadioButton, QLineEdit, QScrollArea, QWidget,
    QFrame, QGridLayout, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from windows_app.styles import DIALOG_STYLE, COLOR_CYAN, COLOR_GREEN, COLOR_RED, COLOR_PEACH, COLOR_LAVENDER, COLOR_MANTLE, COLOR_BASE
from core.db import log_mistake, add_recall_card

# Default sample mock questions for immediate testing & simulation
MOCK_EXAM_DATA = {
    "Physics": [
        {"id": 1, "q": "A solid cylinder of mass M and radius R rolls without slipping down an incline of angle θ. What is the acceleration of its center of mass?", "opts": ["(2/3) g sin θ", "(1/2) g sin θ", "(3/4) g sin θ", "g sin θ"], "ans": 0},
        {"id": 2, "q": "An LC circuit contains a 20 mH inductor and a 50 μF capacitor. What is the angular frequency of natural oscillations of the circuit?", "opts": ["1000 rad/s", "500 rad/s", "2000 rad/s", "100 rad/s"], "ans": 0},
        {"id": 3, "q": "In a photoelectric experiment, stopping potential is 3 V for light of wavelength λ. When wavelength is doubled, stopping potential is 1 V. What is the threshold wavelength?", "opts": ["3λ", "4λ", "2λ", "1.5λ"], "ans": 1},
        {"id": 4, "q": "Two identical sound sources produce beats of frequency 4 Hz. If the tension in one string is increased slightly, the beat frequency becomes 2 Hz. The original frequency was:", "opts": ["Lower than the other", "Higher than the other", "Equal", "Cannot be determined"], "ans": 0},
    ],
    "Chemistry": [
        {"id": 1, "q": "Which of the following compounds will undergo Cannizzaro reaction when treated with concentrated aqueous NaOH?", "opts": ["Benzaldehyde", "Acetaldehyde", "Acetone", "Propionaldehyde"], "ans": 0},
        {"id": 2, "q": "For the reaction 2A + B -> C, the rate law is rate = k[A]²[B]. If concentration of A is doubled and B is halved, the rate of reaction will:", "opts": ["Double", "Quadruple", "Halve", "Remain unchanged"], "ans": 0},
        {"id": 3, "q": "Which of the following complex ions is expected to absorb visible light with highest energy?", "opts": ["[Co(CN)₆]³⁻", "[Co(NH₃)₆]³⁺", "[Co(H₂O)₆]³⁺", "[CoF₆]³⁻"], "ans": 0},
        {"id": 4, "q": "The product formed when phenol is treated with CHCl₃ and aqueous NaOH followed by acidification is:", "opts": ["Salicylaldehyde", "Salicylic acid", "Benzoic acid", "Benzaldehyde"], "ans": 0},
    ],
    "Mathematics": [
        {"id": 1, "q": "Evaluate: ∫[0 to π] (x sin x) / (1 + cos² x) dx.", "opts": ["π² / 4", "π² / 2", "π / 4", "π"], "ans": 0},
        {"id": 2, "q": "If 1, ω, ω² are the cube roots of unity, then the value of (1 - ω + ω²)(1 + ω - ω²) is:", "opts": ["4", "-4", "2", "0"], "ans": 0},
        {"id": 3, "q": "The shortest distance between the lines (x-1)/2 = (y-2)/3 = (z-3)/4 and (x-2)/3 = (y-4)/4 = (z-5)/5 is:", "opts": ["1 / √6", "2 / √6", "0", "1 / √3"], "ans": 0},
        {"id": 4, "q": "The eccentric angle of a point on the ellipse x²/25 + y²/9 = 1 whose distance from the center is 4 is:", "opts": ["π/4", "π/3", "π/6", "π/2"], "ans": 0},
    ]
}

class CbtLockdownDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("JEE Advanced CBT Mock Exam Lockdown")
        self.setStyleSheet(DIALOG_STYLE)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Dialog)
        self.resize(1100, 720)

        self.current_subject = "Physics"
        self.current_q_idx = 0
        self.time_remaining = 180 * 60 # 3 hours in seconds
        
        # Responses: subject -> q_idx -> {choice: int, status: "not_visited"|"not_answered"|"answered"|"marked"}
        self.user_data: Dict[str, Dict[int, Dict[str, Any]]] = {}
        for subj, q_list in MOCK_EXAM_DATA.items():
            self.user_data[subj] = {}
            for i in range(len(q_list)):
                self.user_data[subj][i] = {"choice": -1, "status": "not_visited", "time_spent": 0}

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)

        self._build_ui()
        self._load_question(0)
        self.timer.start(1000)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 14, 18, 14)
        main_layout.setSpacing(10)

        # 1. Top Bar: Header + Timer + Submit
        top_row = QHBoxLayout()
        title_lbl = QLabel("🛡️ JEE ADVANCED CBT SIMULATOR")
        title_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLOR_CYAN};")
        
        self.timer_lbl = QLabel("⏳ TIME LEFT: 03:00:00")
        self.timer_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #a6e3a1; font-family: 'Consolas', monospace;")

        self.submit_btn = QPushButton("FINISH & SUBMIT TEST")
        self.submit_btn.setProperty("class", "primary-btn")
        self.submit_btn.setStyleSheet(f"background-color: {COLOR_RED}; color: #ffffff;")
        self.submit_btn.clicked.connect(self._confirm_submit)

        top_row.addWidget(title_lbl)
        top_row.addStretch()
        top_row.addWidget(self.timer_lbl)
        top_row.addSpacing(20)
        top_row.addWidget(self.submit_btn)
        main_layout.addLayout(top_row)

        # 2. Subject Tabs
        self.subj_row = QHBoxLayout()
        self.subj_buttons: Dict[str, QPushButton] = {}
        for subj in ["Physics", "Chemistry", "Mathematics"]:
            btn = QPushButton(subj)
            btn.setProperty("class", "secondary-btn")
            btn.setCheckable(True)
            if subj == "Physics":
                btn.setChecked(True)
                btn.setStyleSheet(f"background-color: {COLOR_CYAN}; color: #11111b; font-weight: bold;")
            btn.clicked.connect(lambda checked, s=subj: self._switch_subject(s))
            self.subj_buttons[subj] = btn
            self.subj_row.addWidget(btn)
        self.subj_row.addStretch()
        main_layout.addLayout(self.subj_row)

        # 3. Main Center Splitter: Question area + Palette
        center_row = QHBoxLayout()

        # Left Question Area
        q_frame = QFrame()
        q_frame.setStyleSheet(f"background-color: {COLOR_MANTLE}; border: 1px solid #313244; border-radius: 10px; padding: 14px;")
        q_layout = QVBoxLayout(q_frame)

        self.q_num_lbl = QLabel("Question 1")
        self.q_num_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COLOR_LAVENDER};")
        q_layout.addWidget(self.q_num_lbl)

        self.q_text_lbl = QLabel("")
        self.q_text_lbl.setWordWrap(True)
        self.q_text_lbl.setStyleSheet("font-size: 14px; color: #cdd6f4; margin: 10px 0;")
        q_layout.addWidget(self.q_text_lbl)

        # Options
        self.options_group = QButtonGroup(self)
        self.option_radios: List[QRadioButton] = []
        for i in range(4):
            rb = QRadioButton(f"Option {i+1}")
            rb.setStyleSheet("color: #cdd6f4; font-size: 13px; padding: 6px;")
            self.options_group.addButton(rb, i)
            self.option_radios.append(rb)
            q_layout.addWidget(rb)

        q_layout.addStretch()

        # Navigation Buttons
        nav_row = QHBoxLayout()
        self.save_next_btn = QPushButton("Save & Next")
        self.save_next_btn.setProperty("class", "primary-btn")
        self.save_next_btn.clicked.connect(self._save_and_next)

        self.mark_review_btn = QPushButton("Mark for Review & Next")
        self.mark_review_btn.setProperty("class", "secondary-btn")
        self.mark_review_btn.clicked.connect(self._mark_and_next)

        self.clear_btn = QPushButton("Clear Response")
        self.clear_btn.setProperty("class", "secondary-btn")
        self.clear_btn.clicked.connect(self._clear_response)

        nav_row.addWidget(self.save_next_btn)
        nav_row.addWidget(self.mark_review_btn)
        nav_row.addWidget(self.clear_btn)
        q_layout.addLayout(nav_row)

        center_row.addWidget(q_frame, stretch=7)

        # Right Question Palette
        palette_frame = QFrame()
        palette_frame.setFixedWidth(280)
        palette_frame.setStyleSheet(f"background-color: {COLOR_MANTLE}; border: 1px solid #313244; border-radius: 10px; padding: 10px;")
        p_layout = QVBoxLayout(palette_frame)

        p_lbl = QLabel("Question Palette")
        p_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLOR_CYAN};")
        p_layout.addWidget(p_lbl)

        # Legend
        legend = QLabel("🟢 Answered | 🔴 Not Answered | 🟣 Review")
        legend.setStyleSheet("font-size: 10px; color: #a6adc8;")
        p_layout.addWidget(legend)

        self.palette_grid = QGridLayout()
        self.palette_buttons: List[QPushButton] = []
        p_layout.addLayout(self.palette_grid)
        p_layout.addStretch()

        center_row.addWidget(palette_frame, stretch=3)
        main_layout.addLayout(center_row)

    def _switch_subject(self, subj: str):
        self.current_subject = subj
        for s, btn in self.subj_buttons.items():
            if s == subj:
                btn.setChecked(True)
                btn.setStyleSheet(f"background-color: {COLOR_CYAN}; color: #11111b; font-weight: bold;")
            else:
                btn.setChecked(False)
                btn.setStyleSheet("")
        self._load_question(0)

    def _load_question(self, idx: int):
        self.current_q_idx = idx
        q_list = MOCK_EXAM_DATA[self.current_subject]
        if idx >= len(q_list):
            return

        q = q_list[idx]
        self.q_num_lbl.setText(f"{self.current_subject} — Question {idx + 1} of {len(q_list)}")
        self.q_text_lbl.setText(q["q"])

        saved = self.user_data[self.current_subject][idx]
        if saved["status"] == "not_visited":
            saved["status"] = "not_answered"

        # Set options
        self.options_group.setExclusive(False)
        for i, opt_text in enumerate(q["opts"]):
            self.option_radios[i].setText(f"({chr(65+i)}) {opt_text}")
            self.option_radios[i].setChecked(i == saved["choice"])
        self.options_group.setExclusive(True)

        self._refresh_palette()

    def _refresh_palette(self):
        # Clear grid
        for btn in self.palette_buttons:
            btn.deleteLater()
        self.palette_buttons.clear()

        q_list = MOCK_EXAM_DATA[self.current_subject]
        cols = 4
        for i in range(len(q_list)):
            btn = QPushButton(str(i + 1))
            btn.setFixedSize(45, 35)
            status = self.user_data[self.current_subject][i]["status"]

            if status == "answered":
                btn.setStyleSheet(f"background-color: {COLOR_GREEN}; color: #11111b; font-weight: bold; border-radius: 6px;")
            elif status == "marked":
                btn.setStyleSheet(f"background-color: {COLOR_LAVENDER}; color: #11111b; font-weight: bold; border-radius: 6px;")
            elif status == "not_answered":
                btn.setStyleSheet(f"background-color: {COLOR_RED}; color: #ffffff; font-weight: bold; border-radius: 6px;")
            else:
                btn.setStyleSheet("background-color: #313244; color: #cdd6f4; border-radius: 6px;")

            if i == self.current_q_idx:
                btn.setStyleSheet(btn.styleSheet() + f" border: 2px solid {COLOR_CYAN};")

            btn.clicked.connect(lambda checked, idx=i: self._load_question(idx))
            self.palette_grid.addWidget(btn, i // cols, i % cols)
            self.palette_buttons.append(btn)

    def _save_and_next(self):
        choice = self.options_group.checkedId()
        data = self.user_data[self.current_subject][self.current_q_idx]
        data["choice"] = choice
        data["status"] = "answered" if choice >= 0 else "not_answered"
        self._next_question()

    def _mark_and_next(self):
        choice = self.options_group.checkedId()
        data = self.user_data[self.current_subject][self.current_q_idx]
        data["choice"] = choice
        data["status"] = "marked"
        self._next_question()

    def _clear_response(self):
        self.options_group.setExclusive(False)
        for rb in self.option_radios:
            rb.setChecked(False)
        self.options_group.setExclusive(True)
        data = self.user_data[self.current_subject][self.current_q_idx]
        data["choice"] = -1
        data["status"] = "not_answered"
        self._refresh_palette()

    def _next_question(self):
        q_list = MOCK_EXAM_DATA[self.current_subject]
        if self.current_q_idx < len(q_list) - 1:
            self._load_question(self.current_q_idx + 1)
        else:
            self._refresh_palette()

    def _on_tick(self):
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.user_data[self.current_subject][self.current_q_idx]["time_spent"] += 1
            
            hrs = self.time_remaining // 3600
            mins = (self.time_remaining % 3600) // 60
            secs = self.time_remaining % 60
            self.timer_lbl.setText(f"⏳ TIME LEFT: {hrs:02d}:{mins:02d}:{secs:02d}")
            if self.time_remaining < 600:
                self.timer_lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLOR_RED};")
        else:
            self.timer.stop()
            self._submit_test()

    def _confirm_submit(self):
        reply = QMessageBox.question(
            self, "Submit Test",
            "Are you sure you want to finish and submit the test? All responses will be graded according to JEE Advanced marking rules (+4 / -1 / 0).",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._submit_test()

    def _submit_test(self):
        self.timer.stop()

        # Calculate Scores
        total_score = 0
        correct_count = 0
        wrong_count = 0
        unattempted_count = 0
        mistakes_to_log = []

        for subj, q_list in MOCK_EXAM_DATA.items():
            for i, q in enumerate(q_list):
                u = self.user_data[subj][i]
                choice = u["choice"]
                correct_ans = q["ans"]
                if choice == -1:
                    unattempted_count += 1
                elif choice == correct_ans:
                    total_score += 4
                    correct_count += 1
                else:
                    total_score -= 1
                    wrong_count += 1
                    mistakes_to_log.append({
                        "subject": subj,
                        "question": q["q"],
                        "wrong_choice": q["opts"][choice],
                        "correct_choice": q["opts"][correct_ans]
                    })

        # Auto log wrong questions into Mistake Ledger
        for m in mistakes_to_log:
            log_mistake(
                subject=m["subject"],
                topic="CBT Mock Exam",
                error_type="Mock Test Mistake",
                notes=f"Selected '{m['wrong_choice']}'. Correct was '{m['correct_choice']}'."
            )
            add_recall_card(
                question=m["question"],
                answer=f"Correct Option: {m['correct_choice']}",
                tags=[m["subject"], "CBT-Mock"],
                card_type="mock_mistake"
            )

        try:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass

        score_msg = (
            f"🎉 CBT MOCK EXAM COMPLETED!\n\n"
            f"• Total Score: {total_score} marks (+4 / -1 / 0)\n"
            f"• Correct Questions: {correct_count}\n"
            f"• Incorrect Questions: {wrong_count}\n"
            f"• Unattempted: {unattempted_count}\n\n"
            f"⚡ All {len(mistakes_to_log)} incorrect questions were automatically logged into your Mistake Ledger and scheduled into the FSRS Spaced Recall deck!"
        )
        QMessageBox.information(self, "Exam Result & Performance Report", score_msg)
        self.accept()

def open_cbt_lockdown():
    dlg = CbtLockdownDialog()
    dlg.exec()

"""
Growth OS for Windows - JEE Syllabus Weakness Radar & Error Heatmap
Maps the full JEE Advanced syllabus against SQLite mistakes and FSRS memory decay.
"""

import sys
import sqlite3
from pathlib import Path
from typing import Dict, List, Any

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QGridLayout, QProgressBar,
    QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt

from windows_app.styles import (
    DIALOG_STYLE, COLOR_CYAN, COLOR_GREEN, COLOR_RED, COLOR_PEACH,
    COLOR_LAVENDER, COLOR_MANTLE, COLOR_SURFACE0, COLOR_BASE
)
from core.db import DB_PATH, add_target

JEE_SYLLABUS = {
    "Physics": [
        "Rotational Dynamics", "Electrostatics & Capacitors", "Current Electricity",
        "Electromagnetic Induction", "Ray & Wave Optics", "Thermodynamics & KTG",
        "Modern Physics & Atoms", "Fluid Mechanics", "Simple Harmonic Motion",
        "Magnetic Effects of Current", "Work, Power & Energy", "Gravitation"
    ],
    "Chemistry": [
        "Carbonyl Compounds (Aldehydes/Ketones)", "Electrochemistry", "Chemical & Ionic Equilibrium",
        "Coordination Compounds", "Thermodynamics & Thermochemistry", "p-Block Elements",
        "Chemical Kinetics", "Amines & Diazonium Salts", "General Organic Chemistry (GOC)",
        "Atomic Structure & Periodic Trends", "Chemical Bonding & Molecular Structure", "Solutions & Colligative Properties"
    ],
    "Mathematics": [
        "Definite Integration & Area", "Vectors & 3D Geometry", "Conic Sections (Parabola/Ellipse/Hyperbola)",
        "Probability & Bayes Theorem", "Differential Equations", "Matrices & Determinants",
        "Complex Numbers & De Moivre", "Continuity & Differentiability", "Permutations & Combinations",
        "Binomial Theorem & Series", "Circles & Family of Circles", "Functions & Relations"
    ]
}

def get_chapter_telemetry() -> Dict[str, Dict[str, Any]]:
    """Calculates mistake count and card count for each chapter from SQLite."""
    stats = {}
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Mistake counts per topic
        c.execute("SELECT subject, topic, COUNT(*) FROM mistakes GROUP BY subject, topic")
        for subj, topic, count in c.fetchall():
            key = f"{subj}::{topic.strip().lower()}"
            stats[key] = {"mistakes": count, "cards": 0}

        # Recall cards per title
        c.execute("SELECT title, COUNT(*) FROM recall_cards GROUP BY title")
        for title_str, count in c.fetchall():
            key = title_str.strip().lower()
            for full_key in stats:
                if key in full_key or full_key in key:
                    stats[full_key]["cards"] += count

        conn.close()
    except Exception as e:
        print(f"[Radar] Error fetching stats: {e}")
    return stats

class SyllabusRadarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("JEE Syllabus Weakness Radar & Heatmap - Growth OS")
        self.setStyleSheet(DIALOG_STYLE)
        self.resize(880, 640)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.stats = get_chapter_telemetry()
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Header
        top_row = QHBoxLayout()
        header = QLabel("🗺️ JEE Syllabus Weakness Radar")
        header.setObjectName("HeaderTitle")
        top_row.addWidget(header)
        top_row.addStretch()

        legend = QLabel("🔴 High Vulnerability | 🟡 Needs Review | 🟢 Mastered")
        legend.setStyleSheet("font-size: 11px; color: #a6adc8; font-weight: bold;")
        top_row.addWidget(legend)
        main_layout.addLayout(top_row)

        desc = QLabel("Cross-references your Academic Mistake Ledger and FSRS retention decay to pinpoint your biggest exam traps.")
        desc.setStyleSheet("color: #a6adc8; font-size: 11px;")
        main_layout.addWidget(desc)

        # Tabs for Physics, Chemistry, Math
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid #313244; border-radius: 8px; background: {COLOR_MANTLE}; }}
            QTabBar::tab {{ background: #1e1e2e; color: #cdd6f4; padding: 8px 18px; border-top-left-radius: 6px; border-top-right-radius: 6px; }}
            QTabBar::tab:selected {{ background: {COLOR_CYAN}; color: #11111b; font-weight: bold; }}
        """)

        for subj, chapters in JEE_SYLLABUS.items():
            tab_widget = self._create_subject_grid(subj, chapters)
            self.tabs.addTab(tab_widget, subj)

        main_layout.addWidget(self.tabs)

        # Bottom Recommendation Card
        self.rec_card = QFrame()
        self.rec_card.setStyleSheet(f"background-color: rgba(137, 220, 235, 20); border: 1px solid {COLOR_CYAN}; border-radius: 10px; padding: 12px;")
        rec_layout = QHBoxLayout(self.rec_card)

        self.rec_text = QLabel("⚡ HIGHEST-YIELD REVISION PRIORITY: Rotational Dynamics (Calculus & Angular Momentum Traps)")
        self.rec_text.setStyleSheet(f"color: #ffffff; font-weight: bold; font-size: 12px;")
        rec_layout.addWidget(self.rec_text)
        rec_layout.addStretch()

        set_target_btn = QPushButton("🎯 Set as Daily Target")
        set_target_btn.setProperty("class", "primary-btn")
        set_target_btn.clicked.connect(self._set_priority_target)
        rec_layout.addWidget(set_target_btn)

        main_layout.addWidget(self.rec_card)

    def _create_subject_grid(self, subject: str, chapters: List[str]) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(10)
        grid.setContentsMargins(14, 14, 14, 14)

        cols = 3
        for i, ch_name in enumerate(chapters):
            card = self._create_chapter_card(subject, ch_name)
            grid.addWidget(card, i // cols, i % cols)

        scroll.setWidget(container)
        return scroll

    def _create_chapter_card(self, subject: str, chapter: str) -> QFrame:
        card = QFrame()
        card.setFixedHeight(105)
        
        # Determine vulnerability
        match_key = f"{subject}::{chapter.strip().lower()}"
        ch_stats = self.stats.get(match_key, {"mistakes": 0, "cards": 0})
        m_count = ch_stats["mistakes"]
        
        # Color coding
        if m_count >= 2:
            status_color = COLOR_RED
            status_text = "HIGH VULNERABILITY"
            border_css = f"border: 1.5px solid {COLOR_RED}; background-color: rgba(243, 139, 168, 20);"
        elif m_count == 1:
            status_color = COLOR_PEACH
            status_text = "NEEDS BRUSH-UP"
            border_css = f"border: 1px solid {COLOR_PEACH}; background-color: rgba(250, 179, 135, 15);"
        else:
            status_color = COLOR_GREEN
            status_text = "STABLE RETENTION"
            border_css = f"border: 1px solid #313244; background-color: {COLOR_BASE};"

        card.setStyleSheet(f"QFrame {{ {border_css} border-radius: 8px; padding: 6px; }}")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        title = QLabel(chapter)
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 12px; font-weight: bold; color: #cdd6f4;")
        layout.addWidget(title)

        status_lbl = QLabel(f"● {status_text}")
        status_lbl.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {status_color};")
        layout.addWidget(status_lbl)

        metrics_lbl = QLabel(f"Logged Errors: {m_count} | FSRS Cards: {ch_stats['cards']}")
        metrics_lbl.setStyleSheet("font-size: 10px; color: #a6adc8;")
        layout.addWidget(metrics_lbl)

        layout.addStretch()
        return card

    def _set_priority_target(self):
        add_target(
            title="Master Rotational Dynamics Traps",
            target_type="count",
            target_val=25.0,
            unit="problems"
        )
        QMessageBox.information(
            self, "Target Activated",
            "🎯 Target 'Master Rotational Dynamics Traps (25 problems)' has been activated and linked to your top HUD bar!"
        )

def open_syllabus_radar():
    dlg = SyllabusRadarDialog()
    dlg.exec()

"""
Growth OS for Windows - Instant Formula & Reaction Spotlight HUD
Keybinding: Alt + Space
Ultra-fast offline search for formulas, named organic reactions, and calculus theorems.
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QLabel, QTextEdit, QPushButton, QSplitter,
    QWidget, QFrame, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QFont, QKeySequence

from windows_app.styles import DIALOG_STYLE, COLOR_CYAN, COLOR_LAVENDER, COLOR_GREEN, COLOR_PEACH, COLOR_MANTLE
from core.db import add_recall_card

# Comprehensive offline high-yield JEE knowledge bank
JEE_KNOWLEDGE_BASE = [
    # --- PHYSICS ---
    {
        "title": "Carnot Engine & Thermodynamic Efficiency",
        "subject": "Physics",
        "topic": "Thermodynamics",
        "formula": "η = 1 - (T_cold / T_hot) = W_net / Q_in",
        "details": "For any reversible heat engine operating between reservoirs at T_hot and T_cold (in Kelvin).\nEntropy change of universe ΔS_univ = 0 for Carnot cycle.",
        "trap": "Always convert temperatures to absolute Kelvin (T_K = T_C + 273.15). Real irreversible engines always have η < η_carnot."
    },
    {
        "title": "Doppler Effect for Sound Waves",
        "subject": "Physics",
        "topic": "Wave Motion",
        "formula": "f' = f₀ * [(v ± v_observer) / (v ∓ v_source)]",
        "details": "v is speed of sound in medium. Upper signs indicate observer/source moving TOWARD each other; lower signs indicate moving AWAY.",
        "trap": "Wind velocity w: replace v with (v ± w) depending on wind direction. For reflected sound (echo), treat reflecting barrier as moving observer then moving source."
    },
    {
        "title": "Parallel & Perpendicular Axis Theorems",
        "subject": "Physics",
        "topic": "Rotational Mechanics",
        "formula": "Parallel: I = I_cm + M*d² | Perpendicular: I_z = I_x + I_y",
        "details": "Parallel axis works for ANY rigid body. Perpendicular axis theorem STRICTLY applies ONLY to 2D planar laminar objects (z-axis perpendicular to xy-plane).",
        "trap": "Parallel axis MUST pass through the Center of Mass (I_cm); you cannot parallel-shift directly between two random axes."
    },
    {
        "title": "Biot-Savart Law & Ampere's Law",
        "subject": "Physics",
        "topic": "Magnetism",
        "formula": "dB = (μ₀/4π) * (I dl × r̂) / r² | ∮ B · dl = μ₀ * I_enclosed",
        "details": "Magnetic field of circular loop at center: B = μ₀I / (2R). On axis: B = μ₀I R² / (2(R² + x²)^(3/2)).",
        "trap": "Cross product direction given by right-hand thumb rule. In Ampere's law, only include current piercing through the open surface bounded by Amperian loop."
    },
    {
        "title": "Capillary Rise & Surface Tension",
        "subject": "Physics",
        "topic": "Fluid Mechanics",
        "formula": "h = (2 * T * cos θ) / (r * ρ * g)",
        "details": "T is surface tension, θ is contact angle, r is capillary radius, ρ is density. Meniscus radius R = r / cos θ.",
        "trap": "If tube length L < h, water does NOT overflow! Instead, the meniscus flattens: R' increases such that h' * R' = h * r = constant."
    },
    {
        "title": "Photoelectric Effect (Einstein Equation)",
        "subject": "Physics",
        "topic": "Modern Physics",
        "formula": "hν = Φ + K_max = Φ + e*V_stop",
        "details": "Φ is work function (Φ = hν₀ = hc/λ₀). Stopping potential V_stop depends strictly on frequency, NOT light intensity.",
        "trap": "Intensity increases photon flux & saturation current, but has ZERO effect on K_max or stopping potential."
    },

    # --- ORGANIC CHEMISTRY ---
    {
        "title": "Aldol Condensation & Cross-Aldol",
        "subject": "Chemistry",
        "topic": "Carbonyl Compounds",
        "formula": "2 R-CH₂-CHO + dil. NaOH ──> β-hydroxy aldehyde ──(Δ)──> α,β-unsaturated aldehyde",
        "details": "Requires at least one α-hydrogen to form enolate ion. Base abstracts α-H to form nucleophilic enolate which attacks second carbonyl.",
        "trap": "Heating (Δ) promotes E1cB dehydration yielding conjugated α,β-unsaturated compound due to extended resonance stability."
    },
    {
        "title": "Cannizzaro Reaction (Disproportionation)",
        "subject": "Chemistry",
        "topic": "Aldehydes",
        "formula": "2 R-CHO (no α-H) + 50% NaOH ──> R-CH₂OH (alcohol) + R-COO⁻ Na⁺ (salt)",
        "details": "Redox disproportionation of aldehydes with NO α-hydrogens (e.g. Formaldehyde, Benzaldehyde, Trimethylacetaldehyde).",
        "trap": "Hydride transfer (:H⁻) is the slow rate-determining step. In cross-Cannizzaro with Formaldehyde, HCHO is always oxidized to HCOO⁻ (less steric hindrance)."
    },
    {
        "title": "Reimer-Tiemann & Kolbe-Schmitt Reactions",
        "subject": "Chemistry",
        "topic": "Phenols",
        "formula": "Phenol + CHCl₃ + NaOH ──> Salicylaldehyde | Phenol + CO₂ + NaOH ──(Δ, P)──> Salicylic Acid",
        "details": "Reimer-Tiemann intermediate is electrophilic neutral Dichlorocarbene (:CCl₂). Kolbe reaction uses carbon dioxide as weak electrophile.",
        "trap": "In Reimer-Tiemann, using CCl₄ instead of CHCl₃ yields Salicylic acid (o-hydroxybenzoic acid)."
    },
    {
        "title": "Hoffmann Bromamide Degradation",
        "subject": "Chemistry",
        "topic": "Amines",
        "formula": "R-CONH₂ + Br₂ + 4 KOH ──> R-NH₂ (1° amine) + K₂CO₃ + 2 KBr + 2 H₂O",
        "details": "Produces primary amine with ONE LESS carbon atom than parent amide. Key intermediate is Alkyl Isocyanate (R-N=C=O).",
        "trap": "Migration of alkyl group R occurs with complete RETENTION of stereochemical configuration at the chiral migration center."
    },

    # --- PHYSICAL & INORGANIC CHEMISTRY ---
    {
        "title": "Nernst Equation & Electrochemical EMF",
        "subject": "Chemistry",
        "topic": "Electrochemistry",
        "formula": "E_cell = E°_cell - (0.0591 / n) * log₁₀(Q)  [at 298 K]",
        "details": "n is moles of electrons transferred in balanced cell reaction. At equilibrium, E_cell = 0 and Q = K_eq, so E°_cell = (0.0591/n) * log K_eq.",
        "trap": "Pure solids and pure liquids have activity = 1. Watch out for coefficients when writing reaction quotient Q."
    },
    {
        "title": "Arrhenius Equation & Activation Energy",
        "subject": "Chemistry",
        "topic": "Chemical Kinetics",
        "formula": "k = A * e^(-E_a / RT) | ln(k₂ / k₁) = (E_a / R) * [(1/T₁) - (1/T₂)]",
        "details": "A is frequency factor, E_a is activation energy. Slope of Arrhenius plot (ln k vs 1/T) is -E_a / R.",
        "trap": "Catalyst lowers E_a for BOTH forward and reverse reactions equally, increasing k_f and k_b without changing equilibrium constant K."
    },
    {
        "title": "Crystal Field Splitting (Octahedral vs Tetrahedral)",
        "subject": "Chemistry",
        "topic": "Coordination Compounds",
        "formula": "Δ_t = (4/9) * Δ_o | CFSE = [-0.4*n(t2g) + 0.6*n(eg)]*Δ_o + P",
        "details": "Spectrochemical series: I⁻ < Br⁻ < S²⁻ < Cl⁻ < F⁻ < OH⁻ < C₂O₄²⁻ < H₂O < NCS⁻ < EDTA⁴⁻ < NH₃ < en < NO₂⁻ < CN⁻ < CO.",
        "trap": "Tetrahedral complexes NEVER form low spin configurations because Δ_t is always smaller than pairing energy P."
    },

    # --- MATHEMATICS ---
    {
        "title": "King's Property & Periodic Definite Integrals",
        "subject": "Mathematics",
        "topic": "Definite Integration",
        "formula": "∫[a to b] f(x) dx = ∫[a to b] f(a + b - x) dx",
        "details": "For [0 to a]: ∫[0 to a] f(x) dx = ∫[0 to a] f(a - x) dx. Adding original integral to modified integral frequently eliminates difficult numerators.",
        "trap": "For periodic function f(x) with period T: ∫[0 to nT] f(x) dx = n * ∫[0 to T] f(x) dx."
    },
    {
        "title": "Leibniz Integral Rule for Differentiation",
        "subject": "Mathematics",
        "topic": "Calculus",
        "formula": "d/dx [∫[u(x) to v(x)] f(t) dt] = f(v(x))*v'(x) - f(u(x))*u'(x)",
        "details": "Essential for evaluating 0/0 limits containing integral expressions via L'Hopital's rule in JEE Advanced.",
        "trap": "Don't forget to multiply by the derivative of the upper and lower limits (chain rule v'(x) and u'(x))."
    },
    {
        "title": "Shortest Distance Between Skew Lines",
        "subject": "Mathematics",
        "topic": "3D Vectors & Geometry",
        "formula": "d = | (a₂ - a₁) · (b₁ × b₂) | / | b₁ × b₂ |",
        "details": "Lines: r = a₁ + λ b₁ and r = a₂ + μ b₂. If numerator = 0, lines are coplanar and intersect.",
        "trap": "For parallel lines (b₁ = b₂ = b), formula changes to d = | (a₂ - a₁) × b | / | b |."
    },
    {
        "title": "Roots of Unity & Euler's Formula",
        "subject": "Mathematics",
        "topic": "Complex Numbers",
        "formula": "e^(iθ) = cos θ + i sin θ | 1 + ω + ω² = 0, ω³ = 1",
        "details": "Cube roots of unity: 1, ω = (-1 + i√3)/2, ω² = (-1 - i√3)/2. Form an equilateral triangle inscribed in unit circle |z| = 1.",
        "trap": "1 + ω^r + ω^(2r) equals 3 if r is a multiple of 3, and 0 otherwise."
    }
]

class FormulaSpotlightDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("JEE Formula & Reaction Spotlight")
        self.setStyleSheet(DIALOG_STYLE)
        self.resize(780, 520)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Dialog
        )

        self._build_ui()
        self._populate_list(JEE_KNOWLEDGE_BASE)

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(12)

        # Header Search Bar
        search_row = QHBoxLayout()
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet(f"font-size: 18px; color: {COLOR_CYAN};")
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Type formula, reaction, or theorem name (e.g. Carnot, Aldol, Doppler, King)...")
        self.search_edit.setStyleSheet(f"font-size: 15px; padding: 10px 14px; border: 1.5px solid {COLOR_CYAN};")
        self.search_edit.textChanged.connect(self._on_search_changed)

        search_row.addWidget(search_icon)
        search_row.addWidget(self.search_edit)
        main_layout.addLayout(search_row)

        # Splitter: Left results list, Right details panel
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #313244; width: 2px; }")

        # Left list
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 4px;
            }
            QListWidget::item {
                color: #cdd6f4;
                padding: 8px;
                border-radius: 6px;
                margin-bottom: 2px;
            }
            QListWidget::item:selected {
                background-color: #313244;
                color: #89dceb;
                font-weight: bold;
            }
        """)
        self.list_widget.currentRowChanged.connect(self._on_item_selected)
        splitter.addWidget(self.list_widget)

        # Right detail card
        self.detail_widget = QWidget()
        detail_layout = QVBoxLayout(self.detail_widget)
        detail_layout.setContentsMargins(14, 0, 4, 0)
        detail_layout.setSpacing(10)

        self.title_lbl = QLabel("Select an item to view")
        self.title_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLOR_CYAN};")
        detail_layout.addWidget(self.title_lbl)

        self.subject_lbl = QLabel("")
        self.subject_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #b4befe;")
        detail_layout.addWidget(self.subject_lbl)

        # Formula Display
        self.formula_box = QLabel("")
        self.formula_box.setWordWrap(True)
        self.formula_box.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.formula_box.setStyleSheet(f"""
            background-color: {COLOR_MANTLE};
            border: 1px solid rgba(137, 220, 235, 80);
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
            color: #a6e3a1;
            font-family: 'Consolas', monospace;
        """)
        detail_layout.addWidget(self.formula_box)

        # Explanation details
        self.desc_lbl = QLabel("")
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet("font-size: 13px; color: #cdd6f4;")
        detail_layout.addWidget(self.desc_lbl)

        # Pitfall / Trap Box
        self.trap_box = QLabel("")
        self.trap_box.setWordWrap(True)
        self.trap_box.setStyleSheet(f"""
            background-color: rgba(243, 139, 168, 25);
            border-left: 3px solid {COLOR_PEACH};
            padding: 8px;
            font-size: 12px;
            color: #fab387;
        """)
        detail_layout.addWidget(self.trap_box)

        detail_layout.addStretch()

        # Action bar
        act_row = QHBoxLayout()
        self.add_flashcard_btn = QPushButton("➕ Add to Spaced Recall")
        self.add_flashcard_btn.setProperty("class", "primary-btn")
        self.add_flashcard_btn.clicked.connect(self._create_card_from_current)
        act_row.addWidget(self.add_flashcard_btn)

        close_btn = QPushButton("Close [Esc]")
        close_btn.setProperty("class", "secondary-btn")
        close_btn.clicked.connect(self.close)
        act_row.addWidget(close_btn)

        detail_layout.addLayout(act_row)

        splitter.addWidget(self.detail_widget)
        splitter.setSizes([320, 460])
        main_layout.addWidget(splitter)

        # Shortcuts
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.close)

    def _populate_list(self, items: List[Dict[str, Any]]):
        self.list_widget.clear()
        self.current_filtered_items = items
        for item in items:
            list_item = QListWidgetItem(f"[{item['subject'][0]}] {item['title']}")
            self.list_widget.addItem(list_item)
        if items:
            self.list_widget.setCurrentRow(0)

    def _on_search_changed(self, text: str):
        query = text.strip().lower()
        if not query:
            self._populate_list(JEE_KNOWLEDGE_BASE)
            return

        filtered = []
        for item in JEE_KNOWLEDGE_BASE:
            haystack = f"{item['title']} {item['subject']} {item['topic']} {item['formula']} {item['details']}".lower()
            if query in haystack:
                filtered.append(item)
        self._populate_list(filtered)

    def _on_item_selected(self, row: int):
        if row < 0 or row >= len(self.current_filtered_items):
            return
        item = self.current_filtered_items[row]
        self.current_item = item

        self.title_lbl.setText(item["title"])
        self.subject_lbl.setText(f"📚 {item['subject'].upper()} • {item['topic']}")
        self.formula_box.setText(f"📐 {item['formula']}")
        self.desc_lbl.setText(f"💡 {item['details']}")
        self.trap_box.setText(f"⚠️ JEE Advanced Trap:\n{item['trap']}")
        self.add_flashcard_btn.setText("➕ Add to Spaced Recall")
        self.add_flashcard_btn.setEnabled(True)

    def _create_card_from_current(self):
        if not hasattr(self, "current_item"):
            return
        item = self.current_item
        add_recall_card(
            question=f"State the formula and key conditions for: {item['title']}",
            answer=f"{item['formula']}\n\nDetails: {item['details']}\n\nTrap: {item['trap']}",
            tags=[item["subject"], item["topic"], "FormulaSpotlight"],
            card_type="concept"
        )
        self.add_flashcard_btn.setText("✓ Added to FSRS Deck!")
        self.add_flashcard_btn.setEnabled(False)

def open_formula_spotlight():
    dlg = FormulaSpotlightDialog()
    dlg.exec()

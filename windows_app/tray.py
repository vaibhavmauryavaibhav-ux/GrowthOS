"""
Growth OS for Windows - System Tray Integration
Resides in the Windows Taskbar Notification Area with quick shortcuts & autostart toggle.
"""

import sys
import winreg
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt

from windows_app.snipper import trigger_snipper
from windows_app.mistake_dialog import open_mistake_dialog
from windows_app.recall_dialog import open_recall_dialog
from windows_app.trainer_dialog import open_trainer_dialog
from windows_app.formula_spotlight import open_formula_spotlight
from windows_app.coach_dialog import open_coach_dialog
from windows_app.cbt_lockdown import open_cbt_lockdown
from windows_app.syllabus_radar import open_syllabus_radar

RUN_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "GrowthOS"

def is_autostart_enabled() -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_REG_KEY, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

def set_autostart_enabled(enable: bool):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_REG_KEY, 0, winreg.KEY_WRITE)
        if enable:
            exe_path = sys.executable
            if not getattr(sys, 'frozen', False):
                script_path = str(Path(__file__).resolve().parent.parent / "run_windows.py")
                cmd = f'"{exe_path}" "{script_path}"'
            else:
                cmd = f'"{exe_path}"'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as e:
        print(f"[Tray] Autostart registry toggle error: {e}")

def create_tray_icon() -> QIcon:
    """Generates a crisp 64x64 neon cyan lightning bolt tray icon."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Dark circular backdrop
    painter.setBrush(QColor(24, 24, 37))
    painter.setPen(QColor(137, 220, 235))
    painter.drawEllipse(2, 2, 60, 60)

    # Lightning bolt symbol
    font = QFont("Segoe UI", 26, QFont.Weight.Bold)
    painter.setFont(font)
    painter.setPen(QColor(137, 220, 235))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "⚡")
    painter.end()

    return QIcon(pixmap)

class WindowsSystemTray(QSystemTrayIcon):
    def __init__(self, hud_bar, parent=None):
        icon = create_tray_icon()
        super().__init__(icon, parent)
        self.hud_bar = hud_bar
        self.setToolTip("Growth OS - Cognitive Cockpit for Windows")

        self._build_menu()
        self.activated.connect(self._on_activated)

    def _build_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e2e;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                color: #cdd6f4;
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #313244;
                color: #89dceb;
            }
            QMenu::separator {
                height: 1px;
                background: #313244;
                margin: 4px 8px;
            }
        """)

        # 1. Toggle HUD
        toggle_hud_act = menu.addAction("⚡ Toggle Focus HUD Bar")
        toggle_hud_act.triggered.connect(self._toggle_hud)

        menu.addSeparator()

        # 2. Tool launchers
        snip_act = menu.addAction("✂️ Quick Snip to Recall [Alt+Shift+S]")
        snip_act.triggered.connect(trigger_snipper)

        mistake_act = menu.addAction("📝 Mistake Ledger [Alt+Shift+M]")
        mistake_act.triggered.connect(open_mistake_dialog)

        recall_act = menu.addAction("🧠 Active Recall Drill [Alt+Shift+R]")
        recall_act.triggered.connect(open_recall_dialog)

        spotlight_act = menu.addAction("🔍 Formula & Reaction Spotlight [Alt+Space]")
        spotlight_act.triggered.connect(open_formula_spotlight)

        coach_act = menu.addAction("🤖 Socratic AI Sparring Coach [Alt+Shift+D]")
        coach_act.triggered.connect(open_coach_dialog)

        cbt_act = menu.addAction("🛡️ 3-Hour CBT Mock Exam Simulator")
        cbt_act.triggered.connect(open_cbt_lockdown)

        radar_act = menu.addAction("🗺️ JEE Syllabus Weakness Radar")
        radar_act.triggered.connect(open_syllabus_radar)

        trainer_act = menu.addAction("⏱ Question Trainer")
        trainer_act.triggered.connect(open_trainer_dialog)

        audio_act = menu.addAction("🎧 Toggle Focus Audio (40Hz / Brown) [Alt+Shift+A]")
        audio_act.triggered.connect(self.hud_bar.toggle_audio)

        monk_act = menu.addAction("🔒 Toggle Monk Mode [Alt+Shift+W]")
        monk_act.triggered.connect(self.hud_bar.toggle_monk_mode)

        menu.addSeparator()

        # 3. Backup & Export
        backup_act = menu.addAction("💾 Backup & Export Deck / Ledger")
        backup_act.triggered.connect(self._run_backup_export)

        # 4. Autostart checkbox
        self.autostart_act = menu.addAction("🚀 Start with Windows")
        self.autostart_act.setCheckable(True)
        self.autostart_act.setChecked(is_autostart_enabled())
        self.autostart_act.triggered.connect(self._toggle_autostart)

        menu.addSeparator()

        # 5. Exit
        exit_act = menu.addAction("Exit Growth OS")
        exit_act.triggered.connect(QApplication.instance().quit)

        self.setContextMenu(menu)

    def _run_backup_export(self):
        from PyQt6.QtWidgets import QMessageBox
        from core.backup_export import run_full_backup_and_export
        res = run_full_backup_and_export()
        QMessageBox.information(
            None, "Backup & Export Complete",
            f"✅ Academic Data Exported Successfully!\n\n"
            f"• Anki Cards TSV: {res['anki_tsv']}\n"
            f"• Mistake Ledger CSV: {res['mistake_csv']}\n"
            f"• Database Snapshot: {res['db_backup']}\n\n"
            f"Opening export directory..."
        )
        if sys.platform == "win32":
            os.startfile(res["export_dir"])

    def _toggle_hud(self):
        if self.hud_bar.isVisible():
            self.hud_bar.hide()
        else:
            self.hud_bar.show()

    def _toggle_autostart(self):
        enabled = self.autostart_act.isChecked()
        set_autostart_enabled(enabled)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick or reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._toggle_hud()

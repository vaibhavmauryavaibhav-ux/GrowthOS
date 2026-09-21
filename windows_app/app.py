"""
Growth OS for Windows - Main Application Orchestrator
Initializes Qt application, top HUD bar, system tray, and background hotkey listener.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from windows_app.hud_bar import HudBar
from windows_app.tray import WindowsSystemTray
from windows_app.hotkey_service import GlobalHotkeyEmitter, WindowsHotkeyService
from windows_app.snipper import trigger_snipper
from windows_app.mistake_dialog import open_mistake_dialog
from windows_app.recall_dialog import open_recall_dialog

def run_app():
    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Growth OS")
    app.setQuitOnLastWindowClosed(False) # Keep running in system tray

    # Initialize Floating Top HUD Bar
    hud_bar = HudBar()
    hud_bar.show()

    # Initialize System Tray
    tray = WindowsSystemTray(hud_bar)
    tray.show()

    # Initialize Global Hotkeys
    emitter = GlobalHotkeyEmitter()
    emitter.snip_signal.connect(trigger_snipper)
    emitter.mistake_signal.connect(open_mistake_dialog)
    emitter.recall_signal.connect(open_recall_dialog)
    emitter.increment_signal.connect(hud_bar.quick_increment_solved)
    emitter.monk_signal.connect(hud_bar.toggle_monk_mode)

    hotkey_service = WindowsHotkeyService(emitter)
    hotkey_service.start()

    print("=====================================================")
    print(" [OK] Growth OS for Windows is RUNNING!")
    print(" Floating HUD bar docked at top of your screen.")
    print(" System tray icon active in notification area.")
    print("")
    print(" Global Hotkeys:")
    print("   Alt + Shift + S     -> Snip to Spaced Recall")
    print("   Alt + Shift + M     -> Mistake Ledger")
    print("   Alt + Shift + R     -> Timed Active Recall Drill")
    print("   Alt + Shift + Right -> +1 Solved Question")
    print("   Alt + Shift + W     -> Toggle Monk Mode Firewall")
    print("=====================================================")

    try:
        sys.exit(app.exec())
    finally:
        hotkey_service.stop()

if __name__ == "__main__":
    run_app()

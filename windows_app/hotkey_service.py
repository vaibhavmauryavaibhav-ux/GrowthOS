"""
Growth OS for Windows - OS-Level Global Hotkey Service
Listens for system-wide shortcuts even when the application is minimized or unfocused.
"""

import sys
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

class GlobalHotkeyEmitter(QObject):
    snip_signal = pyqtSignal()
    mistake_signal = pyqtSignal()
    recall_signal = pyqtSignal()
    increment_signal = pyqtSignal()
    monk_signal = pyqtSignal()
    spotlight_signal = pyqtSignal()
    coach_signal = pyqtSignal()
    audio_signal = pyqtSignal()

class WindowsHotkeyService:
    def __init__(self, emitter: GlobalHotkeyEmitter):
        self.emitter = emitter
        self.listener = None

    def start(self):
        try:
            from pynput import keyboard

            hotkey_map = {
                '<alt>+<shift>+s': self.emitter.snip_signal.emit,
                '<alt>+<shift>+m': self.emitter.mistake_signal.emit,
                '<alt>+<shift>+r': self.emitter.recall_signal.emit,
                '<alt>+<shift>+<right>': self.emitter.increment_signal.emit,
                '<alt>+<shift>+w': self.emitter.monk_signal.emit,
                '<alt>+<space>': self.emitter.spotlight_signal.emit,
                '<alt>+<shift>+d': self.emitter.coach_signal.emit,
                '<alt>+<shift>+a': self.emitter.audio_signal.emit,
            }

            self.listener = keyboard.GlobalHotKeys(hotkey_map)
            self.listener.daemon = True
            self.listener.start()
            print("[HotkeyService] Global hotkeys registered: Alt+Shift+{S, M, R, Right, W}")
        except Exception as e:
            print(f"[HotkeyService] Warning: Could not bind global hotkeys: {e}")

    def stop(self):
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass

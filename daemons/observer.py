"""
Observer Daemon for Cognitive Growth OS
Continuously tracks active windows and applications with pattern matching for Auto Mode.
Cross-platform support: Wayland (Hyprland), X11, and Windows testing fallback.
"""

import sys
import time
import fnmatch
from typing import Tuple, List, Optional, Dict, Any
from core.db import start_session, end_session, log_telemetry
from core.plugin_manager import plugin_manager
from core.config_loader import load_settings

class WindowObserver:
    def __init__(self):
        self.settings = load_settings()
        self.patterns = self.settings.get("auto_mode_patterns", ["*pw.live*"])
        self.current_session_id: Optional[int] = None
        self.active_pattern: Optional[str] = None
        self.is_auto_mode = (self.settings.get("focus", {}).get("default_mode") == "auto")
        self.last_input_time = time.time()

    def reload_patterns(self):
        self.settings = load_settings()
        self.patterns = self.settings.get("auto_mode_patterns", ["*pw.live*"])

    def get_active_window_info(self) -> Tuple[str, str]:
        """Returns (window_title, app_name) across Linux Wayland, Linux X11, or Windows."""
        platform = sys.platform

        if platform.startswith("linux"):
            # 1. Try Hyprland Wayland IPC
            try:
                import subprocess
                import json
                out = subprocess.check_output(["hyprctl", "activewindow", "-j"], stderr=subprocess.DEVNULL)
                data = json.loads(out.decode())
                title = data.get("title", "")
                app = data.get("class", "")
                return title, app
            except Exception:
                pass

            # 2. Try X11 xdotool
            try:
                import subprocess
                title = subprocess.check_output(["xdotool", "getactivewindow", "getwindowname"], stderr=subprocess.DEVNULL).decode().strip()
                return title, "X11App"
            except Exception:
                pass

            return "Unknown Linux Window", "linux"

        elif platform == "win32":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                hwnd = user32.GetForegroundWindow()
                length = user32.GetWindowTextLengthW(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value
                return title, "WindowsApp"
            except Exception:
                return "Unknown Windows Window", "win32"

        return "Unknown Window", "unknown"

    def matches_auto_pattern(self, title: str) -> Optional[str]:
        """Checks if title matches any wildcard pattern in the whitelist."""
        title_lower = title.lower()
        for pattern in self.patterns:
            if fnmatch.fnmatch(title_lower, pattern.lower()):
                return pattern
        return None

    def tick(self) -> Dict[str, Any]:
        """Performs one observation cycle. Call every 1-2 seconds."""
        title, app = self.get_active_window_info()
        matched = self.matches_auto_pattern(title)
        is_productive = bool(matched)

        # Telemetry logging
        log_telemetry(title, app, matched or "", is_productive=is_productive)

        # Auto Mode Session Logic
        if self.is_auto_mode:
            if matched:
                if self.current_session_id is None:
                    # Auto-start focus session
                    self.current_session_id = start_session(mode="auto", matched_pattern=matched)
                    self.active_pattern = matched
                    plugin_manager.dispatch("on_session_start", {
                        "session_id": self.current_session_id,
                        "mode": "auto",
                        "matched_pattern": matched
                    })
                plugin_manager.dispatch("on_url_matched", matched, title)
            else:
                # Left the productive window
                if self.current_session_id is not None:
                    end_session(self.current_session_id, duration_seconds=0.0, questions_solved=0)
                    plugin_manager.dispatch("on_session_end", {
                        "session_id": self.current_session_id,
                        "reason": "switched_away"
                    })
                    self.current_session_id = None
                    self.active_pattern = None

        return {
            "window_title": title,
            "app_name": app,
            "matched_pattern": matched,
            "is_auto_active": self.current_session_id is not None
        }

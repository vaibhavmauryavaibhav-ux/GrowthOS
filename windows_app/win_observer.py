"""
Growth OS for Windows - Native Win32 Window & Process Observer
Continuously monitors the active foreground window and process for automatic focus tracking.
"""

import sys
import os
import time
import fnmatch
import ctypes
from ctypes import wintypes, byref, sizeof, create_unicode_buffer
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config_loader import load_settings
from core.db import log_telemetry

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

class WindowsObserver:
    def __init__(self):
        self.settings = load_settings()
        self.whitelist = self.settings.get("auto_mode_patterns", [
            "*pw.live*", "*physicswallah*", "*unacademy*", "*allen.in*",
            "*.pdf*", "*sumatra*", "*acrobat*", "*onenote*", "*obsidian*"
        ])
        self.blacklist = self.settings.get("monk_mode_blacklist", [
            "*youtube.com/shorts*", "*instagram*", "*reddit*", "*twitter*",
            "*x.com*", "*discord*", "*twitch*", "*netflix*", "*steam*"
        ])
        
        self.focus_score = 100
        self.last_off_task_time = 0
        self.current_app = ""
        self.current_title = ""

    def get_foreground_info(self) -> Tuple[str, str]:
        """Returns (window_title, process_name) of the currently focused window."""
        if sys.platform != "win32":
            return ("Test Window", "test.exe")

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ("", "")

        # Get window title
        buf_len = user32.GetWindowTextLengthW(hwnd) + 1
        title_buf = create_unicode_buffer(buf_len)
        user32.GetWindowTextW(hwnd, title_buf, buf_len)
        title = title_buf.value

        # Get process executable name
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, byref(pid))
        
        proc_name = ""
        h_process = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
        if h_process:
            try:
                proc_buf = create_unicode_buffer(1024)
                size = wintypes.DWORD(1024)
                if kernel32.QueryFullProcessImageNameW(h_process, 0, proc_buf, byref(size)):
                    proc_name = Path(proc_buf.value).name
            finally:
                kernel32.CloseHandle(h_process)

        self.current_title = title
        self.current_app = proc_name
        return (title, proc_name)

    def evaluate_focus(self) -> int:
        """Evaluates whether current foreground app is on-task or distracting."""
        title, app = self.get_foreground_info()
        haystack = f"{title.lower()} {app.lower()}"

        is_blacklisted = any(fnmatch.fnmatch(haystack, pat.lower()) for pat in self.blacklist)
        is_whitelisted = any(fnmatch.fnmatch(haystack, pat.lower()) for pat in self.whitelist)

        now = time.time()
        if is_blacklisted:
            # Drain focus score
            self.focus_score = max(10, self.focus_score - 4)
            self.last_off_task_time = now
        elif is_whitelisted:
            # Recover focus score smoothly
            self.focus_score = min(100, self.focus_score + 2)
        else:
            # Neutral desktop/system activity
            if now - self.last_off_task_time > 60:
                self.focus_score = min(100, self.focus_score + 1)

        return self.focus_score

windows_observer = WindowsObserver()

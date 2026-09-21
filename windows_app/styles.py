"""
Growth OS for Windows - Styles & Theme Engine
Catppuccin Mocha + Windows 11 Fluent Dark Aesthetics.
"""

import sys
import ctypes
from ctypes import c_int, byref, sizeof

# Catppuccin Mocha Palette
COLOR_CRUST    = "#11111b"
COLOR_MANTLE   = "#181825"
COLOR_BASE     = "#1e1e2e"
COLOR_SURFACE0 = "#313244"
COLOR_SURFACE1 = "#45475a"
COLOR_SURFACE2 = "#585b70"
COLOR_TEXT     = "#cdd6f4"
COLOR_SUBTEXT  = "#a6adc8"
COLOR_CYAN     = "#89dceb"
COLOR_BLUE     = "#89b4fa"
COLOR_LAVENDER = "#b4befe"
COLOR_GREEN    = "#a6e3a1"
COLOR_YELLOW   = "#f9e2af"
COLOR_PEACH    = "#fab387"
COLOR_RED      = "#f38ba8"
COLOR_MAUVE    = "#cba6f7"

def apply_windows_acrylic(hwnd: int):
    """Applies Windows 11 Acrylic/Mica backdrop to a Win32 HWND if supported."""
    if sys.platform != "win32":
        return
    try:
        dwmapi = ctypes.windll.dwmapi
        # DWMWA_SYSTEMBACKDROP_TYPE = 38 (3 = Acrylic, 2 = Mica, 4 = Mica Alt)
        # DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        dark_mode = c_int(1)
        dwmapi.DwmSetWindowAttribute(hwnd, 20, byref(dark_mode), sizeof(dark_mode))

        backdrop_type = c_int(3) # Acrylic
        dwmapi.DwmSetWindowAttribute(hwnd, 38, byref(backdrop_type), sizeof(backdrop_type))
    except Exception:
        pass

import html
import re

def render_markdown_to_html(text: str) -> str:
    """Converts markdown bold, code, math, and lists to clean styled HTML for Qt labels."""
    if not text:
        return ""
    escaped = html.escape(text)
    # Bold **text** -> cyan bold
    escaped = re.sub(r'\*\*(.*?)\*\*', r'<b style="color:#89dceb;">\1</b>', escaped)
    # Inline code `code` -> green pill
    escaped = re.sub(r'`(.*?)`', r'<code style="background-color:#181825; color:#a6e3a1; padding:2px 5px; border-radius:4px; font-family:Consolas;">\1</code>', escaped)
    # Math $...$ -> yellow math font
    escaped = re.sub(r'\$(.*?)\$', r'<span style="color:#f9e2af; font-family:Consolas, monospace; font-style:italic;">\1</span>', escaped)
    # Bullet points
    escaped = re.sub(r'^\s*[-*]\s+(.*)$', r'&bull; \1', escaped, flags=re.MULTILINE)
    # Line breaks
    escaped = escaped.replace("\n", "<br>")
    return f"<div style='line-height: 140%;'>{escaped}</div>"

# Stylesheet for Top Floating HUD Bar
HUD_BAR_STYLE = f"""
QWidget#HudBar {{
    background-color: rgba(24, 24, 37, 215);
    border: 1px solid rgba(137, 220, 235, 70);
    border-radius: 18px;
}}

QLabel {{
    color: {COLOR_TEXT};
    font-family: 'Segoe UI', 'JetBrains Mono', 'Consolas', sans-serif;
    font-size: 12px;
    font-weight: 600;
}}

/* Pill Widgets */
QFrame.pill {{
    background-color: rgba(49, 50, 68, 180);
    border: 1px solid rgba(69, 71, 90, 160);
    border-radius: 12px;
    padding: 3px 10px;
}}
QFrame.pill:hover {{
    background-color: rgba(69, 71, 90, 220);
    border: 1px solid rgba(137, 220, 235, 120);
}}

/* Pill Buttons */
QPushButton.pill-btn {{
    background-color: rgba(49, 50, 68, 180);
    border: 1px solid rgba(69, 71, 90, 160);
    border-radius: 12px;
    color: {COLOR_TEXT};
    font-family: 'Segoe UI', 'Consolas', sans-serif;
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
}}
QPushButton.pill-btn:hover {{
    background-color: rgba(88, 91, 112, 220);
    border: 1px solid rgba(180, 190, 254, 180);
    color: #ffffff;
}}
QPushButton.pill-btn:pressed {{
    background-color: rgba(137, 220, 235, 100);
}}

/* Monk Pill Button Active */
QPushButton.monk-active {{
    background-color: rgba(243, 139, 168, 200);
    border: 1px solid {COLOR_RED};
    color: #ffffff;
}}
"""

# Stylesheet for Modals and Dialogs (Mistake Ledger, Recall Drill, Settings)
DIALOG_STYLE = f"""
QDialog, QWidget#DialogRoot {{
    background-color: {COLOR_BASE};
    border: 1px solid {COLOR_SURFACE1};
    border-radius: 14px;
}}

QLabel {{
    color: {COLOR_TEXT};
    font-family: 'Segoe UI', 'Consolas', sans-serif;
    font-size: 13px;
}}

QLabel#HeaderTitle {{
    font-size: 18px;
    font-weight: bold;
    color: {COLOR_CYAN};
}}

QLineEdit, QTextEdit, QComboBox {{
    background-color: {COLOR_MANTLE};
    border: 1px solid {COLOR_SURFACE1};
    border-radius: 8px;
    color: {COLOR_TEXT};
    padding: 8px 12px;
    font-family: 'Segoe UI', 'Consolas', sans-serif;
    font-size: 13px;
}}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border: 1.5px solid {COLOR_CYAN};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QPushButton.primary-btn {{
    background-color: {COLOR_CYAN};
    color: {COLOR_CRUST};
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: bold;
    font-size: 13px;
}}
QPushButton.primary-btn:hover {{
    background-color: #a6e3a1;
}}
QPushButton.primary-btn:pressed {{
    background-color: #94e2d5;
}}

QPushButton.secondary-btn {{
    background-color: {COLOR_SURFACE0};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_SURFACE1};
    border-radius: 8px;
    padding: 9px 18px;
    font-size: 13px;
}}
QPushButton.secondary-btn:hover {{
    background-color: {COLOR_SURFACE1};
}}

/* Rating Buttons for Spaced Recall */
QPushButton.rating-again {{
    background-color: rgba(243, 139, 168, 40);
    border: 1px solid {COLOR_RED};
    color: {COLOR_RED};
    border-radius: 8px;
    padding: 8px;
    font-weight: bold;
}}
QPushButton.rating-again:hover {{
    background-color: {COLOR_RED};
    color: {COLOR_CRUST};
}}

QPushButton.rating-hard {{
    background-color: rgba(250, 179, 135, 40);
    border: 1px solid {COLOR_PEACH};
    color: {COLOR_PEACH};
    border-radius: 8px;
    padding: 8px;
    font-weight: bold;
}}
QPushButton.rating-hard:hover {{
    background-color: {COLOR_PEACH};
    color: {COLOR_CRUST};
}}

QPushButton.rating-good {{
    background-color: rgba(137, 220, 235, 40);
    border: 1px solid {COLOR_CYAN};
    color: {COLOR_CYAN};
    border-radius: 8px;
    padding: 8px;
    font-weight: bold;
}}
QPushButton.rating-good:hover {{
    background-color: {COLOR_CYAN};
    color: {COLOR_CRUST};
}}

QPushButton.rating-easy {{
    background-color: rgba(166, 227, 161, 40);
    border: 1px solid {COLOR_GREEN};
    color: {COLOR_GREEN};
    border-radius: 8px;
    padding: 8px;
    font-weight: bold;
}}
QPushButton.rating-easy:hover {{
    background-color: {COLOR_GREEN};
    color: {COLOR_CRUST};
}}

QProgressBar {{
    background-color: {COLOR_MANTLE};
    border: 1px solid {COLOR_SURFACE0};
    border-radius: 6px;
    text-align: center;
    color: {COLOR_TEXT};
    font-weight: bold;
    height: 14px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLOR_CYAN}, stop:1 {COLOR_MAUVE});
    border-radius: 5px;
}}
"""

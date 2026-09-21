#!/usr/bin/env python3
"""
Growth OS for Windows - Quick Launcher
Run this script to start the native Windows Growth OS cockpit.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from windows_app.app import run_app

if __name__ == "__main__":
    run_app()

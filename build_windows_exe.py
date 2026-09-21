"""
Build Script for Standalone Growth OS Windows Executable (GrowthOS.exe)
Compiles everything into a single-folder / single-exe package with 0 dependencies.
"""

import subprocess
import sys
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

def build():
    print("=====================================================")
    print("      BUILDING GROWTH OS STANDALONE WINDOWS APP")
    print("=====================================================")

    dist_dir = ROOT_DIR / "dist"
    build_dir = ROOT_DIR / "build"
    spec_file = ROOT_DIR / "GrowthOS.spec"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--name", "GrowthOS",
        "--onedir",
        "--add-data", f"config{';' if sys.platform == 'win32' else ':'}config",
        "--add-data", f"plugins{';' if sys.platform == 'win32' else ':'}plugins",
        "--hidden-import", "PyQt6",
        "--hidden-import", "pynput.keyboard._win32",
        "--hidden-import", "pynput.mouse._win32",
        "--hidden-import", "win32gui",
        "--hidden-import", "win32process",
        "--hidden-import", "yaml",
        "--clean",
        "--y",
        str(ROOT_DIR / "run_windows.py")
    ]

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(ROOT_DIR))
    if result.returncode == 0:
        exe_path = dist_dir / "GrowthOS" / "GrowthOS.exe"
        print("")
        print("=====================================================")
        print(" [OK] BUILD SUCCESSFUL!")
        print(f" Standalone Executable created at:")
        print(f"   {exe_path}")
        print("=====================================================")
    else:
        print(f"[!] Build failed with exit code: {result.returncode}")

if __name__ == "__main__":
    build()

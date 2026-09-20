#!/usr/bin/env bash
# Growth OS ISO Compilation Script
# Requirements: archiso package installed on Arch Linux

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="/tmp/archiso-growth-os"
OUT_DIR="$SCRIPT_DIR/out"

echo "==============================================="
echo "       GROWTH OS : ISO BUILD PIPELINE"
echo "==============================================="

if [ "$EUID" -ne 0 ]; then
  echo "[-] Please run as root (e.g., sudo ./build_iso.sh)"
  exit 1
fi

if ! command -v mkarchiso &> /dev/null; then
    echo "[-] mkarchiso not found. Please install: sudo pacman -S archiso"
    exit 1
fi

mkdir -p "$OUT_DIR"
mkdir -p "$WORK_DIR"

# Copy core growth-os code into airootfs
mkdir -p "$SCRIPT_DIR/airootfs/usr/local/share/growth-os"
cp -r "$SCRIPT_DIR/../core" "$SCRIPT_DIR/airootfs/usr/local/share/growth-os/"
cp -r "$SCRIPT_DIR/../daemons" "$SCRIPT_DIR/airootfs/usr/local/share/growth-os/"
cp -r "$SCRIPT_DIR/../tools" "$SCRIPT_DIR/airootfs/usr/local/share/growth-os/"
cp -r "$SCRIPT_DIR/../hud" "$SCRIPT_DIR/airootfs/usr/local/share/growth-os/"
cp -r "$SCRIPT_DIR/../plugins" "$SCRIPT_DIR/airootfs/usr/local/share/growth-os/"
cp -r "$SCRIPT_DIR/../config" "$SCRIPT_DIR/airootfs/usr/local/share/growth-os/"

echo "[+] Building bootable ISO..."
mkarchiso -v -w "$WORK_DIR" -o "$OUT_DIR" "$SCRIPT_DIR"

echo "[✓] Build complete! Bootable ISO is available in: $OUT_DIR"

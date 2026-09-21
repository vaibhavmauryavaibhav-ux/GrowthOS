#!/usr/bin/env bash
# =============================================================================
# Growth OS : 1-Click Cockpit Installer
# Transforms a fresh Arch Linux / default Hyprland install into Growth OS.
# =============================================================================

set -e

echo "====================================================="
echo "       GROWTH OS : COCKPIT INSTALLER FOR ARCH"
echo "====================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[+] Step 1: Installing essential desktop packages & JetBrains Mono font..."
sudo pacman -S --needed --noconfirm \
    hyprland waybar wofi kitty zathura zathura-pdf-mupdf xournalpp \
    grim slurp wl-clipboard mako pipewire pipewire-pulse wireplumber \
    ttf-jetbrains-mono-nerd noto-fonts noto-fonts-emoji \
    python python-pip python-yaml python-pillow python-requests sqlite

echo "[+] Step 2: Deploying Growth OS core codebase to /usr/local/share/growth-os..."
sudo mkdir -p /usr/local/share/growth-os
sudo cp -r "$SCRIPT_DIR/core" /usr/local/share/growth-os/
sudo cp -r "$SCRIPT_DIR/daemons" /usr/local/share/growth-os/
sudo cp -r "$SCRIPT_DIR/tools" /usr/local/share/growth-os/
sudo cp -r "$SCRIPT_DIR/hud" /usr/local/share/growth-os/
sudo cp -r "$SCRIPT_DIR/plugins" /usr/local/share/growth-os/
sudo cp -r "$SCRIPT_DIR/config" /usr/local/share/growth-os/
sudo chmod -R 755 /usr/local/share/growth-os

echo "[+] Step 3: Registering Python environment & system CLI shortcuts..."
PYTHON_SITE=$(python3 -c "import site; print(site.getsitepackages()[0])" 2>/dev/null || echo "/usr/lib/python3.12/site-packages")
echo "/usr/local/share/growth-os" | sudo tee "$PYTHON_SITE/growth_os.pth" >/dev/null || true
echo 'export PYTHONPATH="/usr/local/share/growth-os:$PYTHONPATH"' | sudo tee /etc/profile.d/growth_os.sh >/dev/null

sudo tee /usr/local/bin/growth-capture >/dev/null << 'EOF'
#!/usr/bin/env bash
exec python /usr/local/share/growth-os/tools/quick_capture.py "$@"
EOF

sudo tee /usr/local/bin/growth-mistake >/dev/null << 'EOF'
#!/usr/bin/env bash
exec python /usr/local/share/growth-os/tools/mistake_logger.py "$@"
EOF

sudo tee /usr/local/bin/growth-recall >/dev/null << 'EOF'
#!/usr/bin/env bash
exec python /usr/local/share/growth-os/tools/recall_runner.py "$@"
EOF

sudo chmod +x /usr/local/bin/growth-*

echo "[+] Step 4: Deploying Hyprland, Waybar, Kitty, and Wofi configs to ~/.config..."
mkdir -p "$HOME/.config"
mkdir -p "$HOME/.growth_os/captures"

# Backup existing configs if present
[ -d "$HOME/.config/hypr" ] && cp -r "$HOME/.config/hypr" "$HOME/.config/hypr.backup_$(date +%s)"
[ -d "$HOME/.config/waybar" ] && cp -r "$HOME/.config/waybar" "$HOME/.config/waybar.backup_$(date +%s)"
[ -d "$HOME/.config/kitty" ] && cp -r "$HOME/.config/kitty" "$HOME/.config/kitty.backup_$(date +%s)"
[ -d "$HOME/.config/wofi" ] && cp -r "$HOME/.config/wofi" "$HOME/.config/wofi.backup_$(date +%s)"

cp -r "$SCRIPT_DIR/iso/airootfs/etc/skel/.config/"* "$HOME/.config/"

# Update /etc/skel so any future user accounts also inherit Growth OS
sudo mkdir -p /etc/skel/.config
sudo cp -r "$SCRIPT_DIR/iso/airootfs/etc/skel/.config/"* /etc/skel/.config/ 2>/dev/null || true

echo "[+] Step 5: Reloading desktop & starting Growth OS HUD..."
if command -v hyprctl &> /dev/null; then
    hyprctl reload || true
fi

# Restart bar and daemons with new configs
killall waybar 2>/dev/null || true
killall mako 2>/dev/null || true
nohup waybar >/dev/null 2>&1 &
nohup mako >/dev/null 2>&1 &
nohup python /usr/local/share/growth-os/daemons/observer.py >/dev/null 2>&1 &

echo ""
echo "====================================================="
echo " [OK] SUCCESS! Growth OS Cockpit is now LIVE!"
echo " Look at your top bar: Waybar HUD is running."
echo ""
echo " Try your cognitive shortcuts:"
echo "   Super + Space      -> Wofi Spotlight Launcher"
echo "   Super + Return     -> Kitty GPU Terminal"
echo "   Super + Shift + S  -> Snip directly to Spaced Recall"
echo "   Super + M          -> Mistake Ledger"
echo "   Super + R          -> Timed Active Recall Drill"
echo "   Super + Right      -> +1 Solved Question"
echo "   Super + W          -> Monk Mode Distraction Lock"
echo "====================================================="

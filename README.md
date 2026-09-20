# Growth OS : High-Cognition Academic Operating System

A specialized, distraction-free Linux operating system engineered for intense competitive exam prep (JEE Advanced), cognitive expansion, automated focus tracking, and active retrieval mastery.

Built on **Arch Linux**, **Hyprland (Wayland)**, and **FSRS (Free Spaced Repetition Scheduler)**.

---

## 🚀 Cloud ISO Build (Automated GitHub Actions)

This repository includes a fully automated GitHub Actions workflow (`.github/workflows/build_iso.yml`).

### How to get your bootable ISO:
1. Create a new repository on your GitHub account.
2. Push this folder to your GitHub repo:
   ```bash
   git init
   git add .
   git commit -m "Initial Growth OS release"
   git branch -M main
   git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
   git push -u origin main
   ```
3. Go to the **Actions** tab on your GitHub repository.
4. The **Build Growth OS Bootable ISO** workflow will automatically spin up an Arch Linux builder, compile the full ISO with all packages, Hyprland, themes, and daemons, and output **`GrowthOS-x86_64.iso`** under Releases/Artifacts!
5. Download the `.iso` and flash it to a USB drive using **Rufus** or copy directly to a **Ventoy** drive.

---

## ⚡ Key Features & Cockpit Architecture

* **Hardware-Accelerated Wayland Desktop (Hyprland):**
  * Smooth animations, frosted glass (blur), and rounded corners.
  * Catppuccin Mocha aesthetic with gradient active borders.
* **Non-Removable Focus HUD (Waybar):**
  * `[⚡ FOCUS: 100%]` Live focus score & attention continuity.
  * `[⏳ JEE ADV: 242d]` Automatic exam countdown ticker.
  * `[🎯 TARGET: 14/20]` Real-time progress on daily non-negotiable wins.
  * `[🧠 DUE: 8]` Spaced Repetition card counter with one-click drill launch.
* **Auto Mode Telemetry:**
  * Configurable whitelist (`settings.yaml`): automatically tracks when you are on `pw.live/*`, coaching modules, and local study PDFs (`*.pdf*`).
* **Instant Screenshot-to-Recall (`Super + Shift + S`):**
  * One hotkey snips any equation, mechanism, or diagram directly into the Spaced Recall database.
* **Mistake Ledger (`Super + M`):**
  * Log mistakes by root cause (*Concept Blindspot*, *Pattern Recognition Failure*, *Execution Slip*, *Panic*).
  * Auto-syncs into the recall queue so you are tested before you forget.
* **Timed Question Trainer (`Super + Right`):**
  * Trains sub-conscious speed with per-question pacing or open stopwatch with `+1` increment hotkey.
* **Monk Mode (`Super + W`):**
  * Kernel-level distraction firewall (`nftables` / hosts redirection).

---

## ⌨️ Cognitive Keybindings

| Keybinding | Action |
| :--- | :--- |
| `Super + Shift + S` | **Snip to Recall** (Capture equation/diagram directly to FSRS Spaced Repetition) |
| `Super + M` | **Log Mistake** (Open error ledger & auto-schedule re-test) |
| `Super + R` | **Active Recall Drill** (Start timed retrieval testing on due cards) |
| `Super + Right` | **Question +1** (Mark question solved & reset per-question timer) |
| `Super + W` | **War Mode** (Engage Monk Mode distraction lock) |
| `Super + Space` | **Wofi Spotlight Launcher** (Fuzzy search apps & tools) |
| `Super + Return` | **Kitty Terminal** (GPU-accelerated transparent terminal) |
| `Super + Q` | Close active window |
| `Super + [1-6]` | Switch workspaces |

---

## 🧩 Extensible Plugins

Drop custom Python extensions into `plugins/` to hook into system events:
* `on_session_start`
* `on_question_solved`
* `on_url_matched`
* `on_mistake_logged`
* `on_recall_completed`

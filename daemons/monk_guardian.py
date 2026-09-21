"""
Monk Mode & Distraction Guardian Daemon
Enforces kernel/network level distraction lockouts during War Mode or deep focus blocks.
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import List

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config_loader import load_settings

class MonkGuardian:
    def __init__(self):
        self.is_locked = False
        self.settings = load_settings()
        self.blacklist = self.settings.get("monk_mode_blacklist", [])

    def enable_lockdown(self):
        """Activates distraction lockout."""
        if self.is_locked:
            return
        self.is_locked = True
        print("[MonkGuardian] 🔒 Monk Mode Lockdown ENGAGED.")

        if sys.platform.startswith("linux"):
            # Linux nftables / iptables rule
            try:
                # Add firewall drop rules for blacklisted domains or update /etc/hosts
                self._apply_linux_hosts_block(enable=True)
            except Exception as e:
                print(f"[MonkGuardian] Linux firewall hook error: {e}")
        elif sys.platform == "win32":
            try:
                self._apply_windows_hosts_block(enable=True)
            except Exception as e:
                print(f"[MonkGuardian] Windows hosts block notice: {e}")

    def disable_lockdown(self):
        """Restores full network access."""
        if not self.is_locked:
            return
        self.is_locked = False
        print("[MonkGuardian] 🔓 Monk Mode Lockdown DISENGAGED.")

        if sys.platform.startswith("linux"):
            self._apply_linux_hosts_block(enable=False)
        elif sys.platform == "win32":
            self._apply_windows_hosts_block(enable=False)

    def _apply_linux_hosts_block(self, enable: bool):
        hosts_file = Path("/etc/hosts")
        if not hosts_file.exists():
            return
        # Appends or removes 127.0.0.1 redirect
        tag = "# GROWTH_OS_MONK_BLOCK"
        lines = hosts_file.read_text().splitlines()
        if enable:
            new_lines = [l for l in lines if tag not in l]
            for domain in self.blacklist:
                base_domain = domain.split("/")[0]
                new_lines.append(f"127.0.0.1 {base_domain} {tag}")
                new_lines.append(f"127.0.0.1 www.{base_domain} {tag}")
            hosts_file.write_text("\n".join(new_lines) + "\n")
        else:
            new_lines = [l for l in lines if tag not in l]
            hosts_file.write_text("\n".join(new_lines) + "\n")

    def _apply_windows_hosts_block(self, enable: bool):
        hosts_file = Path(r"C:\Windows\System32\drivers\etc\hosts")
        if not hosts_file.exists():
            return
        tag = "# GROWTH_OS_MONK_BLOCK"
        try:
            lines = hosts_file.read_text().splitlines()
            if enable:
                new_lines = [l for l in lines if tag not in l]
                for domain in self.blacklist:
                    base_domain = domain.split("/")[0]
                    new_lines.append(f"127.0.0.1 {base_domain} {tag}")
                    new_lines.append(f"127.0.0.1 www.{base_domain} {tag}")
                hosts_file.write_text("\n".join(new_lines) + "\n")
            else:
                new_lines = [l for l in lines if tag not in l]
                hosts_file.write_text("\n".join(new_lines) + "\n")
        except PermissionError:
            # Requires admin privileges on Windows; graceful warning
            print("[MonkGuardian] Notice: Run with administrator privileges to modify system hosts on Windows.")

monk_guardian = MonkGuardian()

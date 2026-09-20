#!/usr/bin/env bash
# profiledef.sh for Arch Linux Growth OS

iso_name="GrowthOS"
iso_label="GROWTH_OS_$(date +%Y%m)"
iso_publisher="Growth OS Cognitive Engineering"
iso_application="Growth OS - High Cognition & Academic Acceleration Operating System"
iso_version="$(date +%Y.%m.%d)"
install_dir="arch"
buildmodes=('iso')
bootmodes=('bios.syslinux.mbr' 'bios.syslinux.eltorito' 'uefi-ia32.grub.esp' 'uefi-x64.grub.esp')
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/usr/local/bin/growth-os"]="0:0:755"
)

#!/bin/bash
# Run as root on a disposable Debian trixie amd64 build host/container.
set -euo pipefail
source_dir=$(cd -- "$(dirname -- "$0")/.." && pwd)
if [[ $(id -u) != 0 || $(dpkg --print-architecture) != amd64 ]]; then
    echo 'Build requires root on Debian amd64.' >&2
    exit 1
fi
build_dir=$(mktemp -d /var/tmp/ty-recovery-build.XXXXXX)
cd "$build_dir"
lb config --mode debian --distribution trixie --architectures amd64 \
    --binary-image iso-hybrid --bootloaders 'syslinux grub-efi' \
    --archive-areas 'main contrib non-free-firmware' --debian-installer none \
    --apt-recommends false --iso-volume TY_RECOVERY \
    --bootappend-live 'boot=live components username=ty hostname=ty-recovery locales=en_US.UTF-8 keyboard-layouts=us console=ttyS0,115200 console=tty0'
mkdir -p config/package-lists config/includes.chroot/opt/ty-recovery \
    config/includes.chroot/etc/skel config/includes.chroot/etc/systemd/system/multi-user.target.wants
cat > config/package-lists/recovery.list.chroot <<'PACKAGES'
live-boot
live-config
live-config-systemd
systemd-sysv
python3
network-manager
wpasupplicant
ca-certificates
curl
less
pciutils
usbutils
dmidecode
util-linux
iproute2
sudo
firmware-linux-free
firmware-iwlwifi
firmware-realtek
PACKAGES
for asset in recovery.py catalog.json Recovery-Guide.html Recovery.ps1 Start-Recovery.cmd Start-Recovery.sh Start-Recovery.command README.md; do
    install -m 0644 "$source_dir/$asset" "config/includes.chroot/opt/ty-recovery/$asset"
done
install -m 0644 "$source_dir/boot/console.py" config/includes.chroot/opt/ty-recovery/console.py
cat > config/includes.chroot/etc/skel/.bash_profile <<'PROFILE'
if [ "$(tty)" = /dev/tty1 ]; then
    python3 /opt/ty-recovery/console.py
fi
PROFILE
cat > config/includes.chroot/etc/systemd/system/ty-recovery-check.service <<'SERVICE'
[Unit]
Description=Validate Ty Recovery live environment
After=multi-user.target
[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /opt/ty-recovery/console.py --self-test
StandardOutput=journal+console
[Install]
WantedBy=multi-user.target
SERVICE
# No After=multi-user.target ordering cycle: enabled units precede that target.
sed -i '/After=multi-user.target/d' config/includes.chroot/etc/systemd/system/ty-recovery-check.service
ln -s ../ty-recovery-check.service config/includes.chroot/etc/systemd/system/multi-user.target.wants/ty-recovery-check.service
lb build
mkdir -p "$source_dir/dist"
install -m 0644 live-image-amd64.hybrid.iso "$source_dir/dist/Ty-Recovery-USB-amd64.iso"
cp live-image-amd64.packages "$source_dir/dist/packages.txt"
cd "$source_dir/dist"
sha256sum Ty-Recovery-USB-amd64.iso > SHA256SUMS
echo "ISO created in $source_dir/dist; keep build directory $build_dir for diagnostics."

#!/usr/bin/env bash
# Рассвет / Rassvet: build the installer ISO from CRUX 3.8's, on any x86_64 Linux with sudo
# (Arch on WSL2 is fine).
#
#   bash build/build-iso.sh        -> out/rassvet-x86_64.iso and its .sha256
#
# The ISO is CRUX's own, with:
#   - the 7.3 kernel (ports/linux) for the installer itself, so the Framework 13 Pro's Wi-Fi,
#     graphics and keyboard work from the first second, and newer Intel firmware;
#   - NetworkManager (nmtui) in the installer, for Wi-Fi;
#   - Rassvet's installer (installer/rassvet-install), which starts on tty1;
#   - those packages ready-built in /rassvet/packages, and this repository in /rassvet/repo.
# Everything else is compiled on the laptop during the install, from the ports.
#
# What it does, in order (each step shows its commands; nothing is hidden):
#   1. xorriso, cpio, rsync, curl, xz on this computer
#   2. CRUX 3.8's ISO, checked against its published SHA-256
#   3. a CRUX build root: CRUX's own live system, with every core package from the ISO
#      installed into it (in ~/.cache/rassvet; made once, reused)
#   4. in the build root: the ports (ports -u), then the kernel and NetworkManager built
#      (prt-get), packages into build/work/packages
#   5. the installer's live system and its initramfs, with those added
#   6. the ISO
set -Eeuo pipefail
project=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
work=$project/build/work
cache=${XDG_CACHE_HOME:-$HOME/.cache}/rassvet
say() { printf '\n==> %s\n' "$*"; }
die() { printf '\nRassvet: %s\n' "$*" >&2; exit 2; }
trap 'echo "Rassvet: stopped at line $LINENO (exit $?)" >&2' ERR

CRUX_ISO=crux-3.8.iso
CRUX_ISO_SHA256=8eebf2a58114def46b78fe4fb2afb3175d9becd583699ed2b5e9e2660521e31f
CRUX_MIRRORS="https://ftp.spline.inf.fu-berlin.de/pub/crux/crux-3.8/iso
https://mirrors.dotsrc.org/crux/crux-3.8/iso"
KVER=7.3.1-rassvet
# packages built here for the installer (and installed first on the laptop, so it has its
# network and its kernel before anything else is compiled)
LIVE_PORTS="linux linux-firmware networkmanager"

[[ $(uname -m) == x86_64 ]] || die "an x86_64 builder is needed"
[[ $EUID -ne 0 ]] || die "run as yourself; it asks for sudo when needed"
sudo -v
mkdir -p "$work" "$project/out" "$cache"

# --------------------------------------------------------------------- 1. tools
say "Tools: xorriso, cpio, rsync, curl, xz"
need=()
for t in xorriso cpio rsync curl xz zstd depmod; do command -v $t >/dev/null || need+=("$t"); done
if [[ ${#need[@]} -gt 0 ]]; then
  if command -v pacman >/dev/null; then sudo pacman -S --needed --noconfirm libisoburn cpio rsync curl xz zstd kmod
  elif command -v apt-get >/dev/null; then sudo apt-get install -y xorriso cpio rsync curl xz-utils zstd kmod
  elif command -v dnf >/dev/null; then sudo dnf install -y xorriso cpio rsync curl xz zstd kmod
  else die "install: ${need[*]}"; fi
fi

# --------------------------------------------------------------------- 2. CRUX's ISO
iso_in=$cache/$CRUX_ISO
if ! echo "$CRUX_ISO_SHA256  $iso_in" | sha256sum -c --status 2>/dev/null; then
  say "CRUX 3.8's ISO (1.7 GB, SHA-256 checked)"
  for m in $CRUX_MIRRORS; do
    curl -fL --retry 3 -C - -o "$iso_in" "$m/$CRUX_ISO" && break || true
  done
  echo "$CRUX_ISO_SHA256  $iso_in" | sha256sum -c - ||
    { rm -f "$iso_in"; die "the CRUX ISO failed its checksum (deleted; run again)"; }
fi
media=$cache/media
if [[ ! -f $media/crux-media ]]; then
  say "Unpacking the ISO's files to $media"
  safe_rm "$media"; mkdir -p "$media"
  xorriso -osirrox on -indev "$iso_in" -extract / "$media" 2>&1 | grep -v '^xorriso : UPDATE' || true
  chmod -R u+w "$media"
fi

# --------------------------------------------------------------------- 3. the build root
root=$cache/buildroot
mounts=()
bind() { sudo mkdir -p "$2"; mountpoint -q "$2" || { sudo mount --bind "$1" "$2"; mounts+=("$2"); }; }
cleanup() {
  for ((i=${#mounts[@]}-1; i>=0; i--)); do sudo umount -R "${mounts[i]}" 2>/dev/null || sudo umount -l "${mounts[i]}" 2>/dev/null || true; done
  mounts=()
}
# rm -rf, but only once nothing at all is mounted inside the folder: a chroot's /dev or /sys
# left mounted would otherwise be deleted with it
safe_rm() {
  local d
  for d in "$@"; do
    [[ -e $d ]] || continue
    d=$(realpath "$d")
    if awk -v p="$d/" '{ if (index($2 "/", p) == 1) found = 1 } END { exit !found }' /proc/self/mounts; then
      awk -v p="$d/" 'index($2 "/", p) == 1 { print $2 }' /proc/self/mounts | sort -r |
        while read -r m; do sudo umount -R "$m" 2>/dev/null || sudo umount -l "$m"; done
    fi
    if awk -v p="$d/" '{ if (index($2 "/", p) == 1) found = 1 } END { exit !found }' /proc/self/mounts; then
      die "something is still mounted inside $d; not deleting it (see: findmnt -R $d)"
    fi
    sudo rm -rf --one-file-system "$d"
  done
}
trap cleanup EXIT
chroot_run() {   # chroot_run ROOT COMMAND: with /proc, /sys, /dev and the network inside
  local r=$1; shift
  bind /proc "$r/proc"; bind /sys "$r/sys"; bind /dev "$r/dev"; bind /dev/pts "$r/dev/pts"
  sudo cp -L /etc/resolv.conf "$r/etc/resolv.conf"
  sudo chroot "$r" /usr/bin/env -i HOME=/root TERM="${TERM:-linux}" \
    PATH=/usr/sbin:/usr/bin:/sbin:/bin MAKEFLAGS="-j$(nproc)" /bin/sh -c "$*"
}
if [[ ! -f $root/.rassvet-ready ]]; then
  say "A CRUX build root in $root: the ISO's live system, then every core package"
  safe_rm "$root"; sudo mkdir -p "$root"
  sudo tar -xJf "$media/rootfs.tar.xz" -C "$root"
  bind "$media" "$root/media"
  # the live system is only a tool here: CRUX's core goes into /target inside it
  chroot_run "$root" 'mkdir -p /target/var/lib/pkg && touch /target/var/lib/pkg/db &&
    for p in /media/crux/core/*.pkg.tar.xz; do pkgadd -r /target "$p" || exit 1; done'
  cleanup
  # the build root proper is that /target
  safe_rm "$cache/buildroot.new"
  sudo mv "$root/target" "$cache/buildroot.new"
  safe_rm "$root"; sudo mv "$cache/buildroot.new" "$root"
  sudo touch "$root/.rassvet-ready"
fi

# --------------------------------------------------------------------- 4. packages for the stick
say "Building in the CRUX root: ${LIVE_PORTS} (prt-get; the kernel takes a while)"
mkdir -p "$work/packages" "$cache/distfiles"
bind "$media" "$root/media"
bind "$project" "$root/usr/src/rassvet"
bind "$work/packages" "$root/packages"
bind "$cache/distfiles" "$root/distfiles"
sudo install -m644 "$project/build/crux/pkgmk.conf" "$root/etc/pkgmk.conf"
sudo install -m644 "$project/build/crux/prt-get.conf" "$root/etc/prt-get.conf"
sudo sed -i -e 's|^PKGMK_SOURCE_DIR=.*|PKGMK_SOURCE_DIR="/distfiles"|' \
  -e 's|^PKGMK_PACKAGE_DIR=.*|PKGMK_PACKAGE_DIR="/packages"|' \
  -e 's|^export CFLAGS=.*|export CFLAGS="-O2 -march=x86-64-v3 -pipe"|' "$root/etc/pkgmk.conf"
chroot_run "$root" "
  set -e
  for f in /etc/ports/*.inactive; do [ -e \"\$f\" ] && mv \"\$f\" \"\${f%.inactive}\"; done
  ports -u core opt xorg contrib
  sh /usr/src/rassvet/build/rassvet-ports sync /usr/src/rassvet /usr/ports/rassvet
  sh /usr/src/rassvet/build/rassvet-ports verify /usr/ports/rassvet linux
  sh /usr/src/rassvet/installer/iso-binaries /media/crux \$(prt-get quickdep $LIVE_PORTS)
  prt-get depinst $LIVE_PORTS
  prt-get quickdep $LIVE_PORTS > /packages/LIVE
"
built=$(cat "$work/packages/LIVE")
echo "    $(echo $built | wc -w) packages for the stick"

# --------------------------------------------------------------------- 5. the live system
say "The installer's live system: CRUX's, plus the kernel, NetworkManager and the installer"
live=$cache/live
safe_rm "$live"; sudo mkdir -p "$live"
sudo tar -xJf "$media/rootfs.tar.xz" -C "$live"
bind "$work/packages" "$live/packages"
chroot_run "$live" '
  set -e
  for name in $(cat /packages/LIVE); do
    pkg=$(ls /packages/$name#*.pkg.tar.* 2>/dev/null | head -n 1)
    [ -n "$pkg" ] || continue
    if pkginfo -i | grep -q "^$name "; then pkgadd -u -f "$pkg"; else pkgadd -f "$pkg"; fi
  done
  rm -rf /lib/modules/6.*
  depmod '"$KVER"'
'
cleanup
sudo install -m755 "$project/installer/rassvet-install" "$live/usr/bin/rassvet-install"
sudo install -m755 "$project/installer/iso-binaries" "$live/usr/bin/iso-binaries"
sudo install -m644 "$project/installer/live-bash_profile" "$live/root/.bash_profile"
sudo tar -C "$live" --one-file-system -cf - . | xz -T0 -6 > "$work/rootfs.tar.xz"
safe_rm "$live"

say "The initramfs: CRUX's, with the 7.3 kernel's storage and filesystem modules"
ird=$work/initramfs.d
safe_rm "$ird"; mkdir -p "$ird"
(cd "$ird" && sudo cpio -idm --quiet < "$media/boot/initramfs")
sudo rm -rf "$ird"/lib/modules/*
modsrc=$root/lib/modules/$KVER
for d in kernel/fs kernel/lib kernel/crypto kernel/drivers/usb kernel/drivers/scsi kernel/drivers/ata \
         kernel/drivers/cdrom kernel/drivers/mmc kernel/drivers/block kernel/drivers/nvme \
         kernel/drivers/hid kernel/drivers/input; do
  [[ -d $modsrc/$d ]] && sudo mkdir -p "$ird/lib/modules/$KVER/$d" &&
    sudo cp -a "$modsrc/$d/." "$ird/lib/modules/$KVER/$d/"
done
sudo cp -a "$modsrc"/modules.order "$modsrc"/modules.builtin* "$ird/lib/modules/$KVER/"
# the initramfs's busybox modprobe reads plain modules only
sudo find "$ird/lib/modules" -name '*.ko.zst' -exec zstd -q -d --rm {} \;
sudo depmod -b "$ird" "$KVER"
# the live system is bigger now: give its RAM disk room
sudo sed -i 's/-o size=1650m/-o size=75%/' "$ird/init"
(cd "$ird" && sudo find . | sudo cpio -o -H newc --quiet) > "$work/initramfs"
safe_rm "$ird"

# --------------------------------------------------------------------- 6. the ISO
say "The ISO"
rm -rf "$work/repo"
rsync -a --exclude=/build/work --exclude=/out --exclude=/local --exclude=__pycache__ \
  "$project/" "$work/repo/"
cp "$media/boot/grub/grub.cfg" "$work/grub.cfg"
sed -i -e 's/Install\/Upgrade CRUX 3.8 (UEFI mode)/Рассвет \/ Rassvet installer/' \
  -e 's/set timeout=99/set timeout=5/' "$work/grub.cfg"
iso=$project/out/rassvet-x86_64.iso
rm -f "$iso"
xorriso -indev "$iso_in" -outdev "$iso" -boot_image any replay \
  -map "$root/boot/vmlinuz-$KVER" /boot/vmlinuz \
  -map "$work/initramfs" /boot/initramfs \
  -map "$work/rootfs.tar.xz" /rootfs.tar.xz \
  -map "$work/grub.cfg" /boot/grub/grub.cfg \
  -map "$work/packages" /rassvet/packages \
  -map "$work/repo" /rassvet/repo \
  -commit 2>&1 | grep -v '^xorriso : UPDATE' || true
[[ -s $iso ]] || die "xorriso wrote no ISO"
(cd "$project/out" && sha256sum "$(basename "$iso")" > "$(basename "$iso").sha256")
say "Done: $iso ($(du -h "$iso" | cut -f1))"
echo "    Write it to a USB stick (dd, Ventoy or Rufus), Secure Boot off, boot it in UEFI mode."

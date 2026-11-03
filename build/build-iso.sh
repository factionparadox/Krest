#!/usr/bin/env bash
# Крест / Krest: build the installer ISO from CRUX 3.8's, on any x86_64 Linux with sudo
# (Arch on WSL2 is fine).
#
#   bash build/build-iso.sh        -> out/krest-x86_64.iso and its .sha256
#
# The ISO is CRUX's own, with:
#   - Arch Linux's ready-built kernel and Intel firmware for the installer itself, so the
#     Framework 13 Pro's Wi-Fi, graphics and keyboard work from the first second;
#   - krest-wifi in the installer: a Wi-Fi menu over CRUX's own wpa_supplicant and dhcpcd
#     (NetworkManager and nmtui are compiled on the laptop with the rest);
#   - Krest's installer (installer/krest-install), which starts on tty1;
#   - those packages ready-built in /krest/packages, and this repository in /krest/repo.
# Nothing is compiled on this computer. Everything is compiled on the laptop during the
# install, from the ports.
#
# What it does, in order (each step shows its commands; nothing is hidden):
#   1. xorriso, cpio, rsync, curl, xz on this computer
#   2. CRUX 3.8's ISO, checked against its published SHA-256
#   3. (none: nothing is built here)
#   4. Arch's kernel and firmware (pacman -Sw) made into a CRUX package, linux-arch, in
#      build/work/packages
#   5. the installer's live system and its initramfs, with those added
#   6. the ISO
set -Eeuo pipefail
project=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
work=$project/build/work
cache=${XDG_CACHE_HOME:-$HOME/.cache}/krest
say() { printf '\n==> %s\n' "$*"; }
die() { printf '\nKrest: %s\n' "$*" >&2; exit 2; }
trap 'echo "Krest: stopped at line $LINENO (exit $?)" >&2' ERR

CRUX_ISO=crux-3.8.iso
CRUX_ISO_SHA256=8eebf2a58114def46b78fe4fb2afb3175d9becd583699ed2b5e9e2660521e31f
CRUX_MIRRORS="https://ftp.spline.inf.fu-berlin.de/pub/crux/crux-3.8/iso
https://mirrors.dotsrc.org/crux/crux-3.8/iso"

[[ $(uname -m) == x86_64 ]] || die "an x86_64 builder is needed"
[[ $EUID -ne 0 ]] || die "run as yourself; it asks for sudo when needed"
sudo -v
mkdir -p "$work" "$project/out" "$cache"

# --------------------------------------------------------------------- helpers
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

# depmod for a tree whose modules are in /lib/modules (Arch's own depmod looks in /usr/lib/modules)
depmod_b() {
  local made=
  if [[ ! -e $1/usr/lib/modules ]]; then sudo mkdir -p "$1/usr/lib"; sudo ln -s ../../lib/modules "$1/usr/lib/modules"; made=1; fi
  sudo depmod -b "$1" "$2"
  [[ -z $made ]] || { sudo rm "$1/usr/lib/modules"; sudo rmdir "$1/usr/lib" "$1/usr" 2>/dev/null || true; }
}

# --------------------------------------------------------------------- 4. packages for the stick
# Nothing is compiled on this computer. The stick gets ready-built binaries only:
#   - Arch Linux's kernel and Intel firmware (pacman downloads them and checks Arch's
#     signatures), made into one CRUX package, linux-arch: the kernel, its modules, and its
#     firmware in /lib/firmware/<kernel version>, which only that kernel reads;
# NetworkManager isn't on CRUX's ISO, so the installer gets online with krest-wifi instead.
# The laptop compiles everything else during the install, Krest's own 7.3 kernel included;
# linux-arch stays on as the fallback kernel in the boot menu.
say "Arch's ready-built kernel and Intel firmware (downloaded by pacman; nothing is compiled)"
command -v pacman >/dev/null || die "this step uses pacman: run the build on Arch (WSL is fine)"
arch=$cache/arch
ARCH_PKGS="linux linux-firmware-intel linux-firmware-realtek linux-firmware-other linux-firmware-whence sof-firmware wireless-regdb"
# into pacman's own cache (pacman downloads as its own user, which can't write in your home);
# explicit names, so pacman fetches them even when this computer has them installed
for try in 1 2 3; do
  sudo pacman -Syw --noconfirm $ARCH_PKGS && break
  [[ $try -lt 3 ]] || die "pacman could not download Arch's packages (the network or the mirror; run again)"
  echo "    the download stalled; trying again ($try of 3; what's already downloaded is kept)"; sleep 5
done
safe_rm "$arch/pkgs"; mkdir -p "$arch/pkgs"
pcache=$(pacman-conf CacheDir 2>/dev/null | head -n 1 || true); pcache=${pcache:-/var/cache/pacman/pkg/}
pacman -Sp --print-format '%n %f' $ARCH_PKGS | while read -r n f; do
  case " $ARCH_PKGS " in *" $n "*) cp "${pcache%/}/$f" "$arch/pkgs/" || exit 1 ;; esac
done || die "the packages pacman downloaded are not in ${pcache}"
akpkg=$(ls -t "$arch"/pkgs/linux-[0-9]*.pkg.tar.zst | head -n 1)
[[ -n $akpkg ]] || die "pacman downloaded no kernel package"
st=$work/linux-arch
safe_rm "$st"; sudo mkdir -p "$st/x"
sudo bsdtar -xpf "$akpkg" -C "$st/x" usr/lib/modules
KVER=$(ls "$st/x/usr/lib/modules" | head -n 1)
[[ -f $st/x/usr/lib/modules/$KVER/vmlinuz ]] || die "no vmlinuz in $(basename "$akpkg")"
echo "    kernel $KVER"
sudo mkdir -p "$st/pkg/boot" "$st/pkg/lib/modules" "$st/pkg/lib/firmware/$KVER"
sudo mv "$st/x/usr/lib/modules/$KVER/vmlinuz" "$st/pkg/boot/vmlinuz-$KVER"
sudo rm -f "$st/x/usr/lib/modules/$KVER/pkgbase" "$st/x/usr/lib/modules/$KVER/build"
sudo mv "$st/x/usr/lib/modules/$KVER" "$st/pkg/lib/modules/"
# CRUX's kmod and the initramfs's busybox read plain modules only
sudo find "$st/pkg/lib/modules" -name '*.ko.zst' -exec zstd -q -d --rm {} +
depmod_b "$st/pkg" "$KVER"
[[ -s $st/pkg/lib/modules/$KVER/modules.dep ]] || die "depmod wrote no modules.dep"
for f in "$arch"/pkgs/{linux-firmware-*,sof-firmware,wireless-regdb}-[0-9]*.pkg.tar.zst; do
  [[ -f $f ]] || continue
  sudo rm -rf "$st/x"; sudo mkdir -p "$st/x"
  sudo bsdtar -xpf "$f" -C "$st/x"
  [[ -d $st/x/usr/lib/firmware ]] && sudo cp -a "$st/x/usr/lib/firmware/." "$st/pkg/lib/firmware/$KVER/"
done
sudo rm -rf "$st/x"
ls "$st/pkg/lib/firmware/$KVER"/iwlwifi-* >/dev/null 2>&1 || die "no Intel Wi-Fi firmware in Arch's packages"
safe_rm "$work/packages"; mkdir -p "$work/packages"
pkgv=${KVER//-/_}
sudo bsdtar --uid 0 --gid 0 --zstd -cf "$work/packages/linux-arch#$pkgv-1.pkg.tar.zst" -C "$st/pkg" boot lib
echo "    $(du -h "$work/packages/linux-arch#$pkgv-1.pkg.tar.zst" | cut -f1) linux-arch package"

echo linux-arch > "$work/packages/LIVE"

# --------------------------------------------------------------------- 5. the live system
say "The installer's live system: CRUX's, plus the kernel, its firmware and the installer"
live=$cache/live
safe_rm "$live"; sudo mkdir -p "$live"
sudo tar -xJf "$media/rootfs.tar.xz" -C "$live"
# CRUX's live root keeps no package database: the stick's packages are unpacked into it
for name in $(cat "$work/packages/LIVE"); do
  pkg=$(ls "$work"/packages/"$name"#*.pkg.tar.* 2>/dev/null | head -n 1 || true)
  [[ -n $pkg ]] || die "no package for $name in $work/packages"
  sudo bsdtar -xpf "$pkg" -C "$live"
done
sudo rm -rf "$live"/lib/modules/6.*
# what the installer uses to get online
for t in usr/sbin/wpa_supplicant usr/sbin/wpa_cli sbin/dhcpcd usr/bin/dialog usr/bin/curl; do
  [[ -x $live/$t ]] || die "CRUX's live system has no /$t"
done
cleanup
sudo install -m755 "$project/installer/krest-install" "$live/usr/bin/krest-install"
sudo install -m755 "$project/installer/iso-binaries" "$live/usr/bin/iso-binaries"
sudo install -m755 "$project/installer/krest-wifi" "$live/usr/bin/krest-wifi"
sudo install -m644 "$project/installer/live-bash_profile" "$live/root/.bash_profile"
sudo tar -C "$live" --one-file-system -cf - . | xz -T0 -6 > "$work/rootfs.tar.xz"
safe_rm "$live"

say "The initramfs: CRUX's, with the $KVER kernel's storage and filesystem modules"
ird=$work/initramfs.d
safe_rm "$ird"; mkdir -p "$ird"
(cd "$ird" && sudo cpio -idm --quiet < "$media/boot/initramfs")
sudo rm -rf "$ird"/lib/modules/*
modsrc=$st/pkg/lib/modules/$KVER
for d in kernel/fs kernel/lib kernel/crypto kernel/drivers/usb kernel/drivers/scsi kernel/drivers/ata \
         kernel/drivers/cdrom kernel/drivers/mmc kernel/drivers/block kernel/drivers/nvme \
         kernel/drivers/hid kernel/drivers/input; do
  [[ -d $modsrc/$d ]] && sudo mkdir -p "$ird/lib/modules/$KVER/$d" &&
    sudo cp -a "$modsrc/$d/." "$ird/lib/modules/$KVER/$d/"
done
sudo cp -a "$modsrc"/modules.order "$modsrc"/modules.builtin* "$ird/lib/modules/$KVER/"
# the initramfs's busybox modprobe reads plain modules only
sudo find "$ird/lib/modules" -name '*.ko.zst' -exec zstd -q -d --rm {} \;
depmod_b "$ird" "$KVER"
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
sed -i -e 's/Install\/Upgrade CRUX 3.8 (UEFI mode)/Крест \/ Krest installer/' \
  -e 's/set timeout=99/set timeout=5/' "$work/grub.cfg"
iso=$project/out/krest-x86_64.iso
rm -f "$iso"
xorriso -indev "$iso_in" -outdev "$iso" -boot_image any replay \
  -map "$st/pkg/boot/vmlinuz-$KVER" /boot/vmlinuz \
  -map "$work/initramfs" /boot/initramfs \
  -map "$work/rootfs.tar.xz" /rootfs.tar.xz \
  -map "$work/grub.cfg" /boot/grub/grub.cfg \
  -map "$work/packages" /krest/packages \
  -map "$work/repo" /krest/repo \
  -commit 2>&1 | grep -v '^xorriso : UPDATE' || true
[[ -s $iso ]] || die "xorriso wrote no ISO"
(cd "$project/out" && sha256sum "$(basename "$iso")" > "$(basename "$iso").sha256")
say "Done: $iso ($(du -h "$iso" | cut -f1))"
echo "    Write it to a USB stick (dd, Ventoy or Rufus), Secure Boot off, boot it in UEFI mode."

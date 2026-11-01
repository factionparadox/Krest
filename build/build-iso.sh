#!/usr/bin/env bash
# Pustota: build the installer ISO on Arch Linux (WSL2 is fine), or natively on Void.
#
#   bash build/build-iso.sh            -> out/pustota-x86_64.iso
#
# On Arch it builds inside a verified Void glibc root filesystem (no Docker, nothing changed
# on Arch beyond a few packages): Void's signed February 2025 rootfs, checked with Void's
# minisign release key and a pinned SHA-256, upgraded, then build/make-iso.sh runs inside it.
# This is the route Archon/Cognoscenti proved on the same Arch WSL builder.
set -Eeuo pipefail
project=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
say() { printf '\n==> %s\n' "$*"; }
die() { printf '\nPustota: %s\n' "$*" >&2; exit 2; }
trap 'echo "Pustota: stopped at line $LINENO (exit $?)" >&2' ERR

[[ $(uname -m) == x86_64 ]] || die "an x86_64 builder is needed"
os=$(. /etc/os-release; echo "$ID")
if [[ $os == void ]]; then
  [[ $EUID -eq 0 ]] || exec sudo bash "$0" "$@"
  exec bash "$project/build/make-iso.sh"
fi
[[ $os == arch ]] || die "build on Arch (WSL2 works) or on Void glibc"
[[ $EUID -ne 0 ]] || die "run as yourself; it asks for sudo when needed"
for cmd in sudo pacman mount umount mountpoint chroot flock; do
  command -v "$cmd" >/dev/null || die "missing $cmd"
done
sudo -v
say "Arch packages the build needs"
sudo pacman -S --needed --noconfirm curl minisign xz tar ca-certificates openssl

cache=$HOME/.cache/pustota
[[ ! -L $cache ]] || die "refusing a symlinked $cache"
mkdir -p "$cache"
exec 9>"$cache/.build.lock"
flock -n 9 || die "a Pustota build is already running"
base=$cache/void-glibc-rootfs
file=void-x86_64-ROOTFS-20250202.tar.xz
sum=3f48e6673ac5907a897d913c97eb96edbfb230162731b4016562c51b3b8f1876
pubkey=$project/build/keys/void-release-20250202.pub

if [[ ! -x $base/usr/bin/xbps-install ]]; then
  say "Void glibc root filesystem (verified)"
  mkdir -p "$cache/downloads"
  (
    cd "$cache/downloads"
    for item in "$file" sha256sum.txt sha256sum.sig; do
      [[ -s $item ]] && continue
      # the dated folder first; "current" while the 2025 images are still the current ones
      curl -fL --retry 3 -o "$item.part" "https://repo-default.voidlinux.org/live/20250202/$item" ||
        curl -fL --retry 3 -o "$item.part" "https://repo-default.voidlinux.org/live/current/$item"
      mv "$item.part" "$item"
    done
    minisign -V -p "$pubkey" -x sha256sum.sig -m sha256sum.txt
    printf '%s  %s\n' "$sum" "$file" | sha256sum -c -
  )
  sudo mkdir -p "$base"
  sudo tar -xJpf "$cache/downloads/$file" -C "$base" --numeric-owner
fi
[[ -x $base/usr/bin/xbps-install ]] || die "incomplete Void rootfs in $base"

sudo mkdir -p "$base/work" "$base/dev" "$base/proc" "$base/sys"
sudo cp -L /etc/resolv.conf "$base/etc/resolv.conf"
cleanup() {
  sudo rm -f "$base/root/pustota-repo-key.pem"
  for item in work sys proc dev; do
    if mountpoint -q "$base/$item"; then sudo umount -R "$base/$item" || echo "could not unmount $item" >&2; fi
  done
}
trap cleanup EXIT
for item in dev proc sys; do
  sudo mount --rbind "/$item" "$base/$item"
  sudo mount --make-rslave "$base/$item"
done
sudo mount --bind "$project" "$base/work"
inroot() {
  sudo chroot "$base" /usr/bin/env -i HOME=/root TERM="${TERM:-xterm}" \
    PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin "$@"
}
# This root is disposable: xbps-src may build in it directly ("ethereal" style).
sudo touch "$base/.pustota-build-root"
# The repository signing key lives in your home, never in the project. Made on the first build;
# keep it (installed systems trust it), and back it up.
key=$HOME/.config/pustota/repo-key.pem
if [[ ! -s $key ]]; then
  mkdir -p "$(dirname "$key")"
  (umask 077; openssl genrsa -out "$key" 4096 2>/dev/null)
  say "New repository signing key: $key  (back it up: installed systems trust it)"
fi
sudo install -m600 "$key" "$base/root/pustota-repo-key.pem"
say "Updating the build root (XBPS first, then everything: no partial upgrades)"
inroot /bin/sh -ec 'xbps-install -Suy xbps'
inroot /bin/sh -ec 'xbps-install -Suy'
inroot /bin/sh -ec 'xbps-install -Sy bash make git curl python3 xz zstd openssl'
say "Building inside Void"
inroot /bin/bash /work/build/make-iso.sh
out=$project/out/pustota-x86_64.iso
[[ -s $out ]] || die "no ISO was produced"
sudo chown -R "$(id -u):$(id -g)" "$project/out" "$project/build/work" 2>/dev/null || true
sudo rm -f "$base/root/pustota-repo-key.pem"
say "Done: $out ($(du -h "$out" | cut -f1))"

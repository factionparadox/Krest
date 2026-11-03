#!/usr/bin/env bash
# Pustota's offline ISO: every Void package the installer needs, in a local repository on the
# ISO, so an install needs no network. Called by make-iso.sh inside Void.
#   make-offline-repo.sh PUSTOTA_REPO KEYS_DIR OUT_DIR
# XBPS itself works out the package set: the same transaction the installer runs (base-system and
# Pustota's three packages into an empty root, with the kernel settings the installer writes),
# downloaded only (-D). Downloads are kept in build/work/void-cache, so the next build fetches
# only what changed. Each package's signature is checked by XBPS as it downloads (Void's repositories
# are signed); the local copy on the ISO is indexed for XBPS but needs no signature of its own.
set -Eeuo pipefail
repo=$1 keys=$2 out=$3
work=$(cd "$(dirname "$out")" && pwd)
cache=$work/void-cache
mirror=${VOID_MIRROR:?VOID_MIRROR is not set}
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
mkdir -p "$cache"
tmp=$(mktemp -d "$work/.offline.XXXXXX")
trap 'rm -rf --one-file-system "$tmp"' EXIT
install -d "$tmp/var/db/xbps/keys" "$tmp/etc/xbps.d"
cp /var/db/xbps/keys/*.plist "$keys"/*.plist "$tmp/var/db/xbps/keys/"
# as the installer writes it: Void's default 6.x kernel stays out, linux-mainline comes in
printf 'ignorepkg=linux\nignorepkg=linux-headers\n' > "$tmp/etc/xbps.d/10-pustota-kernel.conf"
fetch() { XBPS_ARCH=x86_64 xbps-install -r "$tmp" -C etc/xbps.d -c "$cache" -S -D -y "$@"; }

echo "    the install's packages (Void current and nonfree, and Pustota's)"
fetch -R "$repo" -R "$mirror/current" -R "$mirror/current/nonfree" \
  base-system pustota-desktop pustota-learn pustota-russian linux-mainline
# Steam's 32-bit libraries: the installer's list, each on its own (a missing one is skipped)
for pkg in $(python3 -c "import importlib.util as u; s=u.spec_from_file_location('i','$root/installer/pustota-installer.py'); m=u.module_from_spec(s); s.loader.exec_module(m); print(' '.join(m.STEAM_32BIT))"); do
  fetch -R "$mirror/current" -R "$mirror/current/nonfree" -R "$mirror/current/multilib" \
    -R "$mirror/current/multilib/nonfree" "$pkg" >/dev/null 2>&1 || echo "    (not available: $pkg)"
done

echo "    indexing the offline repository"
rm -rf "$out"; mkdir -p "$out"
ln "$cache"/*.xbps "$out"/ 2>/dev/null || cp "$cache"/*.xbps "$out"/
# Void's own packages only: Pustota's are in Pustota's (signed) repository on the ISO
for p in "$repo"/*.xbps; do rm -f "$out/$(basename "$p")"; done
XBPS_TARGET_ARCH=x86_64 xbps-rindex -a "$out"/*.xbps >/dev/null
XBPS_TARGET_ARCH=x86_64 xbps-rindex -r "$out" >/dev/null     # older versions kept in the cache: not on the ISO
[[ -s $out/x86_64-repodata ]] || { echo "make-offline-repo: no repository index" >&2; exit 2; }
echo "    $(ls "$out"/*.xbps | wc -l) packages, $(du -sh "$out" | cut -f1)"

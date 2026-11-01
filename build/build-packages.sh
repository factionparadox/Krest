#!/usr/bin/env bash
# Pustota's package repository, build/work/repo: its own files as three ordinary XBPS packages
# made with Void's xbps-create, plus the packages built from srcpkgs/ (build-srcpkgs.sh), all
# indexed with xbps-rindex and signed (sign-repo.sh). XBPS then owns every file Pustota adds:
#   xbps-query -f pustota-desktop      lists them; xbps-remove takes them away again.
#   pustota-desktop  configuration, session and scripts; depends on everything in packages.txt
#   pustota-learn    pustota-learn and its lessons
#   pustota-russian  the Russian kit (and the Piper speech engine); material downloads later
set -Eeuo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
work=$root/build/work
repo=$work/repo
version=$(cat "$root/VERSION")_1
die() { printf 'build-packages: %s\n' "$*" >&2; exit 2; }
command -v xbps-create >/dev/null || die "needs Void's xbps-create (run inside Void)"
rm -rf "$repo" "$work/pkgroot"; mkdir -p "$repo" "$work/pkgroot"

deps() { local d=; for p in "$@"; do d+="$p>=0 "; done; echo "${d% }"; }
conffiles() { (cd "$1" && find etc -type f 2>/dev/null | sed 's|^|/|' | sort | tr '\n' ' '); }
create() {  # create NAME DESTDIR "short description" "deps"
  local name=$1 dest=$2 desc=$3 depends=$4
  (cd "$repo" && xbps-create -A x86_64 -n "$name-$version" -s "$desc" \
    -l "GPL-3.0-or-later" -H "https://github.com/factionparadox/Pustota" \
    -m "Pustota <pustota@localhost>" -D "$depends" -F "$(conffiles "$dest")" "$dest")
}

# ---------------------------------------------------------------- pustota-desktop
d=$work/pkgroot/desktop
cp -a "$root/desktop/root" "$d"
sed "s/@VERSION@/$(cat "$root/VERSION")/" "$d/etc/xdg/fastfetch/config.jsonc.in" > "$d/etc/xdg/fastfetch/config.jsonc"
rm "$d/etc/xdg/fastfetch/config.jsonc.in"
install -Dm644 "$root/packages.txt" "$d/usr/share/pustota/packages.txt"
install -Dm644 "$root/VERSION" "$d/usr/share/pustota/VERSION"
mapfile -t pkgs < <(grep -v '^#' "$root/packages.txt" | tr ' ' '\n' | grep .)
create pustota-desktop "$d" "Pustota: ratpoison, Plan 9 and a battery-first laptop" "$(deps "${pkgs[@]}")"

# ---------------------------------------------------------------- pustota-learn
l=$work/pkgroot/learn
install -Dm755 "$root/learn/pustota-learn" "$l/usr/bin/pustota-learn"
install -d "$l/usr/share/pustota/learn/topics"
install -m644 "$root"/learn/topics/*.md "$l/usr/share/pustota/learn/topics/"
create pustota-learn "$l" "Pustota Learn: understand and inspect the system" "$(deps python3 man-pages void-docs)"

# ---------------------------------------------------------------- pustota-russian
r=$work/pkgroot/russian
install -Dm755 "$root/russian/pustota-russian" "$r/usr/bin/pustota-russian"
install -Dm755 "$root/russian/pustota-content" "$r/usr/bin/pustota-content"
install -d "$r/usr/lib/pustota/content" "$r/usr/share/pustota/russian" "$r/var/lib/pustota/russian"
install -m644 "$root"/russian/fetch-*.py "$root/russian/mirror.json" "$r/usr/lib/pustota/content/"
install -m644 "$root"/russian/{vocab,library,audiobooks,voices}.tsv "$root/russian/VOCAB-SOURCES.md" \
  "$r/usr/share/pustota/russian/"
# Piper (MIT): a self-contained speech engine, pinned to the release Constellation used.
piper=$work/downloads/piper_linux_x86_64-2023.11.14-2.tar.gz
mkdir -p "$work/downloads"
[[ -s $piper ]] || curl -fL --retry 3 -o "$piper.part" \
  https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz
[[ -s $piper ]] || mv "$piper.part" "$piper"
echo "a50cb45f355b7af1f6d758c1b360717877ba0a398cc8cbe6d2a7a3a26e225992  $piper" | sha256sum -c - >/dev/null ||
  { rm -f "$piper"; die "Piper download failed its checksum (deleted; run again)"; }
tar -xzf "$piper" -C "$r/usr/lib/pustota"
[[ -x $r/usr/lib/pustota/piper/piper ]] || die "Piper archive has no piper binary"
create pustota-russian "$r" "Pustota Russian kit: A1 to B2, offline" \
  "$(deps python3 kiwix-tools mpv yt-dlp zstd pipewire ollama-bin)"

# packages Void does not have, built from srcpkgs/ by build-srcpkgs.sh
for pkg in "$work"/void-packages/hostdir/binpkgs/*.xbps; do
  [[ -e $pkg ]] && cp "$pkg" "$repo/"
done
xbps-rindex -a "$repo"/*.xbps
ls -l "$repo"

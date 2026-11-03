#!/usr/bin/env bash
# Рассвет / Rassvet: build the installer ISO, on any x86_64 Linux with sudo (Arch on WSL2 is
# fine).
#
#   bash build/build-iso.sh               -> out/rassvet-x86_64.iso
#   bash build/build-iso.sh --music DIR   your music on it too (default: local/music, if any)
#   bash build/build-iso.sh --no-music    the ordinary ISO even when local/music exists
#
# What it does:
#  1. Guix itself, if this computer has none: Guix 1.5.0's release (SHA-256 checked) in /gnu
#     and /var/guix, its daemon, and the substitute keys of Guix and Nonguix.
#  2. guix time-machine -C channels.scm: the exact Guix and Nonguix Rassvet is pinned to.
#  3. The system (build/template-config.scm); what installing it builds besides (GRUB, its
#     menu), from a dry run of guix system init; and a dry run for a second, differently
#     answered config (build/variant-config.scm): what that one would still build is what each
#     laptop builds for itself, offline, so its inputs go on the stick (build/offline-items.py).
#  4. All of it, exported and compressed: build/work/system.nar.zst.
#  5. The installer image (guix/rassvet/installer.scm), with the archive added: out/.
set -Eeuo pipefail
project=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
say() { printf '\n==> %s\n' "$*"; }
die() { printf '\nRassvet: %s\n' "$*" >&2; exit 2; }
trap 'echo "Rassvet: stopped at line $LINENO (exit $?)" >&2' ERR

music=$project/local/music
while [[ $# -gt 0 ]]; do
  case $1 in
    --music) [[ $# -ge 2 ]] || die "--music needs a folder"; music=$(realpath -m "$2"); shift 2 ;;
    --no-music) music=; shift ;;
    *) die "unknown option: $1 (use --music DIR or --no-music)" ;;
  esac
done
if [[ -n $music ]]; then
  if [[ -d $music && -n $(ls -A "$music" 2>/dev/null) ]]; then
    say "Your music: $music ($(du -shL "$music" | cut -f1))"
  else
    [[ $music == "$project/local/music" ]] || die "no music in $music"
    music=
  fi
fi
[[ $(uname -m) == x86_64 ]] || die "an x86_64 builder is needed"
[[ $EUID -ne 0 || -n ${RASSVET_BUILD_AS_ROOT:-} ]] || die "run as yourself; it asks for sudo when needed"
sudo -v
work=$project/build/work
mkdir -p "$work" "$project/out"

say "Tools: xorriso and zstd"
for tool in xorriso zstd; do
  command -v $tool >/dev/null && continue
  if command -v pacman >/dev/null; then sudo pacman -S --needed --noconfirm libisoburn zstd
  elif command -v apt-get >/dev/null; then sudo apt-get install -y xorriso zstd
  elif command -v dnf >/dev/null; then sudo dnf install -y xorriso zstd
  else die "install $tool first"; fi
done

# --------------------------------------------------------------------- 1. Guix
guix=/var/guix/profiles/per-user/root/current-guix/bin/guix
if ! command -v guix >/dev/null && [[ ! -x $guix ]]; then
  say "Guix 1.5.0 (binary release, SHA-256 checked) into /gnu and /var/guix"
  tarball=$work/guix-binary-1.5.0.x86_64-linux.tar.xz
  [[ -s $tarball ]] || curl -fL --retry 3 -o "$tarball" \
    https://ftp.gnu.org/gnu/guix/guix-binary-1.5.0.x86_64-linux.tar.xz
  echo "aa41025489c5061543e9c48873eaa829b900b2da75d40f9648913622f5f47817  $tarball" | sha256sum -c - ||
    { rm -f "$tarball"; die "the Guix download failed its checksum (deleted; run again)"; }
  tmp=$(mktemp -d)
  tar --warning=no-timestamp -xf "$tarball" -C "$tmp"
  sudo mv "$tmp/var/guix" /var/ && sudo mv "$tmp/gnu" /
  rm -rf "$tmp"
  sudo groupadd --system guixbuild 2>/dev/null || true
  for i in $(seq -w 1 10); do
    sudo useradd -g guixbuild -G guixbuild -d /var/empty -s "$(command -v nologin || echo /usr/bin/false)" \
      -c "Guix build user $i" --system "guixbuilder$i" 2>/dev/null || true
  done
  sudo mkdir -p /root/.config/guix
  sudo ln -sfn /var/guix/profiles/per-user/root/current-guix /root/.config/guix/current
fi
command -v guix >/dev/null || guix_cmd=$guix
guix_cmd=${guix_cmd:-guix}
daemon=$(dirname "$(readlink -f "$(command -v "$guix_cmd" || echo "$guix")")")/guix-daemon
[[ -x $daemon ]] || daemon=/var/guix/profiles/per-user/root/current-guix/bin/guix-daemon
for key in /var/guix/profiles/per-user/root/current-guix/share/guix/{bordeaux,ci}.guix.gnu.org.pub \
           "$project/guix/rassvet/files/nonguix-signing-key.pub"; do
  [[ -f $key ]] && sudo "$guix_cmd" archive --authorize < "$key"
done
if ! pgrep -x guix-daemon >/dev/null; then
  say "Starting the Guix daemon (for this build)"
  sudo sh -c "nohup $daemon --build-users-group=guixbuild \
    --substitute-urls='https://bordeaux.guix.gnu.org https://ci.guix.gnu.org https://substitutes.nonguix.org' \
    >/var/log/guix-daemon-rassvet.log 2>&1 &"
  sleep 3
fi
# the archive of the system is signed with this computer's key; the ISO trusts it
[[ -s /etc/guix/signing-key.pub ]] || sudo "$guix_cmd" archive --generate-key
subs="--substitute-urls=https://bordeaux.guix.gnu.org https://ci.guix.gnu.org https://substitutes.nonguix.org"
# (RASSVET_CHANNELS_FILE: another channels file, for testing a mirror)
tm() { "$guix_cmd" time-machine -C "${RASSVET_CHANNELS_FILE:-$project/channels.scm}" -- "$@"; }

# --------------------------------------------------------------------- 2-3. the system
cd "$project"
say "The system (downloads about 3 GB of prebuilt packages the first time)"
system=$(tm system build -L guix --no-grafts "$subs" build/template-config.scm | tail -n 1)
[[ -d $system ]] || die "the system did not build"
echo "    $system"
# guix system init also needs GRUB and what it makes GRUB's menu with, which system build does
# not touch: ask init itself (a dry run, into an empty folder) and build what it lists
target=$work/init-target
mkdir -p "$target"
init_dry() {   # (it prints nothing when everything is already built)
  tm system init -n -v 2 --skip-checks -L guix --no-grafts "$subs" "$1" "$target" 2>&1 |
    tr '\r' '\n' | { grep -v '^substitute:' || true; }
}
say "What installing it needs besides the system (GRUB, its menu, the initrd)"
init_dry build/template-config.scm > "$work/template-init.log"
mapfile -t needed < <(python3 build/offline-items.py drvs "$work/template-init.log")
echo "    ${#needed[@]} derivations"
[[ ${#needed[@]} -eq 0 ]] || tm build --no-grafts "$subs" "${needed[@]}" >/dev/null
say "A second, differently answered install: what each laptop must build for itself"
init_dry build/variant-config.scm > "$work/variant-init.log"
grep -A40 'would be built' "$work/variant-init.log" | sed 's/^/    /' || true
python3 build/offline-items.py items "$system" "$work/template-init.log" "$work/variant-init.log" \
  > "$work/offline-items.txt"
# what installing GRUB runs (the dry run lists these only while they are not yet in the store)
tm build --no-grafts "$subs" grub-efi efibootmgr mtools efivar >> "$work/offline-items.txt"
echo "    $(wc -l < "$work/offline-items.txt") items to carry"

# --------------------------------------------------------------------- 4. the archive
say "The system archive (every store item the install needs, zstd)"
mapfile -t closure < <("$guix_cmd" gc -R $(cat "$work/offline-items.txt") | sort -u)
echo "    ${#closure[@]} store items, $("$guix_cmd" size "$system" 2>/dev/null | tail -n 1 | awk '{print $2, $3}')"
sudo "$guix_cmd" archive --export "${closure[@]}" | zstd -T0 -12 -q > "$work/system.nar.zst.part"
mv "$work/system.nar.zst.part" "$work/system.nar.zst"
echo "    $(du -h "$work/system.nar.zst" | cut -f1)"

# --------------------------------------------------------------------- 5. the ISO
say "The installer image"
image=$(RASSVET_SIGNING_KEY=/etc/guix/signing-key.pub \
  tm system image -t iso9660 -L guix "$subs" guix/rassvet/installer.scm | tail -n 1)
[[ -s $image ]] || die "the installer image did not build"
iso=$project/out/rassvet-x86_64.iso
[[ -z $music ]] || iso=$project/out/rassvet-personal-x86_64.iso
extra=(-map "$work/system.nar.zst" /rassvet/system.nar.zst)
[[ -z $music ]] || extra+=(-map "$music" /rassvet/music)
rm -f "$iso"
# Guix compresses the store files on the ISO (zisofs); xorriso unpacks them when it rewrites the
# image, so they are compressed again here (a few minutes), leaving out what GRUB reads (the
# kernel, the initrd), exactly as Guix does. The volume date is GRUB's and the initrd's way of
# finding the stick (search --fs-uuid), so it is kept.
uuid=$(xorriso -indev "$image" -pvd_info 2>/dev/null | sed -n 's/^Modif\. Time *: *//p')
[[ $uuid =~ ^[0-9]{16}$ ]] || die "could not read the image's volume date (got '$uuid')"
say "Writing $iso: the installer image, plus the offline system (recompressing the store)"
xorriso -indev "$image" -outdev "$iso" -boot_image any replay \
  -zisofs level=9:block_size=128k \
  -find /gnu -type f -not -wholename '/boot/*' -not -name bzImage -not -name '*.gz' \
    -not -name 'initrd*' -not -name '*.zst' -not -name '*.png' -not -name unicode.pf2 \
    -exec set_filter --zisofs -- \
  "${extra[@]}" -volume_date uuid "$uuid" -commit 2>&1 |
  grep -v '^xorriso : UPDATE' || true
[[ -s $iso ]] || die "xorriso wrote no ISO"
(cd "$project/out" && sha256sum "$(basename "$iso")" > "$(basename "$iso").sha256")
say "Done: $iso ($(du -h "$iso" | cut -f1))"

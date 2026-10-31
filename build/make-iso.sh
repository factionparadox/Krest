#!/usr/bin/env bash
# Pustota ISO, built inside Void glibc (called by build-iso.sh, or run as root on Void).
#  1. Pustota's own XBPS packages (build-packages.sh) into a small local repository.
#  2. Void's live-image tool, void-mklive, pinned to a known commit.
#  3. A live ISO with Void's newest kernel series (linux-mainline, 7.x: the Framework 13 Pro's
#     Panther Lake needs it), Wi-Fi firmware, NetworkManager and the Pustota installer.
# The installer installs Void from Void's signed repositories and Pustota's packages from the ISO.
set -Eeuo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
say() { printf '\n==> %s\n' "$*"; }
die() { printf '\nPustota: %s\n' "$*" >&2; exit 2; }
trap 'echo "Pustota: stopped at line $LINENO (exit $?)" >&2' ERR
[[ $EUID -eq 0 && $(. /etc/os-release; echo "$ID") == void ]] || die "run as root on Void glibc (build-iso.sh does this)"
[[ $(xbps-uhelper arch) == x86_64 ]] || die "x86_64 glibc only"

work=$root/build/work
mkdir -p "$work" "$root/out"
exec 8>"$work/.make-iso.lock"
flock -n 8 || die "make-iso.sh is already running"

say "Pustota packages"
bash "$root/build/build-packages.sh"
repo=$work/repo
ls "$repo"/pustota-*.xbps >/dev/null && [[ -s $repo/x86_64-repodata ]] || die "Pustota packages missing"

say "void-mklive (pinned)"
rev=3aa194bdea9c83de0b5d78fb889a88f000a44fab   # Sep 2026; knows -v linux-mainline
mk=$work/void-mklive
[[ -d $mk/.git ]] || git clone --no-checkout --filter=blob:none https://github.com/void-linux/void-mklive.git "$mk"
git -C "$mk" fetch -q --depth=1 origin "$rev"
git -C "$mk" checkout -q --force --detach "$rev"
[[ $(git -C "$mk" rev-parse HEAD) == "$rev" ]] || die "void-mklive is not at $rev"
stage=$(mktemp -d "$work/.stage.XXXXXX")
trap 'rm -rf --one-file-system "$stage"' EXIT
cp -a "$mk" "$stage/mklive"
# Builds under WSL2 cannot make a private mount namespace: run grub-mkstandalone with chroot.
python3 "$root/build/patch-void-mklive.py" "$stage/mklive/mklive.sh"

say "Live overlay"
ov=$stage/overlay
install -Dm755 "$root/installer/pustota-installer.py" "$ov/usr/lib/pustota/pustota-installer.py"
install -Dm755 "$root/installer/live-network-setup.sh" "$ov/usr/lib/pustota/live-network-setup.sh"
install -Dm755 "$root/installer/pustota-installer" "$ov/usr/bin/pustota-installer"
install -Dm644 "$root/installer/live-bash-profile" "$ov/etc/skel/.bash_profile"
install -Dm644 "$root/installer/live-motd" "$ov/etc/motd"
install -d "$ov/usr/lib/pustota/repo"
cp "$repo"/pustota-*.xbps "$repo/x86_64-repodata" "$ov/usr/lib/pustota/repo/"
cp "$root/packages.txt" "$ov/usr/lib/pustota/packages.txt"

say "Building the ISO (kernel: linux-mainline)"
live_pkgs="python3 dialog gptfdisk xfsprogs dosfstools parted util-linux xtools
  NetworkManager linux-firmware-network linux-firmware-intel sof-firmware intel-ucode"
cd "$stage/mklive"
./mkiso.sh -a x86_64 -b base -- \
  -v linux-mainline -i gzip -s gzip \
  -p "$(echo $live_pkgs)" \
  -S "dbus NetworkManager" \
  -x "$root/installer/live-postsetup.sh" \
  -C "live.autologin" \
  -T "Pustota" -I "$ov" \
  -o "$stage/pustota.iso"
[[ -s $stage/pustota.iso ]] || die "void-mklive produced no ISO"
mv -f "$stage/pustota.iso" "$root/out/pustota-x86_64.iso"
(cd "$root/out" && sha256sum pustota-x86_64.iso > pustota-x86_64.iso.sha256)
say "Built out/pustota-x86_64.iso"

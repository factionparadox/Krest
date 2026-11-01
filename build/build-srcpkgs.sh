#!/usr/bin/env bash
# Pustota's own xbps-src templates (srcpkgs/: packages Void does not have) built with Void's
# xbps-src, the same tool and rules Void builds its whole repository with.
#   -> build/work/void-packages/hostdir/binpkgs/*.xbps
#
# It runs inside the disposable Void build root (build-iso.sh), so it uses xbps-src's
# "ethereal" style, which Void's documentation gives for exactly that: no chroot of its own,
# the build root itself is the masterdir. Never run this on a Void system you use.
set -Eeuo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
work=$root/build/work
vp=$work/void-packages
rev=7be87667ad95aff4124fdcccb68e2c22b5453a26      # void-packages, 31 October 2026
die() { printf 'build-srcpkgs: %s\n' "$*" >&2; exit 2; }
[[ $EUID -eq 0 ]] || die "run through build/build-iso.sh"

mapfile -t pkgs < <(cd "$root/srcpkgs" && ls)
[[ ${#pkgs[@]} -gt 0 ]] || exit 0

if [[ ! -d $vp/.git ]]; then
  git clone --filter=blob:none --no-checkout https://github.com/void-linux/void-packages.git "$vp"
fi
git -C "$vp" fetch -q --depth=1 origin "$rev"
git -C "$vp" checkout -q --force --detach "$rev"
# xbps-src fetches from the mirror the build chose (as Void's own CI swaps its mirror)
if [[ -n ${VOID_MIRROR:-} ]]; then
  sed -i "s|https://repo-default.voidlinux.org|$VOID_MIRROR|g" "$vp"/etc/xbps.d/repos-remote*.conf
fi
for p in "${pkgs[@]}"; do                       # ours, on top of Void's tree
  rm -rf "$vp/srcpkgs/$p"
  cp -a "$root/srcpkgs/$p" "$vp/srcpkgs/$p"
done

cd "$vp"
if [[ -f /.pustota-build-root ]]; then
  # Pustota's disposable build root (made by build-iso.sh): the ethereal style, as Void's CI
  # containers use it: the root itself is the masterdir.
  xbps-install -Sy base-chroot git >/dev/null
  xbps-uhelper arch > /.xbps_chroot_init
  ln -sfn / masterdir
  export XBPS_CHROOT_CMD=ethereal XBPS_ALLOW_CHROOT_BREAKOUT=yes
  for p in "${pkgs[@]}"; do ./xbps-src -m masterdir pkg "$p"; done
else
  # A real Void system: xbps-src's normal, isolated way, as the user who ran sudo.
  user=${SUDO_USER:-}
  [[ -n $user && $user != root ]] || die "on Void, run build-iso.sh from your own account (it uses sudo itself)"
  chown -R "$user" "$vp"
  sudo -u "$user" ./xbps-src binary-bootstrap
  for p in "${pkgs[@]}"; do sudo -u "$user" ./xbps-src pkg "$p"; done
fi
ls -l hostdir/binpkgs/

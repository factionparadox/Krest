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
  # Inside Pustota's build root, xbps-src gets a root of its own holding only base-chroot and
  # git: base-chroot's minimal tools (chroot-bash, chroot-grep ...) conflict with a full Void
  # system, so it cannot go in the build root itself. This is the setup Void documents for its
  # "ethereal" style (common/chroot-style/ethereal.sh): xbps-src runs inside that root, which
  # is its masterdir, entered with a plain chroot (which works under WSL2).
  mirror=${VOID_MIRROR:-https://repo-default.voidlinux.org}
  sr=$work/xbps-src-root
  if [[ ! -x $sr/usr/bin/git ]]; then
    rm -rf "$sr"; mkdir -p "$sr/var/db/xbps/keys"
    cp /var/db/xbps/keys/*.plist "$sr/var/db/xbps/keys/"      # trust Void's key, as this root does
    xbps-install -r "$sr" -Sy -R "$mirror/current/bootstrap" -R "$mirror/current" base-chroot git
  fi
  xbps-uhelper arch > "$sr/.xbps_chroot_init"
  mkdir -p "$sr/etc" "$sr/hostrepo" "$sr/dev" "$sr/proc" "$sr/sys"
  cp -L /etc/resolv.conf "$sr/etc/resolv.conf"
  unmount() { for m in hostrepo sys proc dev; do mountpoint -q "$sr/$m" && umount -R "$sr/$m"; done; true; }
  trap unmount EXIT
  for m in dev proc sys; do mount --rbind "/$m" "$sr/$m"; mount --make-rslave "$sr/$m"; done
  mount --bind "$vp" "$sr/hostrepo"
  # No -m: xbps-src resolves a masterdir given with -m to its real path ("/"), and ethereal mode
  # then refuses it for not being a link to /. Its default, $XBPS_DISTDIR/masterdir, stays the
  # link (Void's own example runs plain "xbps-src pkg"). Its "cp: ... are the same file" about
  # resolv.conf is expected here and harmless.
  ln -sfn / masterdir
  for p in "${pkgs[@]}"; do
    chroot "$sr" /usr/bin/env -i HOME=/root PATH=/usr/bin:/usr/sbin:/bin:/sbin TERM="${TERM:-xterm}" \
      XBPS_CHROOT_CMD=ethereal XBPS_ALLOW_CHROOT_BREAKOUT=yes \
      /bin/bash -c 'cd /hostrepo && ./xbps-src pkg "$1"' _ "$p"
  done
else
  # A real Void system: xbps-src's normal, isolated way, as the user who ran sudo.
  user=${SUDO_USER:-}
  [[ -n $user && $user != root ]] || die "on Void, run build-iso.sh from your own account (it uses sudo itself)"
  chown -R "$user" "$vp"
  sudo -u "$user" ./xbps-src binary-bootstrap
  for p in "${pkgs[@]}"; do sudo -u "$user" ./xbps-src pkg "$p"; done
fi
ls -l hostdir/binpkgs/

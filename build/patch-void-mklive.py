#!/usr/bin/env python3
"""Pustota's changes to the pinned void-mklive (from Archon/Cognoscenti, plus zstd level 3).

WSL2: avoid unsupported mount propagation.

xbps-uchroot wraps grub-mkstandalone in a new mount namespace and invokes
mount --make-private /. Nested under Arch WSL2 this returns EINVAL even though
normal chroot and EFI loop mounts work. grub-mkstandalone doesn't need a
private mount namespace; use the pinned GRUB binaries in the Void target.
The `--` argument belongs to xbps-uchroot, not grub-mkstandalone.
"""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: patch-void-mklive.py FILE/mklive.sh")
path = Path(sys.argv[1])
source = path.read_text()
old = 'xbps-uchroot "$VOIDTARGETDIR" grub-mkstandalone -- \\'
new = 'chroot "$VOIDTARGETDIR" /usr/bin/grub-mkstandalone \\'
if source.count(old) != 1:
    raise SystemExit("Unsupported void-mklive GRUB anchor; refusing ISO build")
# The pinned x86_64 glibc image should not probe non-existent musl/aarch64
# x86_64 indexes; that causes retry loops and unnecessary 404 log output.
repos_old = ('XBPS_REPOSITORY="$XBPS_REPOSITORY '
             '--repository=https://repo-default.voidlinux.org/current '
             '--repository=https://repo-default.voidlinux.org/current/musl '
             '--repository=https://repo-default.voidlinux.org/current/aarch64"')
repos_new = ('XBPS_REPOSITORY="$XBPS_REPOSITORY '
             '--repository=https://repo-default.voidlinux.org/current"')
if source.count(repos_old) != 1:
    raise SystemExit("Unsupported void-mklive repository anchor")
# Pustota: zstd at level 3 for the live image (fast to build, quick to boot). void-mklive
# passes only the method: mksquashfs would use zstd level 15 and dracut --zstd level 15.
squash_old = '-comp "${SQUASHFS_COMPRESSION}" || die "Failed to generate squashfs image"'
squash_new = ('-comp "${SQUASHFS_COMPRESSION}" $([ "$SQUASHFS_COMPRESSION" = zstd ] && '
              'echo -Xcompression-level 3) || die "Failed to generate squashfs image"')
dracut_old = '/usr/bin/dracut -N --"${INITRAMFS_COMPRESSION}" \\'
# quoted, so dracut receives "--compress=zstd -3 -q -T0" as one argument
dracut_new = ('/usr/bin/dracut -N "$([ "$INITRAMFS_COMPRESSION" = zstd ] && echo "--compress=zstd -3 -q -T0" '
              '|| echo "--${INITRAMFS_COMPRESSION}")" \\')
for anchor in (squash_old, dracut_old):
    if source.count(anchor) != 1:
        raise SystemExit("Unsupported void-mklive compression anchor; refusing ISO build")
source = source.replace(squash_old, squash_new).replace(dracut_old, dracut_new)
path.write_text(source.replace(old, new).replace(repos_old, repos_new))

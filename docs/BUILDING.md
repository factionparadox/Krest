# Building Rassvet

    bash build/build-iso.sh

On any x86_64 Linux with sudo (Arch on WSL2 is fine), with about 30 GB free. The first build downloads about 4 GB of prebuilt packages; later builds reuse them.

| Step | What happens |
| --- | --- |
| 1. Guix | If the computer has no Guix: Guix 1.5.0's binary release from ftp.gnu.org, checked against a pinned SHA-256, unpacked into `/gnu` and `/var/guix`; the `guixbuild` group and ten build users; the daemon, with three substitute servers (bordeaux.guix.gnu.org, ci.guix.gnu.org, substitutes.nonguix.org) and their keys. It also makes this computer's archive-signing key (`/etc/guix/signing-key.*`) if there is none. It installs `xorriso` and `zstd` with pacman, apt or dnf. |
| 2. Pinned channels | Every Guix command runs as `guix time-machine -C channels.scm --`: Guix and Nonguix at fixed commits, both authenticated by their channel introductions. |
| 3. The system | `guix system build build/template-config.scm` (a placeholder laptop). Then `build/variant-config.scm`, answered differently (another user, timezone, UUIDs, no autologin): whatever that second build had to build is what a real laptop builds for itself at install, and `build/offline-items.py` lists those derivations' inputs from the build log. Both build with `--no-grafts` (see below). |
| 4. The archive | `guix gc -R` of the template system and those inputs (about 1,100 store items, 10–11 GB), `sudo guix archive --export`, compressed with `zstd -12`: `build/work/system.nar.zst`, about 3.5 GB, signed with this computer's key. |
| 5. The ISO | `guix system image -t iso9660 guix/rassvet/installer.scm`: Guix's own installation system with Nonguix's kernel and firmware, Rassvet's installer on tty1 in place of Guix's, and this computer's key authorised so the stick accepts the archive. xorriso then adds the archive at `/rassvet/system.nar.zst` (and your music at `/rassvet/music`, if any), recompressing the store files as Guix does (zisofs, leaving the kernel and initrd for GRUB) and keeping the volume date, which is how GRUB and the initrd find the stick. |

Output: `out/rassvet-x86_64.iso` (about 6.5 GB) and its `.sha256`. Work files: `build/work/`. The signing key never leaves `/etc/guix`; only its public half goes on the ISO.

## Grafts

Guix applies urgent security fixes as *grafts*: the fixed library is swapped into already-built packages. Working grafts out needs the ungrafted packages too, which would double the archive, so the ISO's system is installed without grafts. The first `rassvet-update` (guix pull, then `sudo guix system reconfigure /etc/config.scm`) applies them, online.

## The install, offline

`installer/rassvet-install.py` asks five questions and one Yes/No, then:

1. GPT on the chosen disk: 1 GiB EFI, swap the size of the RAM (hibernation), XFS root; mkfs; mounts at `/mnt`.
2. `herd start cow-store /mnt`: from here, store writes go to the new disk, not to the stick's RAM.
3. `zstd -dc /rassvet/system.nar.zst | guix archive --import` (percentage on screen).
4. `/etc/config.scm`: a few lines calling `rassvet-operating-system` with the disk's UUIDs and the answers; `/etc/shadow` with the hashed password for root and the user.
5. `guix system init --no-substitutes --no-grafts /mnt/etc/config.scm /mnt`, loading Rassvet's and Nonguix's modules from the stick (the same commits the archive was built from). It builds only the personal files and installs GRUB.

Every command and its output is on screen and in `/var/log/rassvet-install.log`.

## Rassvet's own packages

`guix/rassvet/packages.scm`: `x-terminal` (st-flexipatch at a pinned commit, with `extras/x-terminal/`'s config), `ly` 1.4.1 (Zig 0.16, with its pinned Zig dependencies), `rassvet-desktop` (`desktop/root`), `rassvet-learn` (`learn/`), `rassvet-russian` (`russian/`) and `piper-tts` (Piper's own release, its loader and library paths pointed into the store). The system is `guix/rassvet/system.scm`.

This repository is also a Guix channel (`.guix-channel`), so installed laptops update from it with `guix pull`. Test a change without an ISO:

    guix time-machine -C channels.scm -- build -L guix x-terminal
    guix time-machine -C channels.scm -- system build -L guix --no-grafts build/template-config.scm
    guix time-machine -C channels.scm -- system vm -L guix build/template-config.scm

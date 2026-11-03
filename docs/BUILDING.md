# Building Krest

    bash build/build-iso.sh

On Arch (WSL2 is fine), with sudo and about 15 GB free. Nothing is compiled: it downloads CRUX 3.8's ISO (1.7 GB) and Arch's ready-built kernel and Intel firmware (pacman, Arch's signatures checked), and nothing else. Everything is compiled on the laptop during the install.

| Step | What happens |
| --- | --- |
| 1. Tools | `xorriso`, `cpio`, `rsync`, `curl` and `xz`, with pacman, apt or dnf if any are missing. |
| 2. CRUX's ISO | `crux-3.8.iso` from a CRUX mirror, checked against its SHA-256 (pinned in the script), unpacked to `~/.cache/krest/media`. |
| 3. The stick's kernel | `pacman -Sw` downloads Arch's `linux`, Intel/Realtek firmware and `sof-firmware`; they become one CRUX package, `linux-arch` (modules decompressed for CRUX's kmod; firmware in `/lib/firmware/<kernel version>`, read only by that kernel), in `build/work/packages`. On the laptop it stays as the fallback kernel; Krest's 7.3 kernel is compiled there. |
| 4. The live system | CRUX's live root, with `linux-arch` unpacked into it (its modules replace 6.12's), the installer, `krest-wifi` (a Wi-Fi menu over CRUX's own wpa_supplicant and dhcpcd: NetworkManager isn't on CRUX's ISO, so it's compiled on the laptop with the rest), and a `.bash_profile` that starts it on tty1. CRUX's initramfs gets that kernel's storage, USB and filesystem modules, and a bigger RAM disk. |
| 5. The ISO | CRUX's ISO rewritten by xorriso with the new kernel, initramfs and live root, the packages in `/krest/packages`, this repository in `/krest/repo`, and the boot menu renamed. |

Output: `out/krest-x86_64.iso` and its `.sha256`.

## The install

`installer/krest-install` (bash and dialog) gets you online with nmtui, asks five questions and one Yes/No, then:

1. GPT on the chosen disk: 1 GiB EFI, swap the size of the RAM, XFS root; mkfs; mounts at `/mnt`.
2. CRUX's core from the stick (`pkgadd -r /mnt`), GRUB's tools and dracut from the ISO, and the stick's kernel and NetworkManager.
3. `/etc/fstab`, `/etc/rc.conf` (name, timezone, UK keymap, services), locales, your user (in `wheel`) and the passwords, ly on tty1 (`/etc/inittab`), dracut's initramfs with early microcode, GRUB (EFI, with `resume=` for hibernation). From here the laptop boots.
4. `ports -u`, Krest's ports synced and every source checked, then each port of the `krest` metapackage's dependency tree built with `prt-get install`, in order, counted on screen (`[n of N]`). This is the long part: Firefox, LibreOffice, Rust and the kernel compile here.

If step 4 stops (a failed build, the network), the laptop still boots to ly or a console: log in and run `sudo krest-install --continue`. The log of every build is in `/var/log/pkgbuild/<port>.log`, and the install's in `/var/log/krest-install.log`.

## Krest's ports

`ports/` is a CRUX port collection, installed as `/usr/ports/krest` and searched first by prt-get. Each port is a `Pkgfile` and a `sha256` file listing every source:

- a hash pinned here, checked by `build/krest-ports verify` before pkgmk may build it;
- or `-`: a GitHub source archive that could not be pinned when the port was written. Its hash is recorded on the first download (`/var/lib/krest/sources.sha256`) and every later download must match.

`krest-desktop`, `krest-learn` and `krest-russian` are made from this repository's `desktop/root`, `learn` and `russian`; `build/krest-ports sync` packs them and stamps their version and release. `krest` is the whole system: installing it installs everything.

To try a port on an installed Krest:

    cd /usr/ports/krest/x-terminal && sudo pkgmk -d -i     # or: sudo prt-get update x-terminal

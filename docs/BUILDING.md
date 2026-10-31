# Building Pustota

    bash build/build-iso.sh

| Step | Script | What happens |
| --- | --- | --- |
| 1 | `build/build-iso.sh` | On Arch: installs `curl minisign xz tar`; downloads `void-x86_64-ROOTFS-20250202.tar.xz`, checks `sha256sum.txt` with Void's release key (`build/keys/`) and the tarball against a pinned SHA-256; unpacks it to `~/.cache/pustota/void-glibc-rootfs`; updates XBPS, then the whole root; installs `bash make git curl python3 xz zstd`; mounts this folder at `/work` and runs step 2 inside. On Void it runs step 2 directly. |
| 2 | `build/make-iso.sh` | Runs step 3, then clones void-mklive at `3aa194b` (September 2026), patches it for WSL2 (`patch-void-mklive.py`: `chroot` instead of `xbps-uchroot` for `grub-mkstandalone`, and only the x86_64 glibc repository), and runs `mkiso.sh -b base -- -v linux-mainline …` with the installer, the live network setup and Pustota's packages as an overlay. |
| 3 | `build/build-packages.sh` | `xbps-create` makes `pustota-desktop` (from `desktop/root`, depending on every name in `packages.txt`), `pustota-learn` and `pustota-russian` (with Piper 2023.11.14-2, SHA-256 checked); `xbps-rindex` indexes them in `build/work/repo`. |

Output: `out/pustota-x86_64.iso` and `out/pustota-x86_64.iso.sha256`. Work files stay in `build/work/` (packages, the void-mklive clone, downloads) and `~/.cache/pustota/` (the Void root). Delete either to start fresh.

The live ISO contains Void's base live image, plus:
- `linux-mainline`, `linux-firmware-intel`, `linux-firmware-network`, `sof-firmware` and `intel-ucode`;
- NetworkManager, with dhcpcd, wpa_supplicant and sshd switched off;
- `dialog gptfdisk xfsprogs dosfstools parted xtools`;
- `/usr/lib/pustota/` (the installer and the package repository).

The installed system gets base-system and the three Pustota packages; everything else follows from their dependencies.

## Tests

    python3 -m unittest discover tests

They run on any Linux with Python 3.9 or later, `bash` and `curl`; `zstd` enables one more.

## Changing what is installed

Edit `packages.txt`; each name must be a Void package (search: `xbps-query -Rs NAME`, or <https://github.com/void-linux/void-packages/tree/master/srcpkgs>). The desktop's files are the folder tree under `desktop/root`. Bump `VERSION` when anything changes, so XBPS sees the new packages as an update.

## The Russian content mirror

`build/publish-content.sh` (from Constellation) packs downloaded material into release assets and writes `russian/mirror.json`. The mirror is currently the `content-v1` release on factionparadox/Kirin.

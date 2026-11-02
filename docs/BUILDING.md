# Building Pustota

    bash build/build-iso.sh

| Step | Script | What happens |
| --- | --- | --- |
| 1 | `build/build-iso.sh` | On Arch: installs `curl minisign xz tar`; downloads `void-x86_64-ROOTFS-20250202.tar.xz`, checks `sha256sum.txt` with Void's release key (`build/keys/`) and the tarball against a pinned SHA-256; unpacks it to `~/.cache/pustota/void-glibc-rootfs`; updates XBPS, then the whole root; installs `bash make git curl python3 xz zstd`; mounts this folder at `/work` and runs step 2 inside. On Void it runs step 2 directly. |
| 2 | `build/make-iso.sh` | Runs steps 3 to 5, then clones void-mklive at `3aa194b` (September 2026), patches it (`patch-void-mklive.py`: `chroot` instead of `xbps-uchroot` for `grub-mkstandalone` under WSL2, only the x86_64 glibc repository, and zstd at **level 3** for the squashfs and the live initramfs), and runs `mkiso.sh -b base -- -v linux-mainline -i zstd -s zstd …` with the installer, the live network setup and Pustota's packages as an overlay. |
| 3 | `build/build-srcpkgs.sh` | void-packages at `7be8766` (31 October 2026) with `srcpkgs/` copied in; `xbps-src pkg` for each. In the disposable build root it uses xbps-src's **ethereal** style, as Void's documentation gives for containers (the root is the masterdir; `/.pustota-build-root` marks it); on a real Void system, xbps-src's normal isolated style as your user. |
| 4 | `build/build-packages.sh` | `xbps-create` makes `pustota-desktop` (from `desktop/root`, depending on every name in `packages.txt`), `pustota-learn` and `pustota-russian` (with Piper 2023.11.14-2, SHA-256 checked); the packages from step 3 join them; `xbps-rindex` indexes them all in `build/work/repo`. |
| 5 | `build/sign-repo.sh` | `xbps-rindex --sign` and `--sign-pkg` with `~/.config/pustota/repo-key.pem` (RSA 4096, made on the first build, copied into the build root only while it runs). XBPS then imports the public key from the repository, served on 127.0.0.1 for a moment, which writes it in XBPS's own format; the live image carries it in `/var/db/xbps/keys`, and the installer copies it to the new system. |

Output: `out/pustota-x86_64.iso` and `out/pustota-x86_64.iso.sha256`. Work files stay in `build/work/` (packages, the void-mklive clone, downloads) and `~/.cache/pustota/` (the Void root). Delete either to start fresh.

The live ISO contains Void's base live image, plus:
- `linux-mainline`, `linux-firmware-intel`, `linux-firmware-network`, `sof-firmware` and `intel-ucode`; (`intel-ucode` comes from Void's **nonfree** repository, which the ISO build, the installer and the installed system (`void-repo-nonfree`) all enable);
- NetworkManager, with dhcpcd, wpa_supplicant and sshd switched off;
- `dialog gptfdisk xfsprogs dosfstools parted xtools`;
- `/usr/lib/pustota/` (the installer and the package repository).

The installed system gets base-system and the three Pustota packages; everything else follows from their dependencies.

## Packages Void does not have: `srcpkgs/`

Ordinary xbps-src templates, as in void-packages:

| Template | What it is |
| --- | --- |
| `x-terminal` | X-терминал: st 0.9.3 via st-flexipatch, fetched with git at a pinned commit (checked after checkout); `files/patches.h` and `files/config.h` are Pustota's |
| `intel-lpmd` | Intel's Energy Optimizer 0.1.0 (adds Panther Lake), fetched with git at the tag's commit; built against elogind's sd-bus, run as a runit service in cgroup-v2 isolate mode (no systemd); Pustota's Panther Lake config in `files/` |
| `ani-cli` | v5.1, pinned to commit `c99221d`; its three files are checked against git's bytes |
| `ollama-bin` | Ollama's official v0.40.13 release, SHA-256 pinned, without CUDA/ROCm. It has a `_ollama` user and a runit service, which stays off until the Russian tutor is installed |

To add one, write `srcpkgs/NAME/template` (see Void's [Manual.md](https://github.com/void-linux/void-packages/blob/master/Manual.md)), add NAME to `packages.txt` or to a package's dependencies, and rebuild.

## The online repository

`bash build/publish-repo.sh` uploads `build/work/repo` (the packages, their `.sig2` signatures and the signed index) to the GitHub release `repo-x86_64`. Installed systems list it in `/usr/share/xbps.d/20-pustota-repository.conf`, so `xbps-install -Su` updates Pustota's packages too. Keep the signing key: a new key means installed systems refuse the repository until they trust the new key.

## Branding

`branding/pustota-original.png` is the roundel. `python3 build/make-branding.py` (needs Pillow) makes the cropped logo and icon sizes, the wallpaper, and fastfetch's logo: the roundel in true colour, two pixels per character (`desktop/root/usr/share/pustota/fastfetch-logo.txt`, 44×22).

## Tests

    python3 -m unittest discover tests

They run on any Linux with Python 3.9 or later, `bash` and `curl`; `zstd` enables one more.

## Changing what is installed

Edit `packages.txt`; each name must be a Void package (search: `xbps-query -Rs NAME`, or <https://github.com/void-linux/void-packages/tree/master/srcpkgs>). The desktop's files are the folder tree under `desktop/root`. Bump `VERSION` when anything changes, so XBPS sees the new packages as an update.

## The Russian content mirror

`build/publish-content.sh` (from Constellation) packs downloaded material into release assets and writes `russian/mirror.json`. The mirror is currently the `content-v1` release on factionparadox/Kirin.

## A personal ISO (your music)

Files of your own, such as music you have bought, go in `local/music` (git ignores everything
under `local/`, so they are never committed or pushed). If that folder exists and is not empty,
`build/build-iso.sh` puts it on the ISO, names it `out/pustota-personal-x86_64.iso`, and the
installer copies it into `~/Music` (owned by you). A personal ISO is for your own machines only:
do not share or publish it. `--no-music` builds the ordinary ISO even when `local/music` exists;
`--music DIR` takes the music from another folder. `local/music` may be a link: the same albums
can serve Constellation and Pustota, for example

    mkdir -p local && ln -sfn ~/Constellation/local/music local/music


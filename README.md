<p align="center"><img src="branding/krest-256.png" width="200" alt="Крест"></p>

# Крест · Krest

*Krest* is Russian for "cross": CRUX is Latin for cross, and Crux is the Southern Cross, four stars that are its mark. It's a light, keyboard-driven laptop distribution of its own, built on **CRUX 3.8**: simple, BSD-style, and compiled on the laptop itself for its own processor. It's for writing, for learning Russian, and for lasting on battery. It's made for the Framework Laptop 13 Pro (Intel Core Ultra series 3, Panther Lake), and runs on most UEFI laptops.

| | |
| --- | --- |
| Base | CRUX 3.8: BSD-style rc scripts, ports and prt-get, glibc. No systemd. Everything is built with `-march=native` |
| Kernel | Linux 7.3.1, built on the laptop from Arch Linux's laptop configuration with Krest's changes (`ports/linux`) |
| Disk | GPT: 1 GiB EFI, swap the size of the RAM (for hibernation), **XFS** root |
| Desktop | X11: **ratpoison**, **polybar**, **dmenu** menus, dunst, slock, **ly** on tty1, **X-терминал** (st with scrollback and a Plan 9 look) |
| Tools | Midnight Commander, **acme** and the rest of **Plan 9** (plan9port), Firefox, **WebCord**, **FreeTube**, **Steam**, the **Proton VPN** app, LibreOffice, mpv, zathura, ani-cli, clipboard history, night light, fastfetch, `framework_tool` |
| Laptop | NetworkManager (nmtui, Wi-Fi menu), bluetuith, PipeWire, TLP and thermald, Intel video decoding, sleep that turns into hibernation after two hours on battery (acpid), low-battery hibernation, nftables firewall |
| Russian | Constellation's kit: a 10,000-word drill, the AI tutor (Qwen3.6 35B-A3B through llama.cpp, on the laptop), Piper voices, FSI/DLI/Peace Corps courses, *Между нами*, Wiktionary, audiobooks. UK and Russian phonetic keyboard; Alt+Shift switches |
| Learning | `krest-learn`: lessons and a wiki on how this system works, `explain`, `doctor`, and CRUX's handbook offline |
| Installer | A net install: nmtui, five questions, one Yes/No, then the CRUX install by itself, with the desktop compiled on the laptop |

Not included: fingerprint login. CRUX has no atomic updates or rollback; updates are rebuilds, and older packages stay in `/usr/ports/packages` to reinstall.

## Installing

1. Build the ISO (below) and write it to a USB stick of 4 GB or more.
2. In the laptop's firmware: **Secure Boot off**. Boot the stick in UEFI mode.
3. The installer starts. Plug in a cable or connect to Wi-Fi with nmtui, then answer: the disk, a computer name, your username, your password (twice), the timezone, and whether to log in automatically.
4. Read the summary and choose **Erase and install**. That's the only point of no return.
5. Steps 1–3 take minutes. Step 4 compiles the desktop on the laptop, every build on screen: **expect most of a day** (Firefox, LibreOffice, Rust and the kernel are the big ones). The laptop can already boot after step 3.

If the compiling stops, restart, log in, and run `sudo krest-install --continue`.

## Updating

```sh
krest-update          # Krest's ports (git pull), CRUX's (ports -u), then prt-get sysup
krest-update --dry    # only show what would be rebuilt
prt-get search foo      # find a port; sudo prt-get depinst foo builds and installs it
```

## Software from the AUR

Arch's AUR recipes (PKGBUILDs) are close cousins of CRUX's Pkgfiles, so Krest converts them:

```sh
port-aurum foo        # shows you foo's PKGBUILD, converts it to /usr/ports/aur/foo, checks its
                      # downloads against the PKGBUILD's sha256sums, then builds and installs it
port-aurum -c foo     # convert only, to read or edit the port first
```

Dependencies get CRUX's names (`python-foo` is `python3-foo`, `libx11` is `xorg-libx11`). One that's only on the AUR is converted too; one that's nowhere is listed at the top of the Pkgfile for you to port. Recipes that need systemd say so in the Pkgfile, and may need editing. CRUX's and Krest's own ports always come first.

## Building the ISO

On Arch (WSL2 works) with sudo and about 15 GB free. Nothing is compiled on that computer:

```sh
git clone https://github.com/factionparadox/Krest && cd Krest
bash build/build-iso.sh            # -> out/krest-x86_64.iso and its .sha256
```

It starts from CRUX 3.8's own ISO (SHA-256 checked), adds Arch Linux's ready-built kernel and Intel firmware so the installer works on the 13 Pro, NetworkManager from CRUX's own packages, and the installer. Nothing is compiled on the computer that builds the ISO: everything is compiled on the laptop during the install. See [docs/BUILDING.md](docs/BUILDING.md).

## Layout

```
ports/        Krest's CRUX port collection (Pkgfile + sha256 per port); ports/krest is the whole system
build/        build-iso.sh, krest-ports (sync and verify the collection), crux/ (pkgmk.conf, prt-get.conf)
installer/    krest-install (the installer), iso-binaries, the live system's .bash_profile
desktop/root  the krest-desktop port's files: /etc/krest, /etc/rc.d, skel, the krest-* commands
learn/        krest-learn, its lessons and wiki
russian/      the Russian kit (from Constellation) and its downloaders
branding/     the Крест mark: the Southern Cross
tests/        python3 -m pytest tests
```

## Status

Version 0.3, 3 November 2026. **Not built or booted yet.** The ports, the installer and the build script are written and checked here:

- **Checked here:**
  - every dependency names a CRUX 3.8 port or one of Krest's;
  - every source has a checksum line, and most are pinned, downloaded and hashed here;
  - the scripts parse and pass shellcheck;
  - the collection sync is reproducible;
  - 48 automated tests pass.
- **Not yet run anywhere:** the ISO build, any port build, and the install. Sources on GitHub's archive service couldn't be downloaded from where this was written. They're marked `-` and pinned on your first download.

## Credits

- **CRUX**: the base, its ISO, ports and handbook.
- **Arch Linux**: the kernel configuration Krest's starts from.
- **Archon/Cognoscenti**: the installer's safety design and the learning tool.
- **Constellation/Kirin**: the Russian kit, word list and content mirror.
- **plan9port, ratpoison, polybar, ly, st-flexipatch, Midnight Commander, dmenu, Piper, llama.cpp, Qwen, Kiwix**: their authors.

Krest is GPL-3.0. Every package keeps its own licence. The Russian material keeps its own: US government courses and LibriVox recordings are public domain, the word list is CC BY-SA 4.0, and *Между нами* is CC BY-NC-ND and is downloaded for your personal use only.

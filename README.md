<p align="center"><img src="branding/rassvet-256.png" width="200" alt="Рассвет"></p>

# Рассвет · Rassvet

*Rassvet* is Russian for "dawn". It's a light, keyboard-driven laptop system built on **GNU Guix System**, for writing, for learning Russian, and for lasting on battery. It's made for the Framework Laptop 13 Pro (Intel Core Ultra series 3, Panther Lake) and runs on most UEFI laptops.

The whole system is one Scheme file, [guix/rassvet/system.scm](guix/rassvet/system.scm). Every change makes a new *generation*; the old ones stay in the boot menu, so a bad update is one restart from undone. The store (`/gnu/store`) is read-only: nothing changes a package once it is built.

| | |
| --- | --- |
| Base | Guix System with **Nonguix** (the Linux kernel, firmware and Intel microcode). **Shepherd** for services, elogind for sessions and sleep. No systemd |
| Disk | GPT: 1 GiB EFI, swap the size of the RAM (for hibernation), **XFS** root |
| Desktop | X11: **ratpoison** (each window fills the screen), **polybar**, **dmenu** menus, dunst, slock, **ly** as the login screen, **X-терминал** (Rassvet's terminal: st with scrollback and a Plan 9 look) |
| Tools | **Midnight Commander**, **acme** and the rest of **Plan 9** (plan9port), Firefox, **Steam**, **LibreOffice**, mpv, zathura, ani-cli, clipboard history, night light, fastfetch with the Рассвет logo |
| Laptop | PipeWire sound, brightness and volume keys, TLP and thermald, zram, suspend that turns into hibernation after two hours, low-battery hibernation, tap-to-click, nftables firewall, fingerprint for sudo |
| Russian | Constellation's kit: a 10,000-word drill, the AI tutor (Qwen3.6 35B-A3B through llama.cpp, on the laptop), Piper voices, FSI/DLI/Peace Corps courses, *Между нами*, Wiktionary, audiobooks. English (UK) and Russian phonetic keyboard; Alt+Shift switches |
| Learning | `rassvet-learn`: 22 lessons on how this system works, the Rassvet wiki (Guix explained page by page: generations, Shepherd, channels, packaging, from-Arch), `search`, `explain` (what a command would do, without running it), `doctor` (a read-only map of the running system), and the Guix manual and cookbook offline (`rassvet-handbook`) |
| Installer | Five questions, one Yes/No, then the manual Guix install by itself, **offline** |

Not packaged for Guix, so not included: framework_tool, WebCord, FreeTube, the Proton VPN app, bluetuith and networkmanager_dmenu. The menu hides what is missing and uses the nearest thing: nmtui for Wi-Fi, bluetoothctl for Bluetooth, Firefox for Discord and YouTube, WireGuard files in NetworkManager for the VPN (`rassvet-vpn`).

## Installing

1. Build the ISO (below) and write it to a USB stick of 8 GB or more.
2. In the laptop's firmware: **Secure Boot off**. Boot the stick in UEFI mode.
3. The installer starts by itself. Answer: the disk, a computer name, your username, your password (twice), the timezone (London is preselected), and whether to log in automatically.
4. Read the summary and choose **Erase and install**. That erases the whole disk; it's the only point of no return.
5. Each step and its output show on screen. Then restart.

The steps are the manual Guix install: partitions and `mkfs`, `herd start cow-store /mnt`, the whole system copied from the stick (`guix archive --import`), `/etc/config.scm` with your answers, and `guix system init`. `/var/log/rassvet-install.log` keeps every command with its output; Alt+F3 opens a shell during the install.

It starts in the desktop (or ly asks for your password). **Super+?** shows the keys, **Ctrl+Super+Space** opens the menu.

## Updating

```sh
rassvet-update                    # guix pull, then sudo guix system reconfigure /etc/config.scm
sudo guix system roll-back        # back to the previous generation (or choose it in the boot menu)
guix install hello                # a program just for you, without touching the system
```

The first update also applies Guix's security grafts, which the offline install leaves out (see [docs/BUILDING.md](docs/BUILDING.md)).

## First things to try

```sh
rassvet-learn                     # the lessons; start with architecture
rassvet-learn doctor              # what is running, read-only
rassvet-learn explain "guix system reconfigure /etc/config.scm"
sudo rassvet-content              # download the Russian material (choose the packs)
rassvet-russian path              # the route from A1 to B2
```

| Keys | |
| --- | --- |
| Super+1…9, Super+Shift+1…9 | go to workstation, send the window there |
| Super+Tab | overview: pick a window or workstation |
| Super+q / f / r | close, full size, width 33→50→67→100% |
| Super+Space | run any program (dmenu) |
| Ctrl+Super+w / t / d / v / e / a / p / o / y / g | Firefox / terminal / Discord / video / files (mc) / ani-cli / VPN / office / YouTube / Steam |
| Ctrl+Super+c / r / n / b / m | acme / Russian / Wi-Fi / Bluetooth / sound mixer |
| Ctrl+Super+Space | the Rassvet menu (Russian, Learn, System, Power) |
| Super+x / z / Escape | lock / suspend / power menu |
| Super+Shift+s | screenshot of an area |
| Alt+Shift | English ↔ Russian |
| Ctrl+t then ? | all of ratpoison's own keys |

## Building the ISO

On any x86_64 Linux with sudo (Arch on WSL2 works), with about 30 GB free:

```sh
git clone https://github.com/factionparadox/Pustota && cd Pustota
bash build/build-iso.sh            # -> out/rassvet-x86_64.iso and its .sha256
# with your own music in local/music (git-ignored): -> out/rassvet-personal-x86_64.iso
```

It installs Guix if the computer has none (the 1.5.0 release, SHA-256 checked), then builds everything with `guix time-machine -C channels.scm`: Guix and Nonguix at pinned, authenticated commits. Almost everything comes prebuilt from Guix's and Nonguix's substitute servers; only Rassvet's own packages (ly, X-терминал and the scripts) compile. The first build downloads about 4 GB. Details: [docs/BUILDING.md](docs/BUILDING.md).

This repository is also the **rassvet** Guix channel, which installed laptops pull from. Its commits are not signed, so unlike Guix and Nonguix it has no channel introduction and `guix pull` does not authenticate it.

## Layout

```
channels.scm     Guix and Nonguix, pinned (the ISO's build and the installer use exactly these)
.guix-channel    this repository as a channel (modules in guix/)
guix/rassvet/    system.scm (the operating system), packages.scm (Rassvet's packages),
                 installer.scm (the USB stick), files/ (Nonguix's substitute key)
installer/       rassvet-install.py, the installer on the stick
build/           build-iso.sh, offline-items.py, the two configs the ISO is built from,
                 make-branding.py, publish-content.sh
desktop/root     the rassvet-desktop package: /etc/rassvet, skel, rassvet-* commands
extras/          X-терминал's config.h and patches.h
learn/           rassvet-learn, its lessons and wiki
russian/         the Russian kit (from Constellation) and its downloaders
branding/        the Рассвет sunrise mark
tests/           python3 -m pytest tests
```

## Status

Version 0.2, 3 November 2026.

STATUS-PLACEHOLDER

## Credits

- **GNU Guix** and **Nonguix**: the base, the installation system and the manual this follows.
- **Archon/Cognoscenti**: the installer's safety design and the learning tool, rewritten here.
- **Constellation/Kirin**: the Russian kit, word list and content mirror.
- **plan9port, ratpoison, polybar, ly, Midnight Commander, dmenu, st-flexipatch, Piper, llama.cpp, Qwen, Kiwix**: their authors.

Rassvet is GPL-3.0. Every package keeps its own licence. The Russian material keeps its own: US government courses and LibriVox recordings are public domain, the word list is CC BY-SA 4.0, and *Между нами* is CC BY-NC-ND and is downloaded for your personal use only.

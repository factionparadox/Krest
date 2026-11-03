# How Rassvet is built

Everything is in https://github.com/factionparadox/Pustota and builds on one x86_64 Linux
machine with sudo (Arch in WSL2 works) with:   bash build/build-iso.sh

1. If the machine has no Guix, build-iso.sh installs Guix 1.5.0's binary release (its SHA-256
   checked) into /gnu and /var/guix, starts its daemon and trusts the substitute keys of Guix
   (bordeaux, ci) and Nonguix.
2. guix time-machine -C channels.scm: the exact Guix and Nonguix commits Rassvet is pinned to.
   Both channels are authenticated, so a tampered mirror is refused.
3. It builds the system (build/template-config.scm) and a second, differently answered one
   (build/variant-config.scm); what the second needed is what a laptop must build for itself
   during the install. Almost nothing is compiled: prebuilt packages (substitutes) come from
   Guix's and Nonguix's servers. Rassvet's own packages are guix/rassvet/packages.scm:
   x-terminal, ly, rassvet-desktop, rassvet-learn, rassvet-russian and piper-tts.
4. Every store item the install needs is exported (guix archive --export) and compressed:
   build/work/system.nar.zst.
5. The installer image (guix/rassvet/installer.scm: Guix's own installation system with
   Nonguix's kernel and Rassvet's installer on tty1), with the archive added:
   out/rassvet-x86_64.iso and its .sha256. --music DIR puts your music on it too.

## Changing X-терминал
Like every suckless program its settings are compiled in. In a copy of the repository, edit
extras/x-terminal/config.h (the look and keys) or patches.h (1 switches a patch on), then
build and install your version for yourself:
    git clone https://github.com/factionparadox/Pustota ~/Pustota ; cd ~/Pustota
    guix build -L guix x-terminal          builds it (its output is a /gnu/store path)
    guix install -L guix x-terminal        your profile's copy comes first in PATH
guix remove x-terminal goes back to the system's.

## On this computer
    guix system describe                    the channels this system was built from
    guix show rassvet-desktop               Rassvet's own packages, like any other
    guix gc -R /run/current-system | wc -l  every store item the system needs

Licences: Rassvet is GPL-3.0; each package keeps its own (guix show NAME, line "license");
the Russian material keeps its own (public domain, CC BY-SA, and Между нами's CC BY-NC-ND,
copied only for your personal use).

# How Pustota is built

Everything is in https://github.com/factionparadox/Pustota and runs on one Linux machine (Arch
in WSL2 works) with:   bash build/build-iso.sh

1. build-iso.sh downloads Void's official root filesystem (February 2025), checks it with Void's
   release key (minisign) and a pinned SHA-256, updates it, and builds inside it. Nothing is
   compiled: Pustota is configuration and scripts on top of Void's packages.
2. build-packages.sh turns the desktop/, learn/ and russian/ folders into three XBPS packages
   with Void's xbps-create, indexed with xbps-rindex. Piper (speech) is downloaded once and
   checked against its SHA-256.
3. make-iso.sh runs void-mklive (Void's live-image tool, pinned to one commit) with
   linux-mainline, the Wi-Fi and audio firmware, NetworkManager, the installer and the three
   packages.
4. The installer then installs Void from Void's repository and Pustota from the ISO.

## On this computer
    xbps-query -f pustota-desktop     every file Pustota added
    xbps-query -x pustota-desktop     every package it pulled in
    cat /usr/share/pustota/packages.txt   the same list, grouped and explained

Licences: Pustota is GPL-3.0; each Void package keeps its own licence (xbps-query -p license NAME);
the Russian material keeps its own (public domain, CC BY-SA, and Между нами's CC BY-NC-ND,
copied only for your personal use).

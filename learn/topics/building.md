# How Pustota is built

Everything is in https://github.com/factionparadox/Pustota and runs on one Linux machine (Arch
in WSL2 works) with:   bash build/build-iso.sh

1. build-iso.sh downloads Void's official root filesystem (February 2025), checks it with Void's
   release key (minisign) and a pinned SHA-256, updates it, and builds inside it. Almost nothing
   is compiled: Pustota is configuration and scripts on top of Void's packages, plus its terminal.
2. build-srcpkgs.sh builds what Void lacks (srcpkgs/: x-terminal, intel-lpmd, webcord, freetube, ani-cli, ollama-bin) with Void's own
   xbps-src, the tool every Void package is built with.
   build-packages.sh turns the desktop/, learn/ and russian/ folders into three XBPS packages
   with Void's xbps-create, indexes them with the others (xbps-rindex) and sign-repo.sh signs
   the repository. Piper (speech) is downloaded once and checked against its SHA-256.
3. make-iso.sh runs void-mklive (Void's live-image tool, pinned to one commit) with
   linux-mainline, the Wi-Fi and audio firmware, NetworkManager, the installer and the
   repository, compressing with zstd at level 3. publish-repo.sh puts the repository online.
4. The installer then installs Void from Void's repository and Pustota from the ISO.

## Changing X-терминал
Like every suckless program its settings are compiled in. To change the font, a colour or a
key: in a copy of the repository, edit srcpkgs/x-terminal/files/config.h (the look and keys)
or files/patches.h (1 switches a patch on), then build just that package and install it:
    bash build/build-iso.sh            (rebuilds everything, ISO included), or on Pustota itself:
    git clone https://github.com/void-linux/void-packages ; cd void-packages
    ./xbps-src binary-bootstrap
    cp -r ~/Pustota/srcpkgs/x-terminal srcpkgs/ ; ./xbps-src pkg x-terminal
    sudo xbps-install -R hostdir/binpkgs -f x-terminal

## On this computer
    xbps-query -f pustota-desktop     every file Pustota added
    xbps-query -x pustota-desktop     every package it pulled in
    cat /usr/share/pustota/packages.txt   the same list, grouped and explained

Licences: Pustota is GPL-3.0; each Void package keeps its own licence (xbps-query -p license NAME);
the Russian material keeps its own (public domain, CC BY-SA, and Между нами's CC BY-NC-ND,
copied only for your personal use).

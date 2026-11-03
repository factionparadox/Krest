# How Krest is built

Everything is in https://github.com/factionparadox/Pustota (on this laptop: /usr/src/krest).
The install stick is CRUX 3.8's own ISO with a few things added, made on any x86_64 Linux
machine with sudo (Arch in WSL2 works) by:   bash build/build-iso.sh

1. It fetches CRUX 3.8's ISO and checks it against its published SHA-256.
2. It makes a CRUX build root: every core package from the ISO, installed by pkgadd from
   CRUX's live system (kept in ~/.cache/krest and reused).
3. In that root: ports -u, Krest's collection (build/krest-ports sync and verify), then
   prt-get builds the 7.3 kernel, linux-firmware and NetworkManager. These are the only
   packages built ahead; the CPU target there is x86-64-v3, not -march=native.
4. The installer's live system: CRUX's, with those packages added and krest-install
   starting on tty1; its initramfs gets the new kernel's storage and input modules.
5. The ISO: CRUX's, with the new kernel, live system and initramfs, the packages in
   /krest/packages and this repository in /krest/repo: out/krest-x86_64.iso and its .sha256.
Everything else is compiled on the laptop during the install (krest-learn learn install).

## Krest's ports
ports/ in the repository: one folder per port, each with a Pkgfile and a sha256 file. On the
laptop, build/krest-ports sync copies them to /usr/ports/krest, packs Krest's own
tarballs (krest-desktop from desktop/root, krest-learn, krest-russian) and stamps their
version; verify downloads every source and checks it. krest-learn wiki pkgfiles has the details.

## Changing X-терминал
Like every suckless program its settings are compiled in: config.h (the look and keys) and
patches.h (1 switches a patch on), in the port. Make your own copy of the port, in a
collection of your own that comes first:
    sudo mkdir -p /usr/ports/local
    sudo cp -r /usr/ports/krest/x-terminal /usr/ports/local/
    sudoedit /usr/ports/local/x-terminal/config.h       (raise release= in its Pkgfile too)
    cd /usr/ports/local/x-terminal && sudo pkgmk -um     record the new checksums
Add  prtdir /usr/ports/local  above the other prtdir lines in /etc/prt-get.conf, then
    sudo prt-get update x-terminal
To go back: remove your copy and  sudo prt-get update x-terminal  again.

## On this computer
    cat /usr/share/krest/version          the Krest version installed
    git -C /usr/src/krest log --oneline | head
    prt-get info krest-desktop            Krest's own ports, like any other
    prt-get quickdep krest | wc -w        how many ports the whole system is

Licences: Krest is GPL-3.0; each program keeps its own (the URL in its Pkgfile leads to it);
the Russian material keeps its own (public domain, CC BY-SA, and Между нами's CC BY-NC-ND,
copied only for your personal use).

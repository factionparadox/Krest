# First steps

Press Super+? for the keys. Super+Space opens the menu; everything in it is a plain command you
can also type. Super+Return opens a terminal.

## Three places to learn from
- These lessons (pustota-learn): how THIS system is put together, and why.
- Void's Handbook, installed offline (void-docs): how Void recommends doing things.
- Manual pages (man xbps-install, man sv, ...): exactly what the installed commands accept.

## Start by looking, not changing
    pustota-learn doctor             what is running, in one screen
    pustota-learn explain "sudo xbps-install -Su"   what a command would do (it is NOT run)
    lsblk -f                         disks and filesystems
    sv status /var/service/*         services (needs sudo for some)
    xbps-query -x pustota-desktop    every package Pustota added

## Keeping up to date
    sudo xbps-install -Su            (or Super+Space -> System -> Update everything)
Void is a rolling release: everything updates together. If XBPS says it must update itself
first, run the same command twice.

## Your files and the system's
Your settings are in your home folder (~/.ratpoisonrc, ~/.config/...). System defaults are in
/etc and /usr/share and belong to packages: xbps-query -o /etc/pustota/ratpoisonrc tells you
which. Change your copies, not the packaged ones, and updates will never overwrite your work.

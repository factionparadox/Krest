# First steps

Press Super+? for the keys. Ctrl+Super+Space opens the menu; everything in it is a plain command you
can also type. Super+Return opens a terminal.

## Three places to learn from
- These lessons (rassvet-learn): how THIS system is put together, and why.
- The Guix manual and Cookbook, installed offline (rassvet-handbook, or info guix): how Guix
  is meant to be used.
- Manual pages (man nmcli, man ratpoison, ...): exactly what the installed commands accept.

## Start by looking, not changing
    rassvet-learn doctor             what is running, in one screen
    rassvet-learn explain "guix system reconfigure /etc/config.scm"   what it would do (NOT run)
    cat /etc/config.scm              this laptop's whole system, in a few lines
    guix system list-generations     every system you can go back to
    sudo herd status                 services
    fastfetch                        the system at a glance, with the Рассвет logo

## Keeping up to date
    rassvet-update                   (or Ctrl+Super+Space -> System -> Update everything)
It runs guix pull (the newest Guix, Nonguix and Rassvet), then
sudo guix system reconfigure /etc/config.scm: a new system generation. The old one stays in the
boot menu; sudo guix system roll-back goes back. The first update takes longest: guix pull
compiles Guix itself, and the security grafts the offline installer left out are applied now.
Programs you installed yourself update separately:  guix upgrade

## Your files and the system's
Your settings are in your home folder (~/.ratpoisonrc, ~/.config/...). The system's files are in
/gnu/store and cannot be edited; /etc/rassvet/ratpoisonrc is a link there. Change your own
copies, or the system declaration, and an update never overwrites your work.

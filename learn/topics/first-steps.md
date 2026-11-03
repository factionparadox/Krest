# First steps

Press Super+? for the keys. Ctrl+Super+Space opens the menu; everything in it is a plain command you
can also type. Super+Return opens a terminal.

## Three places to learn from
- These lessons (rassvet-learn): how THIS system is put together, and why.
- The CRUX handbook, offline (rassvet-handbook): how CRUX is meant to be used: ports, pkgutils,
  prt-get, the rc scripts, the kernel.
- Manual pages (man prt-get, man pkgmk, man ratpoison, ...): exactly what the commands accept.

## Start by looking, not changing
    rassvet-learn doctor             what is running, in one screen
    rassvet-learn explain "prt-get sysup"   what it would do (NOT run)
    cat /etc/rc.conf                 hostname, timezone, keymap, the services started at boot
    prt-get diff                     what an update would rebuild
    pkginfo -i                       every installed package and its version
    fastfetch                        the system at a glance, with the Рассвет logo

## Keeping up to date
    rassvet-update                   (or Ctrl+Super+Space -> System -> Update everything)
    rassvet-update --dry             only list what would be rebuilt
It pulls the Rassvet repository into /usr/src/rassvet, syncs and checks Rassvet's ports,
updates CRUX's (ports -u), then rebuilds every installed package whose port has a new
version (prt-get sysup), on this laptop. That can take a while: a new Firefox or kernel is an
hour or more of compiling. If the kernel was rebuilt, restart to use it.

There is no rollback: an update replaces the old packages. The packages built before stay in
/usr/ports/packages, so a single one can go back with  sudo pkgadd -u -f FILE  (rassvet-learn
learn recovery). Configuration files under /etc are not overwritten by an update; the new
versions are put aside, and  sudo rejmerge  shows each one and asks what to keep.

## Your files and the system's
Your settings are in your home folder (~/.ratpoisonrc, ~/.config/...), and an update never
touches them. The system's settings are plain files in /etc that you may edit directly.

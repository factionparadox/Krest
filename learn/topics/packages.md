# XBPS: installing, updating and asking questions

XBPS (the X Binary Package System) is Void's package manager. It downloads signed repository
indexes, checks every package against them, works out dependencies, and remembers which
package owns each file. Pustota itself is three XBPS packages built with Void's own tools:
pustota-desktop (settings and scripts; it depends on every program Pustota uses),
pustota-learn and pustota-russian.

## Ask (read-only)
    xbps-query -Rs mpv             search the repositories (names and descriptions)
    xbps-query -R mpv              details of a package you have not installed
    xbps-query -l                  everything installed
    xbps-query -f mpv              files owned by an installed package
    xbps-query -o /usr/bin/mpv     which package owns a file
    xbps-query -x pustota-desktop  what a package depends on
    xbps-query -X mpv              what depends on it
    xbps-pkgdb -a                  check the package database

## Change
    sudo xbps-install -Su          update everything (do this rather than updating one package)
    sudo xbps-install gimp         install, with dependencies
    sudo xbps-remove -R gimp       remove it and the dependencies nothing else needs
    sudo xbps-remove -Oo           clean the download cache and orphans
    sudo xbps-reconfigure -f PKG   run a package's setup again
Shortcuts in your shell: xi (install), xq (search), xr (remove), xu (update).

Void is rolling: avoid partial upgrades (updating only some of the system). When XBPS updates
itself it asks you to run the update again. The download cache in /var/cache/xbps keeps old
versions: sudo xbps-install -f /var/cache/xbps/NAME-VERSION.x86_64.xbps goes back one.

References: https://docs.voidlinux.org/xbps/ ; man xbps-install ; man xbps-query

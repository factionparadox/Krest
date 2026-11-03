# Ports: where the software comes from

CRUX has no binary repository. A port is a folder with a Pkgfile (a short shell script: name,
version, sources, and a build() function) and a few small files beside it; a collection is a
folder of ports. pkgmk builds a port into a package (a tarball, name#version-release.pkg.tar.zst)
and pkgadd installs it. prt-get does both, in dependency order. Rassvet follows six
collections, in this order (/etc/prt-get.conf: the first one that has a port wins):
    rassvet    /usr/ports/rassvet    Rassvet's own: the kernel, ly, ratpoison, polybar, the
                                     desktop, the Russian kit, WebCord, FreeTube, Proton VPN ...
    core       /usr/ports/core       CRUX's base system
    opt        /usr/ports/opt        CRUX's optional software
    xorg       /usr/ports/xorg       X11
    contrib    /usr/ports/contrib    maintained by CRUX's users
    compat-32  /usr/ports/compat-32  32-bit libraries (Steam)

## Updating them
    sudo ports -u                    CRUX's collections, from the files in /etc/ports
    rassvet-update                   all of it: git pull in /usr/src/rassvet, Rassvet's
                                     collection synced and checked, ports -u, prt-get sysup
ports -u only changes the recipes; nothing is rebuilt until prt-get sysup (or install).

## Trust
CRUX's ports are signed: each carries a .signature that pkgmk checks with the keys in
/etc/ports. Rassvet's collection is not synced by ports at all: rassvet-ports copies it from
the repository, and every source a Rassvet port downloads has a SHA-256 in the port's sha256
file. A few (GitHub archives that could not be pinned when the port was written) are "-" there:
their hash is recorded on the first download, in /var/lib/rassvet/sources.sha256, and every
later download must match it. The repository itself comes from GitHub over HTTPS; its commits
are not signed.

## Look
    ports -l                          the collections
    ports -d                          installed packages whose port has another version
    prt-get diff                      the same, as prt-get sees it (the order above)
    prt-get path firefox              which collection a port comes from
    cat /var/lib/rassvet/sources.sha256

References: man ports ; man prt-get ; rassvet-handbook ; rassvet-learn wiki ports

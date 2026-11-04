# Software: ports, prt-get and pkgutils

On CRUX every program is built from a port on this laptop, then installed as a package. Three
layers do the work:
- ports (sudo ports -u) brings the collections in /usr/ports up to date: only the recipes.
- pkgutils: pkgmk builds a port into a package file (in /usr/ports/packages), pkgadd installs
  it, pkgrm removes it, pkginfo answers questions. /var/lib/pkg/db lists every installed
  package and its files.
- prt-get works out dependencies (the "Depends on:" line of each Pkgfile), runs pkgmk and
  pkgadd in the right order, and compares what is installed with the ports.
There is one set of packages, the system's: installing needs sudo, and everything you install
is there for every user.

## Ask (read-only)
    prt-get search mpv              port names containing the word
    prt-get dsearch player          names and descriptions
    prt-get info mpv                version, description, dependencies, collection
    prt-get deptree mpv             what it needs, as a tree
    prt-get diff                    installed packages with a newer port
    pkginfo -i                      everything installed, with versions
    pkginfo -l mpv                  the files of a package
    pkginfo -o usr/bin/mpv          which package owns a file

## Change
    krest-update                  update everything (the ports, then prt-get sysup)
    sudo prt-get depinst gimp       build and install gimp with whatever it needs
    sudo prt-get install gimp       just gimp (its dependencies must be there already)
    sudo prt-get update gimp        rebuild and reinstall one
    sudo prt-get remove gimp        remove it (pkgrm); its dependencies stay
    sudo prt-get lock gimp          keep sysup from updating it
Shortcuts in your shell (~/.bashrc): pk (search), pi (depinst), pr (remove), pu (krest-update).

Builds use /etc/pkgmk.conf: -O2 -march=native, every core, sources kept in
/usr/ports/distfiles, finished packages in /usr/ports/packages, the work in /var/tmp/pkgmk-NAME.
Each build's output goes to /var/log/pkgbuild/NAME.log. Packages built with -march=native run
on this processor; they are not meant for another computer.

## No partial upgrades, no rollback
Libraries are shared, so after a library update the programs linked against it are rebuilt
when their ports change; prt-get sysup updates everything at once, which is the safe way.
There are no generations: an update replaces the package. The previous package file stays in
/usr/ports/packages, and  sudo port-undo foo  puts it back (and locks foo so the next update
leaves it alone).

Krest's own helpers:
    port-help                     every package command on one page, in plain English
    port-aurum foo                software from Arch's AUR: converts its PKGBUILD to a port
    port-undo foo                 take back an update that broke foo

References: man prt-get ; man pkgmk ; man pkgadd ; krest-handbook ; krest-learn wiki prt-get ;
krest-learn wiki krest-tools

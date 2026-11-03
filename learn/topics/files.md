# Files: Midnight Commander

mc (Ctrl+Super+e) shows two folders side by side. Tab switches sides; the function keys along the
bottom are the actions:
    F3 view   F4 edit (mcedit)   F5 copy   F6 move/rename   F7 new folder   F8 delete   F10 quit
    Ctrl+o    hide the panels and use the shell underneath (Ctrl+o again to come back)
    Ctrl+\    a list of favourite folders     Alt+?  find files
    Enter on an archive (.zip, .tar.gz, a .pkg.tar.zst package) opens it like a folder.

mcedit, mc's editor, is also the system's EDITOR (/etc/profile.d/krest.sh): sudoedit, git and
prt-get edit use it. Ctrl+s or F2 saves, F10 quits. For writing, acme is there too
(krest-learn learn plan9).

## Look around the system with it
CRUX keeps the usual layout: programs in /usr/bin, libraries in /usr/lib, documentation in
/usr/share. /etc is plain files you can edit; /etc/rc.conf and /etc/rc.d are the system's
start-up. The ports are in /usr/ports, the packages built from them in /usr/ports/packages,
and pkginfo -o usr/bin/mc (the path without its first /) tells you which package a file
belongs to. Logs are in /var/log; your
files and settings in your home folder.

References: man mc ; man mcedit ; https://midnight-commander.org/

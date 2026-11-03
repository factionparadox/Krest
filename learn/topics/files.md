# Files: Midnight Commander

mc (Ctrl+Super+e) shows two folders side by side. Tab switches sides; the function keys along the
bottom are the actions:
    F3 view   F4 edit (mcedit)   F5 copy   F6 move/rename   F7 new folder   F8 delete   F10 quit
    Ctrl+o    hide the panels and use the shell underneath (Ctrl+o again to come back)
    Ctrl+\    a list of favourite folders     Alt+?  find files
    Enter on an archive (.zip, .tar.gz) opens it like a folder.

mcedit, mc's editor, is also the system's EDITOR (/etc/profile.d/rassvet.sh): sudoedit, git and
guix edit use it. Ctrl+s or F2 saves, F10 quits. For writing, acme is there too
(rassvet-learn learn plan9).

## Look around the system with it
There is no /usr: Guix keeps every package in /gnu/store, read-only, and the system's programs
and documentation are reached through /run/current-system/profile (bin, share/doc, share/info).
Much of /etc is links into the store, written by the system declaration; /etc/config.scm is
yours. Logs are in /var/log; your files and settings in your home folder.

References: man mc ; man mcedit ; https://midnight-commander.org/

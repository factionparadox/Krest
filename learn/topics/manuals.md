# Handbooks and manual pages: learning on your own

- The CRUX handbook, offline: rassvet-handbook (less /usr/share/doc/crux/handbook.txt). It
  covers the whole system: installing, the ports, pkgutils, prt-get, the rc scripts and
  rc.conf, the kernel. In less: / searches, n finds the next match, q quits.
  rassvet-handbook mc opens it in Midnight Commander beside the Rassvet wiki.
  The web version: https://crux.nu/ (Documentation, then the 3.8 handbook)
- man: every command's manual. Sections: 1 commands, 5 file formats, 8 administration.
      man prt-get ; man pkgmk ; man pkgadd ; man ports ; man 5 fstab ; man 8 nft
      man -k bluetooth   (or apropos bluetooth): search the manuals
- Pkgfiles: /usr/ports/*/NAME/Pkgfile is how any package here was built: short shell scripts,
  worth reading (prt-get cat NAME).
- 9 man: Plan 9's own manuals (9 man acme).
- rassvet-learn: these lessons; explain shows which lesson and manual cover a command.
- rassvet-learn wiki: the Rassvet wiki, CRUX explained page by page (rc, rc-conf, prt-get,
  ports, pkgfiles, pkgutils, sleep, boot, from-arch ...). rassvet-learn search WORD searches
  the lessons and the wiki together.

## A way to learn something new
1. Read the lesson for the idea (rassvet-learn learn services).
2. Read the wiki page for the detail (rassvet-learn wiki rc).
3. Look at the real thing (rassvet-learn doctor; ls /etc/rc.d; cat /etc/rc.conf).
4. Read CRUX's own account (rassvet-handbook, then / and a word).
5. Read the manual for the exact options (man prt-get), or the script itself
   (less /etc/rc.d/tlp).
6. rassvet-learn explain "sudo /etc/rc.d/tlp restart" to check before running.
7. Change one thing, and know how to undo it (keep a copy of the file you change: there is
   no system rollback on CRUX).

Ctrl+Super+Space -> Learn the system has all of these.

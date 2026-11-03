# Handbooks and manual pages: learning on your own

- The Guix manual, offline: rassvet-handbook (or info guix). It covers the whole system:
  packages, guix pull and reconfigure, generations, services, the store. rassvet-handbook
  cookbook is its companion of worked examples (info guix-cookbook).
  In info: arrows and Enter follow a link, l goes back, s searches, i the index, q quits.
  The web version: https://guix.gnu.org/manual/
- info shepherd: the manual of Shepherd, the init and its herd command.
- man: every command's manual. Sections: 1 commands, 5 file formats, 8 administration.
      man 1 nmcli ; man 5 fstab ; man 8 nft ; man herd
      man -k bluetooth   (or apropos bluetooth): search the manuals
- guix COMMAND --help: every guix subcommand lists its options (guix help lists them all).
- 9 man: Plan 9's own manuals (9 man acme).
- rassvet-learn: these lessons; explain shows which lesson and manual cover a command.
- rassvet-learn wiki: the Rassvet wiki, Guix explained page by page (shepherd, guix-packages,
  channels, system, elogind, boot, from-arch ...). rassvet-learn search WORD searches the
  lessons and the wiki together.

## A way to learn something new
1. Read the lesson for the idea (rassvet-learn learn services).
2. Read the wiki page for the detail (rassvet-learn wiki shepherd).
3. Look at the real thing (rassvet-learn doctor; sudo herd status).
4. Read Guix's own account (info "(guix) Services").
5. Read the manual for the exact options (man herd, info shepherd).
6. rassvet-learn explain "sudo herd restart tlp" to check before running.
7. Change one thing, and know how to undo it (on Guix: the previous generation).

Ctrl+Super+Space -> Learn the system has all of these.

# Handbooks and manual pages: learning on your own

- void-docs: Void's Handbook, offline. void-docs opens it; void-docs xbps searches it.
  The web version: https://docs.voidlinux.org/
- man: every command's manual. Sections: 1 commands, 5 file formats, 8 administration.
      man 1 xbps-install ; man 5 fstab ; man 8 sv
      man -k bluetooth   (or apropos bluetooth): search the manuals
- 9 man: Plan 9's own manuals (9 man acme).
- pustota-learn: these lessons; explain shows which lesson and manual cover a command.

## A way to learn something new
1. Read the lesson for the idea (pustota-learn learn services).
2. Look at the real thing (pustota-learn doctor; ls -l /var/service).
3. Read Void's recommended way (void-docs services).
4. Read the manual for the exact options (man sv).
5. pustota-learn explain "sudo sv restart tlp" to check before running.
6. Change one thing, and know how to undo it.

Super+Space -> Learn the system has all of these.

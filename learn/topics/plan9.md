# Plan 9 tools: acme, sam, rc and the plumber

Plan 9 was Bell Labs' successor to Unix, by the same people. plan9port brings its tools to
Linux, installed in /usr/lib/plan9 (PLAN9 and PATH are set in /etc/profile.d/plan9.sh). Run
them with the "9" wrapper so the Plan 9 versions win:  9 acme,  9 man rc.

## acme (Ctrl+Super+c): text as the interface
acme is an editor in which any text is a command. The mouse buttons do the work:
- left selects; MIDDLE-click runs a word (Put saves, Del closes, Get reloads, Undo, New...);
- RIGHT-click opens or finds the word: a file name opens the file, a word finds the next one.
- Type a shell command anywhere (ls, man ratpoison, grep -n TODO *.md) and middle-click it:
  its output appears in a window.
- The tag line above each window is editable: add your own commands there.
On a touchpad: a three-finger tap is the middle button, two fingers the right (libinput).

## sam, rc, the plumber
- sam: acme's predecessor, with a structural regular-expression language; 9 sam.
- rc: Plan 9's shell, simpler quoting than sh;  9 rc.
- plumber: routes right-clicked text to the right program (files to acme, URLs to the browser).
  pustota-acme starts it; its rules are in $PLAN9/plumb/initial.plumbing.

Fonts: pustota-acme asks fontsrv for DejaVu (variable /mnt/font/DejaVuSans/14a/font, fixed
DejaVuSansMono): edit the script's -f and -F to change size.

References: https://9fans.github.io/plan9port/ ; 9 man 1 acme ;
"Acme: A User Interface for Programmers": https://doc.cat-v.org/plan_9/4th_edition/papers/acme/

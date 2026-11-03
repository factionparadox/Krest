# Plan 9 tools: acme, sam, rc and the plumber

Plan 9 was Bell Labs' successor to Unix, by the same people. plan9port brings its tools to
Linux; Krest's plan9port port builds it on this laptop and installs it in /usr/lib/plan9.
/etc/profile.d/plan9.sh sets PLAN9=/usr/lib/plan9 and adds $PLAN9/bin to the end of PATH
for every login shell, so the Linux commands of the same name (rc, man, sam) still come first.
Run Plan 9's with the "9" wrapper:  9 acme,  9 man rc.  krest-acme and krest-plumb set
PLAN9 and PATH for themselves.

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
  krest-acme starts it; its rules are in $PLAN9/plumb/basic.

Fonts: krest-acme asks fontsrv for DejaVu (variable /mnt/font/DejaVuSans/14a/font, fixed
DejaVuSansMono): copy the script to ~/.local/bin and change -f and -F for another size.

References: https://9fans.github.io/plan9port/ ; 9 man 1 acme ;
"Acme: A User Interface for Programmers": https://doc.cat-v.org/plan_9/4th_edition/papers/acme/

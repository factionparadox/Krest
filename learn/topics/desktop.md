# The desktop: X11, the session, the bar, the menus

There is no display manager. tty1 logs you in, ~/.bash_profile runs startx, and startx runs
/usr/bin/pustota-session: a short script, one line per piece. Read it: it is the desktop.

    xrdb        fonts, DPI and terminal colours (/etc/pustota/Xresources, then ~/.Xresources)
    xss-lock    locks the screen with slock on sleep, lid close and Super+x
    dunst       notifications
    pipewire    sound
    udiskie     mounts USB drives
    xbanish     hides the pointer while you type
    pustota-battery  low-battery warnings and hibernation
    clipmenud   remembers what you copy (Super+v picks it again)
    pustota-nightlight  redshift: a warmer screen after sunset, worked out from your timezone
    polybar     the bar: workspace name, window title, layout, volume, light, Wi-Fi, battery, clock
    ratpoison   the window manager (see: pustota-learn learn ratpoison)
Add your own programs in ~/.config/pustota/autostart (an executable script).

## X-терминал, the terminal
Pustota's own: st (suckless) with a handful of its patches and a Plan 9 look, acme's pale
yellow and Go Mono (by Bigelow & Holmes, who drew Plan 9's Lucida). Ctrl+Super+t opens one.
- Select text and it is copied; Ctrl+Shift+v pastes. Shift+PgUp/PgDn or the wheel scroll back.
- Double-click a word, then right-click: the Plan 9 plumber opens it (a file in acme, a URL in
  Firefox, ls(1) as a man page). Rules: /usr/lib/plan9/plumb/basic.
- Ctrl+Shift+PgUp/PgDn: bigger and smaller text.
Its settings are C source, srcpkgs/x-terminal/files/config.h in Pustota's repository, built
into the program (suckless's way: no settings file to parse). pustota-learn learn building
shows how to change one and rebuild it. pustota-term is the script every menu uses to open it;
xterm stays installed in case X-терминал is ever missing.

## Firewall, fingerprint
ufw is on: everything coming in is dropped, everything going out is allowed (sudo ufw status
verbose). To let something in:  sudo ufw allow 22/tcp  (ssh, for example).
The fingerprint reader works for sudo once a finger is added (menu: System -> Fingerprint, or
fprintd-enroll). sudo then waits for a finger first; after 30 seconds, or with no finger
added, it asks for the password. The screen lock (slock) always wants the password.

## Menus
Ctrl+Super+Space is pustota-menu: dmenu lists of "label, command". Super+Space is dmenu_run: type any
program's name. Both are plain scripts; copy /usr/bin/pustota-menu to ~/.local/bin and edit.

## The keyboard
English (UK) and Russian phonetic, Alt+Shift to switch, set in
/etc/X11/xorg.conf.d/00-keyboard.conf. The bar shows EN or RU.

## Change things
    ~/.config/polybar/config.ini      then: pkill polybar; polybar pustota &
    ~/.Xresources                     then: xrdb -merge ~/.Xresources
    ~/.local/share/xorg-session.log   what the session printed, if something did not start

References: man startx ; man polybar ; man dmenu ; man dunst ; man slock

# The desktop: X11, the session, the bar, the menus

There is no display manager. tty1 logs you in, ~/.bash_profile runs startx, and startx runs
/usr/bin/pustota-session: a short script, one line per piece. Read it: it is the desktop.

    xrdb        fonts, DPI and terminal colours (/etc/pustota/Xresources, then ~/.Xresources)
    xss-lock    locks the screen with slock on sleep, lid close and Super+l
    dunst       notifications
    pipewire    sound
    udiskie     mounts USB drives
    xbanish     hides the pointer while you type
    pustota-battery  low-battery warnings and hibernation
    polybar     the bar: workspace name, window title, layout, volume, light, Wi-Fi, battery, clock
    ratpoison   the window manager (see: pustota-learn learn ratpoison)
Add your own programs in ~/.config/pustota/autostart (an executable script).

## Menus
Super+Space is pustota-menu: dmenu lists of "label, command". Super+d is dmenu_run: type any
program's name. Both are plain scripts; copy /usr/bin/pustota-menu to ~/.local/bin and edit.

## The keyboard
English (UK) and Russian phonetic, Alt+Shift to switch, set in
/etc/X11/xorg.conf.d/00-keyboard.conf. The bar shows EN or RU.

## Change things
    ~/.config/polybar/config.ini      then: pkill polybar; polybar pustota &
    ~/.Xresources                     then: xrdb -merge ~/.Xresources
    ~/.local/share/xorg-session.log   what the session printed, if something did not start

References: man startx ; man polybar ; man dmenu ; man dunst ; man slock

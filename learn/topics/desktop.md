# The desktop: X11, the session, the bar, the menus

ly is the login screen: a text box on tty1. Shepherd's agetty on tty1 hands the console to ly
instead of the usual login prompt; its settings, /etc/ly/config.ini, are written by system.scm
(Rassvet's black, white and red, and auto_login_user if you chose automatic login). ly starts
X, with Rassvet's X configuration, and /run/current-system/profile/bin/rassvet-session: a short
script, one line per piece. Read it: it is the desktop.

    xrdb        fonts, DPI and terminal colours (/etc/rassvet/Xresources, then ~/.Xresources)
    xss-lock    locks the screen with slock on sleep, lid close and Super+x
    dunst       notifications
    udiskie     mounts USB drives
    xbanish     hides the pointer while you type
    rassvet-battery  low-battery warnings and hibernation
    clipmenud   remembers what you copy (Super+v picks it again)
    gnome-keyring    the Secret Service, where programs keep passwords
    rassvet-nightlight  redshift: a warmer screen after sunset, worked out from your timezone
    polybar     the bar: workstation, window title, layout, volume, light, Wi-Fi, battery, clock
    ratpoison   the window manager (see: rassvet-learn learn ratpoison)
Add your own programs in ~/.config/rassvet/autostart (an executable script).

## X-терминал, the terminal
Rassvet's own: st (suckless), built from st-flexipatch with scrollback and clickable links, in
Plan 9's look: acme's pale yellow and Go Mono. Ctrl+Super+t opens one.
- Select text and it is copied; Ctrl+Shift+v pastes. Shift+PgUp/PgDn or the wheel scroll back.
- Double-click a word, then right-click: the Plan 9 plumber opens it (a file in acme, a URL in
  Firefox, ls(1) as a man page).
- Ctrl+Shift+PgUp/PgDn: bigger and smaller text.
Its settings are C source (extras/x-terminal/config.h in Rassvet's repository), compiled in;
rassvet-learn learn building shows how to change and rebuild it. rassvet-term is the script
every menu uses to open it; xterm stays installed in case X-терминал is ever missing.

## Menus
Ctrl+Super+Space is rassvet-menu: dmenu lists of "label, command". Super+Space is dmenu_run: type
any program's name. Entries whose program is not installed are hidden: networkmanager_dmenu,
bluetuith, the Proton VPN app and framework_tool are not packaged for Guix, so Wi-Fi opens nmtui,
Bluetooth bluetoothctl, and Discord and YouTube open in Firefox. To change a menu, copy
"$(command -v rassvet-menu)" to ~/.local/bin and edit your copy.

## The keyboard
English (UK) and Russian phonetic, Alt+Shift to switch: one keyboard-layout in system.scm, used
by GRUB, the console and X alike. The bar shows EN or RU.

## Change things
    ~/.config/polybar/config.ini      then: pkill polybar; polybar rassvet &
    ~/.Xresources                     then: xrdb -merge ~/.Xresources
    ~/.local/share/xorg/Xorg.0.log    the X server's log
The files in /etc/rassvet and /etc/ly are links into the read-only store: change your own
copies, or the system declaration (rassvet-learn wiki system).

References: man startx ; man polybar ; man dmenu ; man dunst ; man slock

# Pustota: ly is the login screen on tty1 and starts the desktop itself. Without ly, logging in
# on the first console starts it here (startx runs ~/.xinitrc).
[ -f ~/.bashrc ] && . ~/.bashrc
if [ -z "$DISPLAY" ] && [ ! -e /var/service/ly ] && [ "$(tty)" = /dev/tty1 ]; then
    exec startx -- -keeptty >~/.local/share/xorg-session.log 2>&1
fi

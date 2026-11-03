# Pustota: on the first console, start the desktop (startx runs ~/.xinitrc).
[ -f ~/.bashrc ] && . ~/.bashrc
if [ -z "$DISPLAY" ] && [ "$(tty)" = /dev/tty1 ]; then
    exec startx -- -keeptty >~/.local/share/xorg-session.log 2>&1
fi

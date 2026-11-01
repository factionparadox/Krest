# runit: services

runit is Void's init (process 1) and service supervisor. It is small enough to read. Each
service is a folder in /etc/sv holding an executable "run" script that starts the program in
the foreground; runit restarts it if it stops. A service is enabled by a symbolic link: the
installer made the links in /etc/runit/runsvdir/default, which the running system sees as
/var/service.

    sudo ln -s /etc/sv/sshd /var/service/     enable and start sshd
    sudo rm /var/service/sshd                 disable it (the definition stays in /etc/sv)
    touch /etc/sv/NAME/down                   keep a linked service stopped at boot

That is the whole of "systemctl enable": a link, which you can see with ls.

## Pustota's services
dbus (messages between programs) · elogind (sessions, suspend, lid) · NetworkManager (Wi-Fi) ·
bluetoothd · tlp (battery tuning) · thermald (heat) · chronyd (clock) · socklog-unix and nanoklogd
(the system log) · zramen (compressed swap in RAM) · earlyoom (stops a runaway program before
memory runs out) · agetty-tty1 ... (the text consoles). ollama appears once the tutor is installed.

## Look and control
    ls -l /var/service ; cat /etc/sv/NetworkManager/run
    sudo sv status /var/service/*
    sudo sv restart NetworkManager    (also: up, down, once, status)
    sudo tail -f /var/log/socklog/everything/current     the system log

References: https://docs.voidlinux.org/config/services/ ; man sv ; man runsv ; man runsvdir

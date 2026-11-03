# Services: BSD-style rc scripts

CRUX's init is SysVinit's init, process 1, run in the BSD style: there are no runlevel
folders of links, only a few shell scripts. /etc/inittab says what init runs: /etc/rc at boot
(filesystems, hostname, keymap, the system log), then /etc/rc.multi, which starts every
service named in SERVICES in /etc/rc.conf, in that order, then /etc/rc.local. At shutdown
/etc/rc.shutdown stops them in reverse order.

A service is a script in /etc/rc.d that takes start, stop, restart and (usually) status.
Packages install their own; you do not enable anything except by listing it in SERVICES.

    cat /etc/rc.conf                       SERVICES=(...) is what starts at boot
    ls /etc/rc.d                           every service script installed
    sudo /etc/rc.d/networkmanager status   one service (the scripts are short: read them)
    sudo /etc/rc.d/networkmanager restart  also: start, stop
To start one at every boot, add its name to SERVICES (after anything it needs, such as dbus);
to stop that, take it out. Changes made with the script itself last until the next boot.

## Krest's services (SERVICES in /etc/rc.conf)
lo (the loopback interface) · crond (scheduled jobs) · dbus (messages between programs) ·
networkmanager (Wi-Fi, Ethernet, VPNs) · acpid (the lid and the power button: krest-sleep) ·
tlp (battery tuning) · thermald (heat) · bluetoothd · chronyd (the clock) · krest-firewall
(nftables) · krest-tutor (the Russian tutor, once its model is downloaded).
/etc/rc itself starts udev and the system log; inittab starts ly on tty1 and text logins on
the other consoles. Some pieces are not services at all: polkit, upower and udisks start when
D-Bus asks for them; slock is a setuid program; gnome-keyring and PipeWire run inside your
session.

## Shutting down
    sudo poweroff ; sudo reboot            no password needed (/etc/sudoers.d/krest)

References: man init ; man inittab ; krest-handbook ; krest-learn wiki rc

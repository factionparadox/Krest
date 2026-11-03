# How Pustota fits together

Pustota is Void Linux (x86_64, glibc) with runit as init, XBPS as package manager and an XFS
root, plus a small X11 desktop: ratpoison, polybar, dmenu and Plan 9's acme. Nothing in it is
hidden: every piece is an ordinary Void package or a short, readable script.

## From power button to desktop
1. UEFI firmware starts GRUB from the EFI partition (/boot/efi).
2. GRUB loads Linux (linux-mainline, the 7.x series) and its initramfs (made by dracut).
3. The initramfs finds the XFS root (or resumes from hibernation, using resume= on the
   kernel line) and hands over to runit, process 1.
4. runit runs /etc/runit/1 (one-off setup), then supervises every service linked into
   /var/service: dbus, elogind, NetworkManager, bluetoothd, tlp, thermald, chronyd, zramen ...
5. ly, the login screen on tty1, logs you in (automatically, if you chose that).
6. ly starts X and the session in /usr/share/xsessions/pustota.desktop: /usr/bin/pustota-session.
7. pustota-session starts the bar, notifications, sound and the screen lock, then ratpoison.

## Where things live
/etc/sv/NAME              service definitions (a run script each)
/var/service/             the services runit is running (links into /etc/sv)
/etc/pustota/             Pustota's desktop defaults: ratpoisonrc, polybar.ini, Xresources
~/.ratpoisonrc ~/.config/polybar/config.ini   your settings (they include the defaults)
/etc/xbps.d/              your package-manager settings (ignorepkg=linux is here)
/usr/share/pustota/       the package list, the keys sheet, these lessons
/var/lib/pustota/russian  the Russian material, once downloaded

## Look for yourself (nothing here changes anything)
    pustota-learn doctor
    ls -l /var/service
    xbps-query -x pustota-desktop
    cat /usr/bin/pustota-session

Next: pustota-learn learn install (what the installer did, step by step).

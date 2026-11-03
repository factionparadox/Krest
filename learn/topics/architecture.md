# How Krest fits together

Krest is CRUX 3.8 (x86_64): BSD-style rc scripts as init, ports and prt-get for software,
glibc, an XFS root, and a small X11 desktop: ratpoison, polybar, dmenu and Plan 9's acme. There
is no systemd and no elogind. Almost everything is compiled on this laptop, for this processor
(-march=native), from ports: CRUX's own collections plus Krest's, which comes from the
Krest repository kept in /usr/src/krest. The `krest` port has no files of its own; its
dependency list is the whole system, so installing it installs everything.

## From power button to desktop
1. UEFI firmware starts GRUB from the EFI partition (/boot/efi).
2. GRUB loads the kernel (/boot/vmlinuz-7.3.1-krest, built from the `linux` port) and its
   initramfs, which dracut made with Intel's microcode at the front.
3. The initramfs finds the XFS root, or resumes from hibernation (resume= on the kernel line),
   and starts init, process 1.
4. init reads /etc/inittab: /etc/rc prepares the system (filesystems, hostname, keymap, the
   system log), then /etc/rc.multi starts every service named in SERVICES in /etc/rc.conf:
   dbus, networkmanager, acpid, tlp, thermald, bluetoothd, chronyd, the firewall, the tutor ...
5. inittab runs ly on tty1 instead of a text login (it logs you in by itself if you chose that).
6. ly starts X and the session in /usr/share/xsessions/krest.desktop: krest-session.
7. krest-session starts sound, the bar, notifications, the screen lock, then ratpoison.

## Where things live
/usr/src/krest              the Krest repository (krest-update pulls it)
/usr/ports/                   the ports: core, opt, xorg, contrib, compat-32 and krest
/usr/ports/distfiles, packages    downloaded sources; every package built here
/var/lib/pkg/db               the list of installed packages and their files
/etc/rc.conf                  hostname, timezone, keymap and the services started at boot
/etc/rc.d/                    one script per service (start, stop, restart, status)
/etc/pkgmk.conf /etc/prt-get.conf   how ports are built, and in which order collections count
/etc/krest/                 ratpoisonrc, polybar.ini, Xresources
~/.ratpoisonrc ~/.config/polybar/config.ini   your settings (they include the defaults)
/var/lib/krest/russian      the Russian material, once downloaded

## Look for yourself (nothing here changes anything)
    krest-learn doctor
    cat /etc/rc.conf
    pkginfo -i | wc -l                how many packages are installed
    prt-get diff                      which ports are newer than what is installed
    less "$(command -v krest-session)"

Next: krest-learn learn install (what the installer did, step by step).

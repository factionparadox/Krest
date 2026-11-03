# How Rassvet fits together

Rassvet is GNU Guix System (x86_64) with the Nonguix channel: GNU Shepherd as init, Guix as
package manager, an XFS root, and a small X11 desktop: ratpoison, polybar, dmenu and Plan 9's
acme. There is no systemd anywhere. The whole system is one declaration in Scheme,
guix/rassvet/system.scm in Rassvet's channel; /etc/config.scm on this laptop is a few lines
that call it with your disk's UUIDs, your name and your choices.

## From power button to desktop
1. UEFI firmware starts GRUB from the EFI partition (/boot/efi).
2. GRUB lists the current system and every older generation; it loads Linux (Nonguix's full
   kernel) and its initrd straight from /gnu/store.
3. The initrd (Guix's, with Intel's microcode in front) finds the XFS root, or resumes from
   hibernation (resume= on the kernel line), and hands over to Shepherd, process 1.
4. Shepherd starts the services system.scm declares: udev, dbus, elogind, NetworkManager,
   bluetooth, ntpd, nftables, tlp, thermald, zram, earlyoom, guix-daemon ...
5. agetty on tty1 hands the console to ly, the login screen (it logs you in by itself if you
   chose that).
6. ly starts X and the session in /run/current-system/profile/share/xsessions/rassvet.desktop:
   rassvet-session.
7. rassvet-session starts the bar, notifications, the screen lock, then ratpoison.

## Where things live
/gnu/store/                   every package, each in its own folder; read-only
/run/current-system           the running system generation (a link into the store)
/run/current-system/profile   the system's programs: bin/, share/ (there is no /usr)
/etc/config.scm               this laptop's system: the one file of it that is yours to edit
/etc/rassvet/                 ratpoisonrc, polybar.ini, Xresources (links into the store)
~/.ratpoisonrc ~/.config/polybar/config.ini   your settings (they include the defaults)
~/.guix-profile               the packages you installed yourself (guix install)
/var/lib/rassvet/russian      the Russian material, once downloaded

## Look for yourself (nothing here changes anything)
    rassvet-learn doctor
    cat /etc/config.scm
    guix system describe              this generation: its channels, kernel, config file
    sudo herd status                  every service
    less "$(command -v rassvet-session)"

Next: rassvet-learn learn install (what the installer did, step by step).

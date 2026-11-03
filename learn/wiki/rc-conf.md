# rc.conf, fstab and inittab: the system's files

On CRUX the system is its files. There is no declaration to rebuild: you edit a file in /etc,
and it takes effect at the next boot, or when you restart what reads it. Keep a copy before a
large change (cp /etc/rc.conf /etc/rc.conf.old): there is no rollback.

## /etc/rc.conf
Read by /etc/rc at boot and by rc.multi and rc.shutdown. The installer set:
  FONT=default           the console font (setfont's name; see: locale)
  KEYMAP=uk              the console keyboard (X has its own: see: locale)
  TIMEZONE=Europe/London one of /usr/share/zoneinfo, as you chose
  HOSTNAME=rassvet       this computer's name, as you chose (also in /etc/hosts)
  SERVICES=(lo crond dbus networkmanager acpid tlp thermald bluetoothd chronyd
            rassvet-firewall rassvet-tutor)
                         started in this order at boot (see: rc)
Change one with sudoedit /etc/rc.conf. HOSTNAME, KEYMAP and TIMEZONE are applied at the next
boot; a service added to SERVICES can be started now with sudo /etc/rc.d/NAME start.

## /etc/fstab
What /etc/rc checks and mounts at boot: the root (XFS) and /boot/efi by UUID, the swap
partition, /dev/pts and /dev/shm (see: filesystems). After an edit, sudo mount -a tries it.

## /etc/inittab
What init runs. The parts Rassvet changed or relies on:
  id:2:initdefault:                       boot to runlevel 2 (multi-user)
  rc::sysinit:/etc/rc                     the boot script
  rs:S1:wait:/etc/rc.single ; rm:2:wait:/etc/rc.multi ; rd:06:wait:/etc/rc.shutdown
  c1:2:respawn:/usr/bin/ly                ly on tty1, in place of agetty (the installer's
                                          one change)
  c2 ... c6                               text logins on tty2 to tty6 (Ctrl+Alt+F2 ...)
After an edit:  sudo init q  makes init read it again. To have a text login on tty1 instead
of ly, put back an agetty line for c1 like the others.

## Other files that are the system
  /etc/default/grub         the kernel command line (see: boot)
  /etc/pkgmk.conf           how ports are built ; /etc/prt-get.conf: which collections
  /etc/sudoers.d/rassvet    who may use sudo (see: users)
  /etc/ly/config.ini        the login screen, automatic login
  /etc/X11/xorg.conf.d/30-rassvet.conf   X's keyboard, touchpad and graphics driver
  /etc/nftables.d/rassvet.nft            the firewall (see: network)
  /etc/rassvet/             ratpoisonrc, polybar.ini, Xresources
  /etc/profile.d/rassvet.sh EDITOR and the video settings for every login
Files that came in a package are protected on update: if the package brings a new version,
yours stays and the new one waits in /var/lib/pkg/rejected for sudo rejmerge (see: pkgutils).

## What there is not
No generations, no atomic updates and no rollback. An update rebuilds packages one at a time
and replaces each as it goes; if something breaks, the way back is the previous package file
(see: prt-get) and your copies of the files you changed.

See also: rc, boot, filesystems, pkgutils ; man fstab ;
man inittab ; rassvet-handbook

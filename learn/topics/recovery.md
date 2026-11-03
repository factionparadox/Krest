# When something breaks

Find the first layer that failed, collect the exact error, then change one thing.
firmware -> GRUB -> kernel/initramfs -> XFS root -> init and /etc/rc -> services -> ly -> X
-> ratpoison

## An update went wrong
CRUX has no generations and no rollback: krest-update rebuilds packages and replaces the old
ones. What you have instead:
- The previous package file. Every build lands in /usr/ports/packages as
  NAME#VERSION-RELEASE.pkg.tar.zst, and an older version stays until a build of the same
  name and version overwrites it:
      ls /usr/ports/packages/NAME#*
      sudo pkgadd -u -f /usr/ports/packages/NAME#OLDVERSION-1.pkg.tar.zst
      sudo prt-get lock NAME                 so the next sysup leaves it alone
- The build log, if it was a build that failed: /var/log/pkgbuild/NAME.log. A failed build
  changes nothing installed; fix the cause and run krest-update again.
- Configuration: an update does not overwrite your files in /etc; sudo rejmerge offers the
  new versions it put aside.
- After a library update, a program may complain of a missing .so: rebuild it with
  sudo prt-get update NAME (revdep, from the prt-utils port, finds them all).

## The desktop does not start
Log in on another console (Ctrl+Alt+F2) and read /var/log/Xorg.0.log. Fix ~/.xinitrc or
~/.ratpoisonrc, or move them aside: the defaults are in /usr/share/krest/skel/ (cp from there
to put one back). If ly itself is the trouble, comment out its line (c1) in /etc/inittab and
run sudo init q: tty1 is free again, and startx from it starts the desktop.

## A service fails
    for s in /etc/rc.d/*; do echo "${s##*/}: $(sudo $s status 2>&1 | head -n 1)"; done
    sudo tail -n 50 /var/log/messages     the system log; some services have /var/log/NAME.log
    sudo /etc/rc.d/NAME restart
    sudo sh -x /etc/rc.d/NAME start       every line the script runs, to see where it stops

## It does not boot at all
Boot the Krest stick, press Alt+F2 for a root shell, mount the disk and go into it, as the
CRUX handbook does:
    mount /dev/nvme0n1p3 /mnt ; mount /dev/nvme0n1p1 /mnt/boot/efi
    for d in dev dev/pts proc sys run sys/firmware/efi/efivars; do mount --bind /$d /mnt/$d; done
    chroot /mnt /bin/bash
Then, inside: put an old kernel back (krest-learn learn kernel), remake the initramfs
(dracut --force --early-microcode --kver 7.3.1-krest /boot/initramfs-7.3.1-krest.img),
or reinstall GRUB:
    grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=Krest
    grub-mkconfig -o /boot/grub/grub.cfg
The XFS root can be checked only unmounted, from the stick:  xfs_repair /dev/nvme0n1p3

## Logs
    sudo tail -n 100 /var/log/messages
    sudo dmesg | tail -n 50
    less /var/log/krest-install.log ; ls /var/log/pkgbuild

References: krest-handbook ; man pkgadd ; man prt-get ; man xfs_repair

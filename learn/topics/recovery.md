# When something breaks

Find the first layer that failed, collect the exact error, then change one thing.
firmware -> GRUB -> kernel/initramfs -> XFS root -> runit -> services -> login -> X -> ratpoison

## The desktop does not start
Log in on another console (Ctrl+Alt+F2) and read ~/.local/share/xorg-session.log. Fix
~/.xinitrc or ~/.ratpoisonrc, or move them aside: cp /etc/skel/.ratpoisonrc ~ puts back the
default.

## A new kernel misbehaves
GRUB, "Advanced options": boot the previous kernel. Then  sudo xbps-reconfigure -f linux7.N
(rebuild its initramfs), or wait for the next update.

## An update went wrong (there are no snapshots: this is the undo)
XFS has no snapshots, so Pustota cannot roll the whole system back the way ZFS boot
environments do. What it has instead: XBPS keeps every package it downloaded in /var/cache/xbps,
so the version you had before an update is still on the disk.

1. Find what changed. The update's own output, or the log of what XBPS did:
       grep -h 'xbps' /var/log/socklog/everything/current | tail -n 50
       xilog | tail -n 30                         what was installed or updated last (xtools)
       ls -t /var/cache/xbps | head -n 20          the newest downloads first
2. Put the old version back. xdowngrade (from xtools) installs a package file from the cache:
       ls /var/cache/xbps/firefox-*                 the versions you still have
       sudo xdowngrade /var/cache/xbps/firefox-133.0_1.x86_64.xbps
3. Stop the next update bringing the broken one straight back:
       sudo xbps-pkgdb -m hold firefox               (and later: -m unhold firefox)
       xbps-query -H                                 what is on hold
4. Check the database is consistent:  sudo xbps-pkgdb -a

Keep the cache: sudo xbps-remove -O deletes the old versions. Do that only when things work
(it frees space: du -sh /var/cache/xbps). The kernel has its own safety net, above: Void keeps
the previous one until  sudo vkpurge rm  removes it.

If the desktop itself will not start after an update, do this from another console
(Ctrl+Alt+F2). If nothing boots, use the install stick (below) and run the same commands
inside  xchroot /mnt.

## It does not boot at all: repair from the install stick
Boot the Pustota stick, then on tty2 (user anon, password voidlinux):
    sudo mount /dev/nvme0n1p3 /mnt ; sudo mount /dev/nvme0n1p1 /mnt/boot/efi
    sudo xchroot /mnt                 a shell inside the installed system
    xbps-reconfigure -fa ; grub-install --target=x86_64-efi --efi-directory=/boot/efi \
        --bootloader-id=Pustota ; grub-mkconfig -o /boot/grub/grub.cfg
The XFS root can be checked only unmounted:  sudo xfs_repair /dev/nvme0n1p3

## Logs
    sudo tail -n 100 /var/log/socklog/everything/current
    sudo dmesg | tail -n 50
    less /var/log/pustota-install.log

References: https://docs.voidlinux.org/installation/guides/chroot.html ; man xfs_repair ;
https://docs.voidlinux.org/xbps/troubleshooting/

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

## An update went wrong
Old packages are in /var/cache/xbps:  sudo xbps-install -f /var/cache/xbps/NAME-OLDVERSION...
sudo xbps-pkgdb -a checks the package database.

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

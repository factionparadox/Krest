# When something breaks

Find the first layer that failed, collect the exact error, then change one thing.
firmware -> GRUB -> kernel/initrd -> XFS root -> Shepherd -> services -> ly -> X -> ratpoison

## An update went wrong: go back a generation
Every guix system reconfigure (every rassvet-update) makes a new system generation and keeps
the old ones, kernel and all. Going back is a whole-system undo:
    sudo guix system roll-back            the previous generation becomes the current one
    guix system list-generations          what there is to go back to
    sudo guix system switch-generation 7  any one of them
or, if it does not boot: in GRUB, "GNU system, old configurations...", and pick an older
entry. Booting an old entry does not change the default; roll back once it is up.
Your own packages have the same undo:  guix package --roll-back  (and guix pull --roll-back
for Guix itself). Nothing is deleted until you delete generations and run guix gc.

## The desktop does not start
Log in on another console (Ctrl+Alt+F2) and read ~/.local/share/xorg/Xorg.0.log. Fix
~/.xinitrc or ~/.ratpoisonrc, or move them aside: the defaults are in
/run/current-system/profile/share/rassvet/skel/ (cp from there to put one back).

## A service fails
    sudo herd status                      which ones are stopped or failing
    sudo herd status NAME                 its state and recent messages
    sudo tail -n 50 /var/log/messages     the system log; some services have /var/log/NAME.log
    sudo herd restart NAME

## It does not boot at all
First try an older generation from GRUB: that covers almost every case. If even that fails
(a broken disk, GRUB itself gone), boot the Rassvet stick, press Alt+F3 for a root shell,
mount the disk and go into it, as in the Guix manual's "Chrooting into an existing system":
    mount /dev/nvme0n1p3 /mnt ; mount /dev/nvme0n1p1 /mnt/boot/efi
    for d in /dev /proc /sys; do mount --rbind $d /mnt$d; done
    chroot /mnt /bin/sh
    source /var/guix/profiles/system/profile/etc/profile
    source /home/YOU/.config/guix/current/etc/profile
    guix-daemon --build-users-group=guixbuild --disable-chroot &
    guix system reconfigure /etc/config.scm       rebuilds the system and reinstalls GRUB
The XFS root can be checked only unmounted, from the stick:  xfs_repair /dev/nvme0n1p3

## Logs
    sudo tail -n 100 /var/log/messages
    sudo dmesg | tail -n 50
    less /var/log/rassvet-install.log

References: info "(guix) Chrooting into an existing system" ; info "(guix) Invoking guix system" ;
man xfs_repair

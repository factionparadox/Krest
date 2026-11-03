# Disks and filesystems: GPT, EFI, swap and XFS

The installer split the disk (GPT) into three partitions, which lsblk -f shows:
  1. EFI system partition, 1 GiB, FAT32, mounted at /boot/efi: GRUB lives here.
  2. swap, the size of the RAM: hibernation writes memory here, and it is the overflow when
     memory runs short (there is no zram).
  3. the root filesystem, XFS, at /: everything else, /usr/ports and its builds included.
NVMe partitions are named with a p: /dev/nvme0n1p1, p2, p3.

They are in /etc/fstab, by UUID, which the installer wrote; edit it like any file
(man 5 fstab), then sudo mount -a to try a new line before restarting.

## Why XFS
XFS is fast with large files and many files at once, and very mature. It can grow
(xfs_growfs) but never shrink, and it has no snapshots: on CRUX there is no system rollback
either, so your undo for the system is the old package files in /usr/ports/packages, and for
your files, a backup. Check it from the install stick, unmounted, with xfs_repair; while
mounted, xfs_scrub checks online.

## Look
    lsblk -f ; findmnt / ; df -h
    cat /etc/fstab
    swapon --show
    xfs_info /                        XFS geometry
    du -sh /usr/ports/distfiles /usr/ports/packages /var/tmp/pkgmk-*  what building keeps
Old sources and packages pile up in /usr/ports/distfiles and packages; delete the ones you no
longer need (keep the last package of anything you may want to go back to).

## TRIM
Nothing trims the SSD on a schedule. Now and then:
    sudo fstrim -av
or once a week through crond: sudo crontab -e, and the line  30 12 * * 0 /sbin/fstrim -a

## Danger
wipefs, sfdisk, mkfs.* and dd destroy data in a moment. Back up before touching partitions.
USB sticks and drives are mounted by udiskie (through udisks) when you plug them in; by hand,
udisksctl mount -b /dev/sdX1, or sudo mount.

References: https://docs.kernel.org/admin-guide/xfs.html ; man xfs ; man lsblk ; man fstab

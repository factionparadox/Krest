# Disks and filesystems: GPT, EFI, swap and XFS

The installer split the disk (GPT) into three partitions, which lsblk -f shows:
  1. EFI system partition, 1 GiB, FAT32, mounted at /boot/efi: GRUB lives here.
  2. swap, the size of the RAM: hibernation writes memory here. (Day-to-day swapping happens
     first in zram, compressed RAM, which is faster; the partition is mostly for hibernation.)
  3. the root filesystem, XFS, at /: everything else, the store (/gnu/store) included.
NVMe partitions are named with a p: /dev/nvme0n1p1, p2, p3.

There is no /etc/fstab to edit: the file systems and swap are fields of the operating system
(by UUID, from /etc/config.scm), and Guix mounts them. /gnu/store is mounted a second time,
read-only, over itself: only guix-daemon writes there.

## Why XFS
XFS is fast with large files and many files at once, and very mature. It can grow
(xfs_growfs) but never shrink, and it has no snapshots; on Guix that matters less, because
system generations are the undo (rassvet-learn learn recovery). Check it from the install
stick, unmounted, with xfs_repair; while mounted, xfs_scrub checks online.

## Look
    lsblk -f ; findmnt / ; df -h
    findmnt /gnu/store                the read-only bind mount
    swapon --show ; zramctl
    xfs_info /                        XFS geometry
    du -sh /gnu/store ; guix gc -F 20G   the store's size; free space until 20 GB are free

## Danger
wipefs, sgdisk, mkfs.* and dd destroy data in a moment. Back up before touching partitions.
USB sticks and drives mount by themselves (udiskie, through udisks); its notification and
findmnt show where.

References: https://docs.kernel.org/admin-guide/xfs.html ; man xfs ; man lsblk ;
info "(guix) File Systems"

# Disks and filesystems: GPT, EFI, swap and XFS

The installer split the disk (GPT) into three partitions, which lsblk -f shows:
  1. EFI system partition, 1 GiB, FAT32, mounted at /boot/efi: GRUB lives here.
  2. swap, the size of the RAM: hibernation writes memory here. (Day-to-day swapping happens
     first in zram, compressed RAM, which is faster; the partition is mostly for hibernation.)
  3. the root filesystem, XFS, at /: everything else.
NVMe partitions are named with a p: /dev/nvme0n1p1, p2, p3.

## Why XFS
XFS is fast with large files and many files at once, and very mature. Two things to know:
it can grow (xfs_growfs) but never shrink, and it has no snapshots (rollback here means older
packages from the XBPS cache, or a backup). Check it from the install stick, unmounted, with
xfs_repair; while mounted, xfs_scrub checks online.

## Look
    lsblk -f ; findmnt / ; df -h
    cat /etc/fstab                    mounts by UUID (written by xgenfstab -U)
    swapon --show ; zramctl
    xfs_info /                        XFS geometry

## Danger
wipefs, sgdisk, mkfs.* and dd destroy data in a moment. Back up before touching partitions.
USB sticks and drives mount by themselves (udiskie) under /run/media/YOU.

References: https://docs.kernel.org/admin-guide/xfs.html ; man xfs ; man fstab ; man lsblk

# Filesystems and disks

## Pustota's layout
  nvme0n1p1   1 GiB   FAT32   /boot/efi   the EFI system partition (boot loader)
  nvme0n1p2   = RAM   swap                hibernation; also overflow beyond zram
  nvme0n1p3   rest    XFS     /           everything else
  zram0       RAM     swap                compressed swap in memory (zramen), used first
See it: lsblk -f ; findmnt ; swapon --show

## /etc/fstab
One line per filesystem to mount at boot: what (by UUID, so renamed disks do not matter),
where, type, options, dump, fsck order. The installer wrote it with xgenfstab -U.
  blkid                          the UUIDs
  sudo mount -a                  test fstab without rebooting (an error here would stop a boot)
Add  nofail  to the options of a disk that is not always plugged in.

## XFS
XFS is a journalling filesystem from SGI, built for speed with large files and many parallel
writes, and with very fast filesystem checks.
  xfs_info /                     its geometry (block size, log, features)
  sudo xfs_growfs /              grow to fill an enlarged partition (online)
  sudo xfs_fsr                   defragment (rarely needed)
  sudo xfs_repair /dev/nvme0n1p3 check and repair: only unmounted, from the install stick
  cp --reflink=always a b        an instant copy that shares data until either is changed
Things XFS cannot do: shrink, and snapshots (there is no rollback; see pustota-learn learn
recovery for the way back from a bad update).

## TRIM
SSDs stay fast when told which blocks are free. Void runs no TRIM on its own, so Pustota does
it weekly: /etc/cron.weekly/fstrim, run by the snooze-weekly service (see: time).
  sudo fstrim -av                now, by hand (takes seconds)
  ls -l /var/cache/snooze/       when the weekly jobs last ran

## USB sticks and drives
udiskie (started with the session) mounts them as they are plugged in, under
/run/media/YOU/LABEL, and notifies you. To unmount: udiskie-umount /run/media/YOU/LABEL, or
udisksctl unmount -b /dev/sda1. exFAT (exfatprogs) and NTFS (ntfs-3g, and the kernel's ntfs3)
work as well as FAT and Linux filesystems.

Format a stick (this erases it: check the name with lsblk first):
  sudo mkfs.exfat -n LABEL /dev/sdX1

## Space
  df -h -x tmpfs -x devtmpfs     free space
  du -sh ~/* | sort -h           what is large in your home
  xhog | head                    the largest packages (xtools)
  sudo xbps-remove -O            old packages in the cache

See also: boot, xbps ; man fstab ; man xfs ; man xfs_repair ; man fstrim ;
https://docs.voidlinux.org/config/ssd.html ; https://docs.kernel.org/admin-guide/xfs.html

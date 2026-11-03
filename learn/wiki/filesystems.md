# Filesystems and disks

## Krest's layout
  nvme0n1p1   1 GiB   FAT32   /boot/efi   the EFI system partition (boot loader)
  nvme0n1p2   = RAM   swap                hibernation, and overflow when memory runs short
  nvme0n1p3   rest    XFS     /           everything else, /usr/ports and its builds included
On a disk too small for that swap, there is no swap partition and the root is p2. There is
no zram.
See it: lsblk -f ; findmnt ; swapon --show

## /etc/fstab
The installer wrote it, by UUID:
  UUID=...  /          xfs   defaults,noatime  0 1
  UUID=...  /boot/efi  vfat  umask=0077        0 2
  UUID=...  swap       swap  defaults          0 0
  devpts    /dev/pts   devpts  noexec,nosuid,gid=tty,mode=0620  0 0
  shm       /dev/shm   tmpfs   defaults                         0 0
/etc/rc mounts everything in it at boot (after checking the filesystems marked 1 or 2) and
turns on the swap. To add a disk that is always there:
  sudo blkid                                  its UUID
  UUID=...  /data  ext4  defaults,noatime  0 2     a new line in /etc/fstab
  sudo mkdir /data ; sudo mount -a            try it now, before a restart depends on it
For a disk that is not always plugged in, add nofail, or leave it to udiskie.

## XFS
XFS is a journalling filesystem from SGI, built for speed with large files and many parallel
writes, and with very fast filesystem checks.
  xfs_info /                     its geometry (block size, log, features)
  sudo xfs_growfs /              grow to fill an enlarged partition (online)
  sudo xfs_repair /dev/nvme0n1p3 check and repair: only unmounted, from the install stick
  cp --reflink=always a b        an instant copy that shares data until either is changed
XFS cannot shrink, and has no snapshots. CRUX has no system rollback either: your files'
undo is a backup, and the system's the old package files (see: pkgutils).

## TRIM
SSDs stay fast when told which blocks are free. Nothing does it on a schedule here:
  sudo fstrim -av                now, by hand (takes seconds)
  sudo crontab -e                and a line such as  30 12 * * 0 /sbin/fstrim -a  for every
                                 Sunday (see: time)

## USB sticks and drives
krest-session starts udiskie, which mounts them through udisks as they are plugged in and
notifies you with the folder. By hand:
  udisksctl mount -b /dev/sda1 ; udisksctl unmount -b /dev/sda1
  sudo mount /dev/sda1 /mnt      the plain way
exFAT (exfatprogs), NTFS (ntfs-3g, and the kernel's ntfs3) and FAT (dosfstools) work as well as
Linux filesystems.
Format a stick (this erases it: check the name with lsblk first):
  sudo mkfs.exfat -n LABEL /dev/sdX1

## Space
  df -h -x tmpfs -x devtmpfs     free space
  du -sh ~/* | sort -h           what is large in your home
  du -sh /usr/ports/distfiles /usr/ports/packages    sources and packages kept from builds
  sudo rm -rf /var/tmp/pkgmk-*   build folders left by failed builds (none run meanwhile)

See also: boot, prt-get ; man fstab ; man xfs ; man xfs_repair ; man fstrim ;
https://docs.kernel.org/admin-guide/xfs.html

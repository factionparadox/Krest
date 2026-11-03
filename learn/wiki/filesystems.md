# Filesystems and disks

## Rassvet's layout
  nvme0n1p1   1 GiB   FAT32   /boot/efi   the EFI system partition (boot loader)
  nvme0n1p2   = RAM   swap                hibernation; also overflow beyond zram
  nvme0n1p3   rest    XFS     /           everything else, /gnu/store included
  zram0       16 GB   swap                compressed swap in memory (zstd), used first
On a disk too small for that swap, there is no p2 and the root is p2.
See it: lsblk -f ; findmnt ; swapon --show ; zramctl

## Declared, not in fstab
The file systems are the operating system's file-systems field: / and /boot/efi by UUID (from
/etc/config.scm's #:root-uuid and #:efi-uuid), plus Guix's %base-file-systems (/proc, /sys,
/dev/pts, the read-only bind mount of /gnu/store and so on). Swap is swap-devices, by UUID.
Guix mounts them; there is no /etc/fstab to edit. To add a disk that is always there:

  (file-system (mount-point "/data") (device (uuid "...")) (type "ext4")
               (mount? #t) (create-mount-point? #t))

in an operating-system wrapping Rassvet's (see: system), consed onto
(operating-system-file-systems base). blkid shows the UUIDs. For a disk that is not always
plugged in, leave it to udiskie instead.

## XFS
XFS is a journalling filesystem from SGI, built for speed with large files and many parallel
writes, and with very fast filesystem checks.
  xfs_info /                     its geometry (block size, log, features)
  sudo xfs_growfs /              grow to fill an enlarged partition (online)
  sudo xfs_repair /dev/nvme0n1p3 check and repair: only unmounted, from the install stick
  cp --reflink=always a b        an instant copy that shares data until either is changed
XFS cannot shrink, and has no snapshots; the system's undo is its generations
(rassvet-learn learn recovery), and your files' undo is a backup.

## TRIM
SSDs stay fast when told which blocks are free. fstrim-service-type in system.scm runs
fstrim on every mounted filesystem once a week, as an mcron job (see: time).
  sudo fstrim -av                now, by hand (takes seconds)
  sudo herd schedule mcron       when it next runs

## USB sticks and drives
udiskie (started with the session) mounts them through udisks as they are plugged in, and
notifies you with the folder. To unmount: udiskie-umount PATH, or udisksctl unmount -b /dev/sda1.
exFAT (exfatprogs), NTFS (ntfs-3g, and the kernel's ntfs3) and FAT (dosfstools) work as well as
Linux filesystems.

Format a stick (this erases it: check the name with lsblk first):
  sudo mkfs.exfat -n LABEL /dev/sdX1

## Space
  df -h -x tmpfs -x devtmpfs     free space
  du -sh ~/* | sort -h           what is large in your home
  du -sh /gnu/store              the store; guix gc frees what no generation uses
  guix size firefox              a package and its dependencies

See also: boot, guix-packages ; info "(guix) File Systems" ; info "(guix) Swap Space" ;
man xfs ; man xfs_repair ; man fstrim ; https://docs.kernel.org/admin-guide/xfs.html

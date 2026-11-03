# What the installer did (the manual Guix install, automated)

The Guix manual's manual installation goes: partition, make filesystems, mount at /mnt,
herd start cow-store /mnt, write /mnt/etc/config.scm, guix system init. The Rassvet installer
did exactly those steps, in that order, after your one "Erase and install", and with no network:
every package came from the USB stick. Its log is in /var/log/rassvet-install.log: every
command it ran, with its output.

## The steps, as commands
1. Partitions (GPT, sgdisk): 1 GiB EFI (FAT32), swap the size of your RAM, XFS for the rest
       mkfs.vfat -F 32 -n EFI /dev/nvme0n1p1 ; mkswap -L swap /dev/nvme0n1p2
       mkfs.xfs -L Rassvet /dev/nvme0n1p3
   (on a disk too small for that much swap, there is no swap partition and no hibernation)
2. Mount the root at /mnt and the EFI partition at /mnt/boot/efi; swapon the swap.
3. herd start cow-store /mnt     from here on, what Guix stores goes onto the new disk,
                                 not into the stick's memory
4. zstd -dc system.nar.zst | guix archive --import     the whole system from the stick
5. /mnt/etc/config.scm: (use-modules (rassvet system)) and one call,
   (rassvet-operating-system #:host-name ... #:user ... #:timezone ... #:autologin? ...
    #:efi-uuid ... #:root-uuid ... #:swap-uuid ...). Your password, hashed, into /etc/shadow
   for you and for root; Guix keeps it when it creates the accounts.
6. guix system init --no-substitutes --no-grafts /mnt/etc/config.scm /mnt
   builds the few personal pieces (accounts, the GRUB menu) and installs GRUB.
No grafts: Guix's security fixes are applied as "grafts", which would need the network. The
first rassvet-update applies them.

## See the result
    cat /etc/config.scm ; lsblk -f
    guix system list-generations     generation 1 is the installed one
    less /var/log/rassvet-install.log

Reference: info "(guix) Manual Installation"

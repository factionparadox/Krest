# What the installer did (the manual Void install, automated)

Void's handbook installs "via chroot": you partition, make filesystems, install base-system
into /mnt, write fstab, chroot in, set things up and install GRUB. The Pustota installer did
exactly those steps, in that order, after your one "Erase and install". Its log is in
/var/log/pustota-install.log: every command it ran, with its output.

## The steps, as commands
1. Partitions (GPT):  sgdisk  ->  1 GiB EFI (FAT32), swap the size of your RAM, XFS for the rest
       mkfs.vfat -F 32 /dev/nvme0n1p1 ; mkswap /dev/nvme0n1p2 ; mkfs.xfs /dev/nvme0n1p3
2. Mount them at /mnt/target (root), /mnt/target/boot/efi, and swapon the swap.
3. Copy Void's signing keys, then install:
       xbps-install -r /mnt/target -S base-system pustota-desktop pustota-learn pustota-russian
   with "ignorepkg=linux" in /etc/xbps.d so Void's 6.x kernel stays out and linux-mainline
   (7.x, which the Framework 13 Pro needs) goes in.
4. fstab from the mounted filesystems, by UUID:   xgenfstab -U /mnt/target > /mnt/target/etc/fstab
5. Name, language, time, keyboard: /etc/hostname; en_GB.UTF-8 and ru_RU.UTF-8 uncommented in
   /etc/default/libc-locales; /etc/locale.conf; /etc/localtime; KEYMAP in /etc/rc.conf.
6. Into the new system (chroot): useradd -m -G wheel,audio,video,... you; chpasswd; a sudoers
   file letting the wheel group use sudo.
7. Services: a link in /etc/runit/runsvdir/default for each (ln -s /etc/sv/NAME ...).
8. xbps-reconfigure -fa  (builds the locales and, through dracut, the initramfs)
9. grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=Pustota
   grub-mkconfig -o /boot/grub/grub.cfg   (resume=UUID=... for hibernation was added first)

## See the result
    cat /etc/fstab ; lsblk -f
    grep -v '^#' /etc/default/libc-locales | grep .
    ls -l /etc/runit/runsvdir/default
    less /var/log/pustota-install.log

Reference: https://docs.voidlinux.org/installation/guides/chroot.html

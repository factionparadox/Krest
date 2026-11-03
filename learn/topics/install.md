# What the installer did (the CRUX handbook's install, automated)

The CRUX handbook's installation goes: partition, make filesystems, mount at /mnt, install the
core packages, write fstab and rc.conf, build a kernel, install a boot loader. The Rassvet
installer (rassvet-install) did those steps, in that order, after your one "Erase and install",
then compiled the rest of the system. Its log is /var/log/rassvet-install.log: every command
it ran, with its output.

## The steps, as commands
0. The network: nmtui, if there was no cable. The install needs it (the desktop is compiled
   from sources downloaded during the install).
1. Partitions (GPT, sfdisk): 1 GiB EFI (FAT32), swap the size of your RAM, XFS for the rest
       mkfs.fat -F 32 -n EFI /dev/nvme0n1p1 ; mkswap -L swap /dev/nvme0n1p2
       mkfs.xfs -L Rassvet /dev/nvme0n1p3
   (on a disk too small for that much swap, there is no swap partition and no hibernation)
   Then the root at /mnt, the EFI partition at /mnt/boot/efi, swapon.
2. pkgadd -r /mnt for every package in the stick's crux/core, GRUB and its tools, then the
   stick's ready-built kernel, linux-firmware and NetworkManager: the laptop can boot and get
   online before anything is compiled.
3. Your settings: /etc/fstab (by UUID), /etc/rc.conf (HOSTNAME, TIMEZONE, KEYMAP=uk,
   SERVICES), locales (en_GB, ru_RU, en_US), your account (wheel, audio, video, input, users)
   and the passwords, hashed, for you and root. The repository to /usr/src/rassvet, the CRUX
   handbook to /usr/share/doc/crux, pkgmk.conf and prt-get.conf, ly on tty1 in /etc/inittab,
   then dracut (microcode first) and GRUB, with resume=. From here the laptop boots.
4. Compiling: ports -u, rassvet-ports sync and verify (Rassvet's collection, every source
   checked), then prt-get quickdep rassvet gives the build order of the whole system, and
   prt-get install builds each port not yet installed. This is the long step: hours.
   Then your home folder from /usr/share/rassvet/skel, and ly's settings.

If step 4 stopped (a failed download, a build error), the system still boots, though tty1
stays empty until ly has been built: log in on another console (Ctrl+Alt+F2) and carry on
where it stopped:
    sudo rassvet-install --continue
A failed build's log is /var/log/pkgbuild/NAME.log.

## See the result
    cat /etc/fstab /etc/rc.conf ; lsblk -f
    pkginfo -i | wc -l
    less /var/log/rassvet-install.log

Reference: rassvet-handbook (the CRUX handbook's installation chapter)

# Рассвет wiki: CRUX, explained

A reference for the system under Rassvet, in the manner of the Arch Wiki: what each part is,
how CRUX does it, the files and commands, and worked examples. The lessons
(rassvet-learn learn) are the short guided tour; this is where to look things up.

Read a page:      rassvet-learn wiki rc
Search all pages: rassvet-learn search hibernate
In acme or mc:    the pages are plain text in /usr/share/rassvet/learn/wiki/

## Coming from Arch
  from-arch       pacman, systemctl, journalctl, mkinitcpio, the AUR: the CRUX equivalents

## The system
  rc-conf         /etc/rc.conf, /etc/fstab, /etc/inittab: the files that are the system
  rc              init and services: /etc/rc, rc.multi, the rc.d scripts, writing one
  logging         syslog, /var/log/messages, build logs, dmesg
  sleep           suspend and hibernate without a session manager: rassvet-sleep, acpid
  boot            UEFI, GRUB, dracut's initramfs, the kernel command line, microcode
  kernel          the linux port, its configuration, old kernels, modules
  users           accounts, groups and what each allows, sudo, PAM
  locale          locales, the keyboard layout, console font, time zone
  time            chronyd and the clock; crond

## Packages
  prt-get         search, depinst, sysup, diff, remove, lock: everyday software
  pkgutils        pkgadd, pkgrm, pkginfo, pkgmk, rejmerge, and /var/lib/pkg/db
  pkgfiles        writing a port: the Pkgfile, pkgmk, footprints, Rassvet's sha256 files
  ports           the collections, ports -u, Rassvet's collection, signatures

## Hardware and devices
  framework       this laptop: what it needs, what Rassvet sets for it and why, known issues
  filesystems     fstab, XFS, TRIM, USB drives, exFAT/NTFS
  network         NetworkManager, DNS, Wi-Fi, VPN, the nftables firewall
  sound           PipeWire and WirePlumber without systemd or elogind
  graphics        Intel: Mesa, VA-API video decoding, Vulkan
  firmware        linux-firmware, microcode, framework_tool
  handbook        the CRUX handbook, offline (rassvet-handbook)

Every page ends with its sources: the CRUX handbook (offline: rassvet-handbook), the manual
pages and upstream documentation. When a page and a manual disagree, the manual is right;
please fix the page.

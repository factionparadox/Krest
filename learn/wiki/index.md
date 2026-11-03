# Рассвет wiki: Guix System, explained

A reference for the system under Rassvet, in the manner of the Arch Wiki: what each part is,
how Guix does it, the files and commands, and worked examples. The lessons
(rassvet-learn learn) are the short guided tour; this is where to look things up.

Read a page:      rassvet-learn wiki shepherd
Search all pages: rassvet-learn search hibernate
In acme or mc:    the pages are plain text in /run/current-system/profile/share/rassvet/learn/wiki/

## Coming from Arch
  from-arch       pacman, systemctl, journalctl, mkinitcpio, the AUR: the Guix equivalents

## The system
  system          /etc/config.scm, system.scm, reconfigure, generations, changing the system
  shepherd        init and services: herd, declaring a service, Rassvet's services
  logging         syslog, /var/log/messages, each service's log, dmesg
  elogind         sessions, seats, suspend and hibernate, the lid, polkit
  boot            UEFI, GRUB and generations, the initrd, the kernel command line, microcode
  kernel          Nonguix's linux, old kernels, modules, out-of-tree modules
  users           declared accounts, groups and what each allows, sudo, PAM
  locale          locales, the keyboard layout, console font, time zone
  time            ntpd and the clock; mcron, Guix's cron

## Packages
  guix-packages   guix search/install/remove/upgrade, profiles, generations, guix gc
  guix-tools      guix show, edit, graph, size, describe, time-machine, shell ...
  guix-packaging  writing a package, guix build -L, Rassvet's channel
  channels        guix, nonguix and rassvet; guix pull; substitutes; authentication

## Hardware and devices
  framework       this laptop: what it needs, what Rassvet sets for it and why, known issues
  filesystems     file systems in the declaration, XFS, TRIM, USB drives, exFAT/NTFS
  network         NetworkManager, DNS, Wi-Fi, VPN, the nftables firewall
  sound           PipeWire and WirePlumber on Guix
  graphics        Intel: Mesa, VA-API video decoding, Vulkan
  firmware        linux-firmware, microcode, fwupd
  handbook        the Guix manual and Cookbook, offline (info guix, rassvet-handbook)

Every page ends with its sources: the Guix manual (offline: info guix), the manual pages and
upstream documentation. When a page and a manual disagree, the manual is right; please fix the page.

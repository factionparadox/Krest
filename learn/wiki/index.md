# Пустота wiki: Void Linux, explained

A reference for the system under Pustota, in the manner of the Arch Wiki: what each part is,
how Void does it, the files and commands, and worked examples. The lessons
(pustota-learn learn) are the short guided tour; this is where to look things up.

Read a page:      pustota-learn wiki runit
Search all pages: pustota-learn search hibernate
In acme:          the pages are plain text in /usr/share/pustota/learn/wiki/

## Coming from Arch
  from-arch       pacman, systemctl, journalctl, mkinitcpio, the AUR: the Void equivalents

## The system
  runit           init and services: stages, sv, writing a service, logs, user services
  logging         socklog, svlogd, vlogger, dmesg: where messages go
  elogind         sessions, seats, suspend and hibernate, the lid, polkit
  boot            UEFI, GRUB, dracut, the kernel command line, microcode
  kernel          linux-mainline and linuxN.M, vkpurge, modules, DKMS
  users           accounts, groups and what each group allows, sudo, PAM
  locale          glibc locales, rc.conf, console font, keyboard layouts, time zone
  time            chrony and the clock; cron (Void ships none) and snooze

## Packages
  xbps            every xbps-* tool, configuration, repositories, keys, holds, the cache
  xtools          the helper scripts: xlocate, xdowngrade, xcheckrestart, xchroot ...
  xbps-src        building packages from templates; Pustota's own srcpkgs/
  repositories    current, nonfree, multilib, debug; mirrors; Pustota's signed repository

## Hardware and devices
  filesystems     fstab, XFS, TRIM, USB drives, exFAT/NTFS
  network         NetworkManager, DNS, Wi-Fi, ufw
  sound           PipeWire and WirePlumber on Void
  graphics        Intel: Mesa, VA-API video decoding, Vulkan
  firmware        linux-firmware, microcode, fwupd, framework_tool

Every page ends with its sources: the Void Handbook (offline: void-docs), the manual pages and
upstream documentation. When a page and a manual disagree, the manual is right; please fix the page.

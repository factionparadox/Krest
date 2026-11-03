# From Arch to CRUX

Arch and CRUX are close relatives in spirit (Arch began as a CRUX-inspired distribution, and
Arch's rc.conf and makepkg will look familiar here): simple, close to upstream, plain text
configuration. The differences: CRUX builds
everything from source on your machine, has no systemd (init is SysVinit with BSD-style rc
scripts), and its package tools are a few small programs. Most Arch knowledge about programs
carries straight over; this table is the rest.

## Packages
  pacman -Syu                 krest-update   (git pull, ports -u, then prt-get sysup)
  pacman -Sy                  sudo ports -u                (new ports; nothing rebuilt)
  pacman -S foo               sudo prt-get depinst foo     (built here, with its dependencies)
  pacman -Rns foo             sudo prt-get remove foo      (dependencies stay: remove them too)
  pacman -Ss word             prt-get search word ; prt-get dsearch word
  pacman -Qi foo / -Si foo    prt-get info foo
  pacman -Ql foo              pkginfo -l foo
  pacman -Qo /path            pkginfo -o path              (a regular expression, no leading /)
  pacman -Q                   pkginfo -i ; prt-get listinst
  pacman -Qu                  prt-get diff
  pacman -Qdt                 prt-get listorphans
  pacman -Sc                  rm what you no longer need from /usr/ports/distfiles, packages
  IgnorePkg in pacman.conf    sudo prt-get lock foo
  downgrade                   sudo pkgadd -u -f /usr/ports/packages/foo#OLD-1.pkg.tar.zst
  makepkg / PKGBUILD          pkgmk / Pkgfile              (see: pkgfiles)
  the AUR                     contrib, or a collection of your own   (see: ports)
  pacman-key                  CRUX's signify keys in /etc/ports; Krest's sha256 files
  pacman -U file.pkg.tar.zst  sudo pkgadd file.pkg.tar.zst ; -u to upgrade
  .pacnew files               sudo rejmerge

## Services and the system
  systemctl enable foo        add foo to SERVICES in /etc/rc.conf
  systemctl disable foo       take it out of SERVICES
  systemctl start/stop foo    sudo /etc/rc.d/foo start / stop
  systemctl restart foo       sudo /etc/rc.d/foo restart
  systemctl status foo        sudo /etc/rc.d/foo status
  systemctl list-units        ls /etc/rc.d ; cat /etc/rc.conf
  journalctl -f               sudo tail -f /var/log/messages
  journalctl -u foo           /var/log/messages, or /var/log/foo.log if it has one
  journalctl -k               sudo dmesg
  systemctl suspend           krest-sleep suspend           (see: sleep)
  systemctl poweroff/reboot   sudo poweroff / sudo reboot
  timedatectl set-timezone    TIMEZONE= in /etc/rc.conf      (see: rc-conf)
  locale.gen / locale-gen     localedef -i en_GB -f UTF-8 en_GB.UTF-8     (see: locale)
  hostnamectl set-hostname    HOSTNAME= in /etc/rc.conf, and /etc/hosts
  vconsole.conf               KEYMAP= and FONT= in /etc/rc.conf
  mkinitcpio -P               dracut (the linux port runs it)  (see: boot)
  /etc/fstab, /etc/default/grub   the same files, the same way
  systemd-timesyncd           chronyd                          (see: time)
  systemd-networkd/resolved   NetworkManager (Krest)
  systemd timers              crond                            (see: time)
  systemd --user services     ~/.config/krest/autostart, run by the session
  logind.conf                 acpid's rules and krest-sleep  (see: sleep)
  arch-chroot                 mount --bind /dev /proc /sys /run, then chroot (learn recovery)

## Things that differ in spirit
- Everything is compiled: an update is hours, not minutes, when Firefox or the kernel change.
- No rollback and no snapshots: keep the old package files, and back up /etc before large
  changes.
- No dependency resolution on removal: prt-get remove takes only what you name.
- Ports are short shell scripts you are expected to read and copy.
- No journal: plain text logs through syslog in /var/log.

See also: prt-get, rc, rc-conf, ports ; krest-handbook ;
the Arch Wiki's package-manager table: https://wiki.archlinux.org/title/Pacman/Rosetta

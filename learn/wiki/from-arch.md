# From Arch to Void

Void and Arch are both rolling, simple and close to upstream. They differ in the init system
(runit, not systemd), the package manager (XBPS, not pacman) and in leaving out what systemd
would otherwise provide. Most Arch knowledge carries straight over; this table is the rest.

## Packages
  pacman -Syu                 sudo xbps-install -Su
  pacman -S foo               sudo xbps-install foo
  pacman -Rns foo             sudo xbps-remove -R foo
  pacman -Ss word             xbps-query -Rs word
  pacman -Qi foo / -Si foo    xbps-query foo / xbps-query -R foo
  pacman -Ql foo              xbps-query -f foo
  pacman -Qo /path            xbps-query -o /path (installed) ; xlocate /path (any package)
  pacman -Qdt ; -Rns $(...)   sudo xbps-remove -o            (orphans)
  pacman -Qe                  xbps-query -m                  (installed on purpose)
  pacman -Sc                  sudo xbps-remove -O            (old packages in the cache)
  IgnorePkg in pacman.conf    ignorepkg=foo in /etc/xbps.d/*.conf ; or xbps-pkgdb -m hold foo
  downgrade (AUR)             xdowngrade /var/cache/xbps/foo-1.2_1.x86_64.xbps
  makepkg / PKGBUILD          xbps-src / template            (see: xbps-src)
  the AUR                     no equivalent: templates you write or adopt (Pustota's srcpkgs/)
  pacman-key                  keys in /var/db/xbps/keys, imported on first use

## Services and the system
  systemctl enable --now foo  sudo ln -s /etc/sv/foo /var/service/
  systemctl disable --now foo sudo rm /var/service/foo
  systemctl start/stop foo    sudo sv up foo / sudo sv down foo
  systemctl restart foo       sudo sv restart foo
  systemctl status foo        sudo sv status foo
  systemctl list-units        sudo sv status /var/service/*
  journalctl -f               sudo tail -f /var/log/socklog/everything/current
  journalctl -k               dmesg
  systemctl suspend           loginctl suspend               (elogind)
  systemctl poweroff/reboot   loginctl poweroff / reboot ; or poweroff / reboot
  timedatectl set-timezone    sudo ln -sf /usr/share/zoneinfo/Europe/London /etc/localtime
  localectl / locale.gen      /etc/default/libc-locales then xbps-reconfigure -f glibc-locales
  hostnamectl set-hostname    echo NAME | sudo tee /etc/hostname
  mkinitcpio -P               sudo xbps-reconfigure -f linux-mainline   (runs dracut)
  systemd-timesyncd           chronyd (a runit service)
  systemd-networkd/resolved   NetworkManager (Pustota), or dhcpcd / wpa_supplicant / iwd
  systemd timers, cron        none installed: cronie, fcron or snooze   (see: time)
  systemd --user services     a runsvdir for your user              (see: runit)
  /etc/systemd/logind.conf    /etc/elogind/logind.conf and logind.conf.d/
  arch-chroot                 xchroot (xtools)
  genfstab -U                 xgenfstab -U (xtools)

## Things that differ in spirit
- No unit files: a service is a folder with a shell script that runs the program in the
  foreground. Read /etc/sv/*/run; most are three lines.
- No journal: logging is plain text through syslog (socklog), per facility.
- Partial upgrades are as unsupported as on Arch. When XBPS itself has an update,
  xbps-install -Su updates XBPS first and asks you to run it again.
- Package names: -devel instead of nothing (headers are split out, as in Debian), and kernels are
  versioned packages (linux6.18, linux7.3); see kernel.
- Void has a glibc and a musl edition. Pustota is glibc (x86_64).

See also: xbps, runit, the Void Handbook (https://docs.voidlinux.org/xbps/), and the Arch Wiki's
table of package-manager commands, which has an XBPS column:
https://wiki.archlinux.org/title/Pacman/Rosetta

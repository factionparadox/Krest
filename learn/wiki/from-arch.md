# From Arch to Guix

Arch and Guix are both rolling and close to upstream, but Guix works differently underneath:
packages live in a read-only store, the system is one declaration you rebuild rather than a set
of files you edit, every change is a generation you can go back to, and the init is Shepherd,
not systemd. Most Arch knowledge about programs carries straight over; this table is the rest.

## Packages
  pacman -Syu                 rassvet-update   (guix pull, then sudo guix system reconfigure)
  pacman -Sy                  guix pull                    (new package definitions)
  pacman -S foo               guix install foo             (for you; no sudo)
                              or add it to the system's packages (see: system)
  pacman -Rns foo             guix remove foo              (then guix gc frees the space)
  pacman -Ss word             guix search word
  pacman -Qi foo / -Si foo    guix show foo
  pacman -Ql foo              ls -R $(guix build foo)      (its store folder)
  pacman -Qo /path            readlink -f /path names the store item ; guix locate FILE
  pacman -Q / -Qe             guix package -I              (what you installed)
  pacman -Qdt ; -Rns $(...)   guix gc                      (unused store items)
  pacman -Sc                  guix gc -d 1m                (old generations, then collect)
  IgnorePkg in pacman.conf    pin a version: guix install foo@1.2, or a manifest, or
                              guix time-machine for an older Guix
  downgrade (AUR)             guix package --roll-back ; sudo guix system roll-back
  makepkg / PKGBUILD          guix build -L DIR / a package definition (see: guix-packaging)
  the AUR                     channels: Nonguix, or your own (see: channels)
  pacman-key                  channel introductions; substitute keys in /etc/guix/acl
  pacman -U file.pkg.tar.zst  guix archive --import < file.nar

## Services and the system
  systemctl enable --now foo  add (service foo-service-type) to the declaration, reconfigure
  systemctl disable foo       remove it from the declaration, reconfigure
  systemctl start/stop foo    sudo herd start foo / sudo herd stop foo
  systemctl restart foo       sudo herd restart foo
  systemctl status foo        sudo herd status foo
  systemctl list-units        sudo herd status
  journalctl -f               sudo tail -f /var/log/messages
  journalctl -u foo           sudo herd status foo (recent messages) ; /var/log/foo.log
  journalctl -k               sudo dmesg
  systemctl suspend           loginctl suspend               (elogind)
  systemctl poweroff/reboot   loginctl poweroff / reboot ; or sudo shutdown / sudo reboot
  timedatectl set-timezone    #:timezone in /etc/config.scm, reconfigure
  localectl / locale.gen      #:locale (and locale-definitions), reconfigure
  hostnamectl set-hostname    #:host-name in /etc/config.scm, reconfigure
  mkinitcpio -P               nothing: each generation builds its own initrd
  /etc/fstab                  the file-systems field              (see: filesystems)
  /etc/default/grub           the bootloader and kernel-arguments fields   (see: boot)
  systemd-timesyncd           ntpd (ntp-service-type)
  systemd-networkd/resolved   NetworkManager (Rassvet)
  systemd timers, cron        mcron jobs in the declaration     (see: time)
  systemd --user services     Guix Home's Shepherd               (see: shepherd)
  /etc/systemd/logind.conf    elogind-configuration in the declaration   (see: elogind)
  arch-chroot                 mount --rbind, chroot, start guix-daemon   (learn recovery)
  genfstab -U                 nothing: the installer wrote UUIDs into /etc/config.scm

## Things that differ in spirit
- No editing /etc: most of it is generated from the declaration and replaced at reconfigure.
  The one file to edit is /etc/config.scm.
- No partial-upgrade problem: each package refers to the exact store items it was built with,
  so installing one new program cannot break another.
- Updates can be undone whole: the previous system generation is in the GRUB menu.
- Users install software without root, into their own profile; guix shell tries a program
  without installing it.
- No journal: plain text logs through syslog in /var/log.
- Guix proper takes only free software; Nonguix provides the full kernel, firmware, Firefox
  and Steam.

See also: guix-packages, shepherd, system, channels ; info "(guix) Getting Started" ;
the Arch Wiki's package-manager table: https://wiki.archlinux.org/title/Pacman/Rosetta

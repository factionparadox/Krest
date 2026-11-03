# Shepherd: services

GNU Shepherd is Guix System's init (process 1) and service manager, written in Guile Scheme like
Guix. You do not enable or disable services by hand: each one is declared in the operating
system (system.scm, plus anything you add in /etc/config.scm), and guix system reconfigure
works out what Shepherd should run. Removing a service from the declaration removes it from the
next generation; rolling back brings it back.

    sudo herd status                  every service: started, stopped, failing
    sudo herd status NetworkManager   one, with its process and recent messages
    sudo herd restart NetworkManager  also: start, stop
    sudo herd doc rassvet-tutor       what a service is for

herd talks to the running Shepherd; changes made with it last until the next boot or
reconfigure. Reconfigure starts new services, but does not restart running ones that changed:
sudo herd restart NAME, or a reboot, picks up their new version.

## Rassvet's services
dbus (messages between programs) · elogind (sessions, suspend, lid) · NetworkManager and
wpa-supplicant (Wi-Fi) · bluetooth · ntpd (clock) · nftables (firewall) · tlp (battery
tuning) · thermald (heat) · zram (compressed swap in RAM) · earlyoom (stops a runaway program
before memory runs out) · mcron (scheduled jobs: the weekly TRIM) · guix-daemon (builds and
downloads for guix) · udev · the system log · the text consoles, tty1 being ly ·
rassvet-tutor (once the model is downloaded).
Some pieces are not Shepherd services: polkit, upower, udisks and fprintd start when D-Bus asks
for them; slock is a setuid program; gnome-keyring is a PAM module and a program the session
starts.

References: info shepherd ; info "(guix) Services" ; man herd ; rassvet-learn wiki shepherd

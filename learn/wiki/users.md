# Users, groups and sudo

## Accounts are declared
The operating system's users field lists every account; Guix creates them at activation and
writes /etc/passwd and /etc/group from it. Rassvet declares one user, the #:user from
/etc/config.scm, plus Guix's base accounts (root, nobody, the guixbuild users). Passwords are
the stateful part: Guix keeps the hashes already in /etc/shadow (the installer put yours there),
and you change them with passwd as usual.
  passwd ; sudo passwd root         change a password
  id ; groups                       who you are, your groups
Accounts made with useradd do not survive the next reconfigure. To add one, in /etc/config.scm
(see: system):
  (users (cons (user-account (name "anna") (group "users") (home-directory "/home/anna")
                             (supplementary-groups '("audio" "video")))
               (operating-system-users base)))
then reconfigure and give it a password with sudo passwd anna.

## What the groups are for
  wheel       may use sudo
  netdev      network devices (Guix's group for NetworkManager and Wi-Fi control)
  audio       access to sound devices (PipeWire works through your session anyway)
  video       access to video devices (the GPU, the webcam)
  input       input devices: /dev/input/event* (some tools read keyboards directly)
  lp          printers
  kvm         run virtual machines with KVM
  users       the ordinary users' group
The installer's account has all of these (system.scm's supplementary-groups).

## sudo
  sudo COMMAND                 run as root (asks your password, then remembers it a while)
  sudo -i                      a root shell (exit to leave)
/etc/sudoers is generated (the sudoers-file field; Guix's default lets wheel run anything), so
visudo and /etc/sudoers.d are not the way: change the field in the declaration. The root
password is yours, for recovery from a console.

## PAM
PAM (Pluggable Authentication Modules) decides how a program checks who you are. On Guix,
/etc/pam.d is generated too: each service type adds its entries. Rassvet adds:
  ly and ly-autologin          the login screen (autologin: pam_permit, no password asked;
                               the rest as a normal login)
  screen-locker-service-type   slock: a PAM entry and a setuid slock, so it can check your
                               password
  gnome-keyring-service-type   unlocks the keyring at login
fprintd-service-type runs the fingerprint service (fprintd-enroll adds a finger, fprintd-verify
tests it), but system.scm adds no fingerprint line to sudo's PAM entry, so sudo asks for the
password.

See also: elogind (polkit), system ; info "(guix) User Accounts" ; info "(guix) operating-system Reference" ;
man sudo ; man pam.d

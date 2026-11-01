# Users, groups and sudo

## Accounts
  sudo useradd -m -G wheel,audio,video NAME     a new user with a home folder
  sudo passwd NAME                              set the password
  sudo usermod -aG GROUP NAME                   add to a group (log out and in to take effect)
  sudo userdel -r NAME                          remove, with the home folder
  id ; groups                                   who you are, your groups
Accounts are lines in /etc/passwd, passwords (hashed) in /etc/shadow, groups in /etc/group.

## What the groups are for
  wheel       may use sudo (Pustota's rule: /etc/sudoers.d/10-pustota-wheel)
  audio       access to sound devices (PipeWire works through your session anyway)
  video       access to video devices (the GPU)
  input       input devices: /dev/input/event* (some tools read keyboards directly)
  network     change NetworkManager connections without a password (Void's polkit rule)
  bluetooth   use Bluetooth without root
  storage     access to removable storage devices
  disk        raw access to whole disks: powerful, so not given by default
  socklog     read the system logs in /var/log/socklog (see: logging)
  kvm         run virtual machines with KVM
  users       the ordinary users' group
The installer gives your account wheel, audio, video, input, network, bluetooth, storage,
socklog and users (those that exist). The Void Handbook's "Users and Groups" page has the full
table of Void's groups.

## sudo
  sudo COMMAND                 run as root (asks your password, then remembers it 5 minutes)
  sudo -i                      a root shell (exit to leave)
  sudo visudo -f /etc/sudoers.d/NAME     add rules safely (visudo checks the syntax)
Never edit /etc/sudoers itself: an update to sudo may replace it; files in /etc/sudoers.d
are yours. Pustota also sets the root password to yours, for recovery from a console.

doas (package opendoas) is a smaller alternative from OpenBSD, configured in /etc/doas.conf.

## PAM
PAM (Pluggable Authentication Modules) decides how a program checks who you are. Each program
has a file in /etc/pam.d. Pustota's installer adds one line to /etc/pam.d/sudo:

  auth      sufficient pam_fprintd.so

which tries the fingerprint reader first: with a finger enrolled (fprintd-enroll, or the menu:
System -> Fingerprint) touching the sensor is enough; otherwise, or after 30 seconds, sudo asks
for the password as usual. Lines are read top to bottom; "sufficient" means success here is
enough, failure moves on to the next line.

See also: elogind (polkit), logging ; man useradd ; man usermod ; man sudoers ; man pam.d ;
https://docs.voidlinux.org/config/users-and-groups.html

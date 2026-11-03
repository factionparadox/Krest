# Users, groups and sudo

## Accounts
Accounts are the ordinary files: /etc/passwd, /etc/group and /etc/shadow, changed with the
ordinary tools. The installer made yours with
  useradd -m -U -G wheel,audio,video,input,users -s /bin/bash YOU
and set your password and root's to the one you gave (hashed with SHA-512).
  passwd ; sudo passwd root         change a password
  id ; groups                       who you are, your groups
  sudo useradd -m -U -G audio,video,input,users -s /bin/bash anna ; sudo passwd anna
                                    another account (add wheel for sudo)
  sudo usermod -aG GROUP YOU        join a group (log in again for it to count)
New accounts get their home from /etc/skel; Rassvet's desktop files are in
/usr/share/rassvet/skel:  sudo cp -rn /usr/share/rassvet/skel/. /home/anna/ ; then chown -R.

## What the groups are for
  wheel       may use sudo
  audio       access to sound devices
  video       access to video devices (the GPU, the webcam, the backlight)
  input       input devices: /dev/input/event* (some tools read keyboards directly)
  users       the ordinary users' group
With no logind handing devices to the person at the keyboard, these groups are how you reach
the hardware.

## sudo
  sudo COMMAND                 run as root (asks your password, then remembers it a while)
  sudo -i                      a root shell (exit to leave)
  sudo visudo -f /etc/sudoers.d/NAME     a rule of your own, checked before it is saved
/etc/sudoers.d/rassvet:
  %wheel ALL=(ALL:ALL) ALL
  %wheel ALL=(root) NOPASSWD: /usr/bin/rassvet-sleep, /sbin/reboot, /sbin/poweroff
so sleeping, restarting and powering off need no password (the menu, Super+z and acpid's
rassvet-sleep rely on it). The root password is yours, for recovery from a console.

## PAM
PAM (Pluggable Authentication Modules) decides how a program checks who you are; its files
are /etc/pam.d/NAME, one per program. The ones that matter here:
  ly                the login screen (with automatic login, ly logs you in without asking)
  login, su, sudo   CRUX's own
  slock             is setuid root and checks your password itself, through /etc/shadow
dumb_runtime_dir in the session entries makes /run/user/UID at login (see: sound).
There is no fingerprint login: fprintd is not included.

See also: sleep, rc-conf ; man useradd ; man usermod ; man sudo ; man sudoers ; man pam.d

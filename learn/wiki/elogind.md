# elogind

elogind is systemd's login manager (logind) taken out of systemd so it can run on its own. It
tracks who is logged in where (sessions and seats), gives the person at the keyboard access to
the screen, sound and input devices, and handles suspend, hibernate, the lid and the power
button. On Guix it is elogind-service-type, a Shepherd service that needs D-Bus.

## What it does for you
- Sessions: logging in through ly creates a session; elogind makes /run/user/UID (your
  XDG_RUNTIME_DIR, where PipeWire and D-Bus put their sockets) and removes it when you leave.
- Device access: the active session's user gets access to the GPU, input and sound devices,
  so Xorg can run without root.
- Power: loginctl suspend / hibernate / poweroff work for the user at the keyboard, through
  polkit, without sudo.
- Events: the lid, the power button and long idle are handled by elogind, by its settings.

## Commands
  loginctl                          sessions now
  loginctl session-status           yours, in detail
  loginctl suspend ; hibernate ; suspend-then-hibernate ; poweroff ; reboot
  loginctl lock-session             asks the session's locker to lock (Rassvet: xss-lock, slock)

## Settings
There are no logind.conf files to edit: Guix writes elogind's configuration from the
elogind-configuration record. Rassvet's, in system.scm:
  handle-lid-switch                 suspend-then-hibernate if there is swap, else suspend
  handle-lid-switch-external-power  suspend (on the charger the lid only suspends)
  handle-power-key                  suspend
  hibernate-delay-seconds           7200: after two hours asleep it hibernates (the battery
                                    then drains not at all)
Other fields: handle-lid-switch-docked, idle-action and idle-action-seconds, the suspend and
hibernate modes (info "(guix) Desktop Services" lists them all). Change them in /etc/config.scm
with modify-services (see: system), then reconfigure; a restart of elogind can end your session,
so reboot rather than sudo herd restart elogind.

## Hibernation
Hibernation writes memory to swap and powers off; the next boot reads it back. It needs:
- a swap partition at least as big as the memory in use (Rassvet makes it the size of the RAM);
- resume=UUID=... on the kernel command line (system.scm adds it when #:swap-uuid is set);
- Secure Boot off (the kernel refuses hibernation under lockdown).
Guix's initrd resumes by itself when resume= is there. Test: loginctl hibernate. If it comes back
to a fresh boot instead, check  cat /proc/cmdline  for resume= and
sudo dmesg | grep -i -e resume -e hibernat.

## polkit
polkit decides which unprivileged requests (suspend, mounting a USB stick, changing Wi-Fi)
are allowed. Rules come from the packages that extend polkit-service-type (elogind,
NetworkManager, udisks ...) and are gathered into the store; pkaction lists every action.
New rules are added in the declaration (polkit-service-type extensions), not in /etc.

See also: shepherd, users, boot ; man loginctl ; info "(guix) Desktop Services" ;
man polkit

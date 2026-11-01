# elogind

elogind is systemd's login manager (logind) taken out of systemd so it can run on its own. It
tracks who is logged in where (sessions and seats), gives the person at the keyboard access to
the screen, sound and input devices, and handles suspend, hibernate, the lid and the power
button. On Void it is a runit service and needs D-Bus.

## What it does for you
- Sessions: logging in on tty1 creates a session; elogind makes /run/user/UID (your
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
  loginctl lock-session             asks the session's locker to lock (Pustota: xss-lock, slock)

## Settings
  /etc/elogind/logind.conf          the defaults, commented
  /etc/elogind/logind.conf.d/*.conf your changes (Pustota's are here)
  /etc/elogind/sleep.conf.d/*.conf  how suspend and hibernate are done

Pustota sets:
  logind.conf.d/50-pustota.conf      HandleLidSwitch=suspend, HandlePowerKey=suspend
  logind.conf.d/60-pustota-hibernate.conf   (written by the installer when there is swap)
                                     HandleLidSwitch=suspend-then-hibernate: the lid suspends ...
  sleep.conf.d/60-pustota-hibernate.conf
                                     HibernateDelaySec=2h: ... and after two hours asleep,
                                     hibernates (the battery then drains not at all)
Files are read in order of their names, so 60- overrides 50-.

Other useful keys in logind.conf: HandlePowerKey= (poweroff, suspend, ignore ...),
HandleLidSwitchExternalPower= (what the lid does on the charger), IdleAction= and IdleActionSec=.
After a change: sudo sv restart elogind (this can end your session: save work first, or reboot).

## Hibernation
Hibernation writes memory to swap and powers off; the next boot reads it back. It needs:
- a swap partition at least as big as the memory in use (Pustota makes it the size of the RAM);
- resume=UUID=... on the kernel command line (the installer adds it to /etc/default/grub);
- the resume module in the initramfs (Pustota's /etc/dracut.conf.d adds it);
- Secure Boot off (the kernel refuses hibernation under lockdown).
Test: loginctl hibernate. If it comes back to a fresh boot instead, check  cat /proc/cmdline
for resume= and  dmesg | grep -i -e resume -e hibernat.

## polkit
polkit decides which unprivileged requests (suspend, mounting a USB stick, changing Wi-Fi)
are allowed. Rules live in /usr/share/polkit-1/rules.d (from packages) and
/etc/polkit-1/rules.d (yours). Void's NetworkManager, for instance, ships a rule that lets
members of the network group change connections. pkaction lists every action.

See also: runit, users, boot ; man loginctl ; man logind.conf ; man sleep.conf ;
man polkit ; https://docs.voidlinux.org/config/session-management.html ;
https://docs.voidlinux.org/config/power-management.html

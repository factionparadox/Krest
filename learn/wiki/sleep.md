# Sleep, hibernation and the lid

CRUX has no session manager: no systemd-logind and no elogind. Nothing watches the lid or the
power button for you, and there is no loginctl suspend. Rassvet does it with three plain
pieces: acpid catches the events, rassvet-sleep acts on them, and sudo lets your session call
it without a password.

## acpid
/etc/rc.d/acpid, in SERVICES. acpid reads the kernel's ACPI events and runs the action of
every rule in /etc/acpi/events whose event= matches. Rassvet's port installs two:
  /etc/acpi/events/lid      event=button/lid.*close    action=/usr/bin/rassvet-sleep lid
  /etc/acpi/events/power    event=button/power.*       action=/usr/bin/rassvet-sleep power
  acpi_listen               watch the events as they happen (close the lid, press a key)
Add a rule of your own (for the charger, say: event=ac_adapter.*), then
sudo /etc/rc.d/acpid restart.

## rassvet-sleep
A short script, run as root (acpid runs it so; from your session it calls itself through
sudo, which /etc/sudoers.d/rassvet allows without a password):
  rassvet-sleep suspend      lock the screen, then echo mem > /sys/power/state
  rassvet-sleep hibernate    lock, then echo disk > /sys/power/state
  rassvet-sleep power        the power button: suspend
  rassvet-sleep lid          the lid closed: if it is still closed, lock and suspend; on
                             battery, with hibernation possible, suspend with an RTC alarm
                             two hours ahead (rtcwake), and if the alarm is what woke it,
                             hibernate
Locking: for every X display it runs  xset s activate  as the display's owner, which makes
xss-lock start slock. Super+z, the power menu and rassvet-battery (at 4 %) use the same
script. The two hours are HOURS= at the top of /usr/bin/rassvet-sleep; an update of
rassvet-desktop replaces that file, so keep a note of any change you make there.

## Hibernation
Hibernation writes memory to swap and powers off; the next boot reads it back. It needs:
- a swap partition at least as big as the memory in use (the installer made it the size of
  the RAM; on a small disk there is none);
- resume=UUID=... on the kernel command line (the installer added it to /etc/default/grub);
- the initramfs, whose dracut resume module reads the image back;
- Secure Boot off (the kernel refuses hibernation under lockdown).
rassvet-sleep checks the first two (grep resume= /proc/cmdline, a partition in /proc/swaps)
and refuses to hibernate without them. Test: rassvet-sleep hibernate. If it comes back to a
fresh boot instead, check  cat /proc/cmdline  and  sudo dmesg | grep -i -e resume -e hibernat.

## Suspend modes
  cat /sys/power/mem_sleep          [s2idle] is normal on this laptop (S0ix)
  rassvet-sleepcheck                suspends for a minute and reports the time in S0ix
                                    (see: framework)

## What logind would also have done
- XDG_RUNTIME_DIR (/run/user/UID): the dumb_runtime_dir PAM module makes it at login.
- Device access for X: Xorg runs as root through its setuid wrapper; sound, video and input
  devices are reached through the audio, video and input groups.
- polkit: it still answers D-Bus requests (udisks, NetworkManager), but with no logind to
  say which session is active, rules meant for "the user at the keyboard" may not apply;
  sudo covers the rest.
- Idle actions: xset's screen saver and DPMS times (rassvet-session and rassvet-battery).

See also: power (rassvet-learn learn power), boot, users ; man acpid ; man rtcwake ;
https://docs.kernel.org/admin-guide/pm/sleep-states.html

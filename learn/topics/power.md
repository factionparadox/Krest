# Battery, heat, sleep and hibernation

Pustota keeps the laptop idle as much as possible: ratpoison and polybar barely use the CPU,
no compositor redraws the screen, and services are few. Then:
- tlp tunes the hardware for battery when unplugged (/etc/tlp.d/50-pustota.conf: the CPU's
  energy policy and platform profile go to power-saving; Wi-Fi power saving on).
- thermald keeps the CPU cool without fans racing.
- zram swaps into compressed RAM before touching the disk; earlyoom stops a runaway program.
- the screen blanks after 10 minutes and turns off later (xset in pustota-session).

## Sleep
Closing the lid suspends (elogind). If the installer made a swap partition the size of the
RAM, the lid uses suspend-then-hibernate: after two hours asleep the laptop hibernates, writing
memory to disk and switching off completely, so a forgotten laptop does not drain flat. The
battery watcher (pustota-battery) warns at 15 % and 7 % and hibernates at 4 %.
Settings: /etc/elogind/logind.conf.d/ and /etc/elogind/sleep.conf.d/.

    loginctl suspend ; loginctl hibernate      (Super+z suspends; Super+Escape is the power menu)

## Measure, don't guess
    sudo powertop                    watts used and what uses them
    sudo tlp-stat -b ; tlp-stat -s   battery health; tlp's state
    cat /sys/class/power_supply/BAT1/capacity
    cat /sys/firmware/acpi/platform_profile

Avoid running a second power manager (power-profiles-daemon, auto-cpufreq) beside tlp: they
fight over the same settings.

References: https://docs.voidlinux.org/config/power-management.html ; man tlp ; man logind.conf

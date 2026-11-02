# Battery, heat, sleep and hibernation

Pustota keeps the laptop idle as much as possible: ratpoison and polybar barely use the CPU,
no compositor redraws the screen, and services are few. Then:
- tlp tunes the hardware for battery when unplugged (/etc/tlp.d/50-pustota.conf: the CPU's
  energy policy and platform profile go to power-saving; Wi-Fi power saving on).
- thermald keeps the CPU cool without fans racing.
- zram swaps into compressed RAM before touching the disk; earlyoom stops a runaway program.
- on battery the screen runs at 60 Hz instead of 120 and blanks after 5 minutes instead of 10
  (pustota-battery switches both when you plug in or unplug).
- video is decoded by the GPU, not the processor: mpv (/etc/mpv/mpv.conf: hwdec=auto-safe)
  and Firefox (VA-API, /usr/lib/firefox/browser/defaults/preferences/pustota.js).
- Wi-Fi power saving stays on: NetworkManager would otherwise reset what tlp sets
  (/etc/NetworkManager/conf.d/50-pustota-wifi-powersave.conf).
- the SSD uses less power (nvme.noacpi=1 on the kernel command line) and is trimmed weekly.
- Ollama, the tutor's engine, unloads the model after a minute idle (OLLAMA_KEEP_ALIVE=1m).

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

## More, if you want it (each one costs something)
  CPU_BOOST_ON_BAT=0 in /etc/tlp.d/60-mine.conf   no turbo on battery: cooler and longer-
                                   lasting, but noticeably slower (the AI tutor especially)
  DEVICES_TO_DISABLE_ON_BAT_NOT_IN_USE="bluetooth"   Bluetooth off on battery when nothing is
                                   connected (turn it on again in bluetuith to pair)
  a dimmer screen                  the screen is the largest single draw: brightness keys
  a charge limit (framework_tool --charge-limit 80)   not more runtime, but a longer-lived
                                   battery for a laptop that lives on the charger
After a tlp change: sudo tlp start. Then measure with powertop rather than trusting a list.

Left out on purpose: Intel's low-power daemon for these chips (intel-lpmd) needs systemd to
move work between core types, and Void has none; tlp and the kernel's own scheduling cover it.

Avoid running a second power manager (power-profiles-daemon, auto-cpufreq) beside tlp: they
fight over the same settings.

References: https://docs.voidlinux.org/config/power-management.html ; man tlp ; man logind.conf

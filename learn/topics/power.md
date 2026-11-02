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
- intel_lpmd, Intel's Energy Optimizer, moves light work (typing, a video, an idle desktop) onto
  the four low-power cores and lets the big ones sleep; heavy work brings them back.
- Firefox installs uBlock Origin on first start (/usr/lib/firefox/distribution/policies.json):
  adverts and trackers are much of what keeps the processor busy on the web.

## Sleep
Closing the lid suspends (elogind). If the installer made a swap partition the size of the
RAM, the lid uses suspend-then-hibernate: after two hours asleep the laptop hibernates, writing
memory to disk and switching off completely, so a forgotten laptop does not drain flat. The
battery watcher (pustota-battery) warns at 15 % and 7 % and hibernates at 4 %.
Settings: /etc/elogind/logind.conf.d/ and /etc/elogind/sleep.conf.d/.

    loginctl suspend ; loginctl hibernate      (Super+z suspends; Super+Escape is the power menu)
    pustota-sleepcheck                          is that sleep the deep kind? (below)

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

## intel_lpmd
Intel's Energy Optimizer (release 0.1.0, the one that added Panther Lake), packaged by Pustota
(srcpkgs/intel-lpmd) because Void has no package. Of its three ways of confining work, one asks
systemd; Pustota uses "cgroup v2 isolate", which writes /sys/fs/cgroup itself (Void mounts
cgroup v2 there by default). When the load is light it isolates the other cores, so everything
runs on the low-power ones; above 95 % load it lets them all back.
    sudo sv status intel_lpmd ; sudo tail /var/log/socklog/daemon/current
    cat /sys/fs/cgroup/lpm/cpuset.cpus      the cores set aside while it is in low-power mode
    sudo intel_lpmd_control OFF ; ... AUTO  pause it ; let it decide again
    sudo rm /var/service/intel_lpmd         switch it off for good, if it causes trouble
Settings: /etc/intel_lpmd/intel_lpmd_config_F6_M204.xml (then sudo sv restart intel_lpmd).

## Is sleep really asleep?
    pustota-sleepcheck               suspends for a minute, then says how much of it the chip
                                     spent in its deepest state (S0ix). Near 100 % is right;
                                     near 0 % means something keeps it awake all night
Also in the menu: System -> Sleep check.

## Switch off what you do not use (menu: System)
    the touchscreen                  sudo framework_tool --touchscreen-enable false
    the keyboard light               sudo framework_tool --kblight 0
    expansion cards                  on earlier Framework 13s HDMI and DisplayPort cards drew a
                                     little power with nothing plugged in; take out one you rarely
                                     use and compare in powertop

Avoid running a second power manager (power-profiles-daemon, auto-cpufreq) beside tlp: they
fight over the same settings.

References: https://docs.voidlinux.org/config/power-management.html ; man tlp ; man logind.conf

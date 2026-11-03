# Battery, heat, sleep and hibernation

Rassvet keeps the laptop idle as much as possible: ratpoison and polybar barely use the CPU,
no compositor redraws the screen, and services are few. Then, all declared in system.scm:
- tlp tunes the hardware for battery when unplugged: the CPU's energy policy goes to "power"
  and the platform profile to "low-power" (on the charger: balance_performance and balanced);
  Wi-Fi power saving on battery.
- thermald keeps the CPU cool without fans racing.
- zram: 16 GB of compressed swap in RAM (zstd), used before the disk; earlyoom stops a
  runaway program before memory runs out.
- on battery the screen runs at 60 Hz instead of 120 and blanks after 5 minutes instead of 10
  (rassvet-battery switches both when you plug in or unplug).
- video is decoded by the GPU, not the processor: mpv (~/.config/mpv/mpv.conf: hwdec=auto-safe)
  and Firefox (VA-API, switched on in /etc/firefox/policies/policies.json).
- Wi-Fi power saving stays on: NetworkManager would otherwise reset what tlp sets
  (/etc/NetworkManager/conf.d/50-rassvet-wifi-powersave.conf).
- the SSD uses less power (nvme.noacpi=1 on the kernel command line) and is trimmed weekly.
- Firefox offers uBlock Origin on first start (the same policies file): adverts and trackers
  are much of what keeps the processor busy on the web.
- the tutor (llama-server) uses no processor while idle, but keeps its model in memory while
  it runs: sudo herd stop rassvet-tutor frees it until the next boot.

## Sleep
Closing the lid suspends (elogind). If the installer made a swap partition the size of the
RAM, the lid uses suspend-then-hibernate: after two hours asleep the laptop hibernates, writing
memory to disk and switching off completely, so a forgotten laptop does not drain flat. On the
charger the lid only suspends; the power key suspends too. The battery watcher (rassvet-battery)
warns at 15 % and 7 % and hibernates at 4 %. These are elogind-configuration fields in system.scm.

    loginctl suspend ; loginctl hibernate      (Super+z suspends; Super+Escape is the power menu)
    rassvet-sleepcheck                          is that sleep the deep kind? (below)

## Measure, don't guess
    sudo powertop                    watts used and what uses them
    sudo tlp-stat -b ; sudo tlp-stat -s   battery health; tlp's state
    cat /sys/class/power_supply/BAT1/capacity
    cat /sys/firmware/acpi/platform_profile

## More, if you want it (each one costs something)
tlp's settings are fields of tlp-configuration; change them by wrapping the system in
/etc/config.scm (rassvet-learn wiki system has the pattern), for example
    (tlp-service-type config => (tlp-configuration (inherit config) (cpu-boost-on-bat? #f)))
  cpu-boost-on-bat? #f             no turbo on battery: cooler and longer-lasting, but
                                   noticeably slower (the AI tutor especially)
  a dimmer screen                  the screen is the largest single draw: brightness keys
Then sudo guix system reconfigure /etc/config.scm, and measure with powertop rather than
trusting a list. Avoid a second power manager (power-profiles-daemon, auto-cpufreq) beside tlp:
they fight over the same settings.

## Is sleep really asleep?
    rassvet-sleepcheck               suspends for a minute, then says how much of it the chip
                                     spent in its deepest state (S0ix). Near 100 % is right;
                                     near 0 % means something keeps it awake all night
Also in the menu: System -> Sleep check.

## Not here
framework_tool (touchscreen off, keyboard light, charge limit) is not packaged for Guix, and
neither is intel_lpmd, Intel's low-power daemon. Expansion cards you rarely use can simply come
out: compare in powertop.

References: info "(guix) Power Management Services" ; man tlp ; man loginctl

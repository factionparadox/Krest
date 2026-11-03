# Framework Laptop 13 Pro (Intel Core Ultra Series 3)

The laptop Krest is built for: Framework's 2026 redesign of the 13, with Intel's Core Ultra
Series 3 ("Panther Lake") processors.

## This one
  Processor   Core Ultra 5 325: 8 cores (4 performance, 4 low-power efficient), 8 threads,
              up to 4.5 GHz; Intel graphics with 4 Xe cores; an NPU (not used by Krest)
  Memory      LPCAMM2 LPDDR5X, 6800 MT/s on the Ultra 5 325 (32 GB here)
  Display     13.5", 2880x1920 (3:2, 256 ppi), 30-120 Hz, touch
  Wi-Fi       Intel Wi-Fi 7 BE211 (PCI 8086:e440), driver iwlwifi; Bluetooth on the same card
  Graphics    PCI 8086:b082 (Xe3), kernel driver xe
  Battery     74 Wh
  Touchpad    haptic (no moving parts; the click is a vibration)
Check yours: lscpu ; lspci -nn

## What it needs, and what Krest sets
  a new kernel      Panther Lake needs a recent one (Framework recommends the newest): the
                    linux port, 7.3.1, built here (see: kernel)
  firmware          linux-firmware, and the CPU microcode (intel-ucode) through dracut's
                    --early-microcode (see: firmware)
  framework_tool    the embedded controller: charge limit, keyboard light, touchscreen,
                    the haptic click force, firmware versions (see: firmware)
  -march=native     everything is compiled for this processor (/etc/pkgmk.conf)

From nixos-hardware's module for this board (framework/13-inch/intel-core-ultra-series3,
which includes the common Framework 13 and Intel settings), Krest also sets:
  nvme.noacpi=1     kernel argument: lower SSD power use, also while suspended
                    (check: cat /proc/cmdline)
  blacklist cros_usbpd_charger   its USB-C charger driver would wake the laptop
                    (/etc/modprobe.d/krest-framework.conf, from krest-desktop)
  TLP               battery tuning (nixos-hardware uses TLP too unless another tuner is on)

Tools for this laptop (menu: System):
  krest-sleepcheck    does sleep reach S0ix? (suspends for a minute)
Krest's own battery settings for this panel and chip (krest-learn learn power): 60 Hz on
battery (120 on the charger), earlier screen blanking, GPU video decoding in mpv and Firefox,
Wi-Fi power saving kept on.

## Not on Krest
  fprintd           the fingerprint reader: not included, so there is no fingerprint login
                    or sudo (the menu's fingerprint entry stays hidden)
  fwupd             firmware updates from the LVFS (see: firmware)
  intel_lpmd        Intel's low-power daemon for these hybrid chips: not included
  iio-sensor-proxy  the ambient light sensor; only GNOME and KDE use it for automatic
                    brightness, and ratpoison has nothing to read it
  framework-laptop-kmod   a community kernel module exposing the EC in /sys; not included
  speaker tuning    nixos-hardware's equaliser preset is for the classic 13's speakers; it says
                    the 13 Pro needs different tuning, and none is published yet
  weekly TRIM       not scheduled (see: filesystems)
  Secure Boot       must stay off: the kernel and GRUB are not signed, and hibernation needs it off

## Known issues (community reports, autumn 2026)
- The haptic touchpad has been reported, rarely, not to come back after sleep. Reloading its
  driver may bring it back (untested on Krest):
      sudo modprobe -r hid_multitouch && sudo modprobe hid_multitouch
  If it happens often, report it on the Framework community forum with your BIOS version.
- If the battery drops a lot overnight, run krest-sleepcheck: under 80 % in S0ix means a
  device or driver keeps the chip awake; unplug expansion cards one at a time to find it.
- Text size: Krest uses 144 dpi (150%). Framework's own guides suggest 200% for this panel;
  for larger text set  Xft.dpi: 192  in ~/.Xresources and log in again (see: graphics).

## Updating the firmware
sudo fwupdtool refresh ; sudo fwupdtool get-updates  (the System menu's "Firmware updates")
lists what the LVFS has for this laptop. Framework also publishes BIOS updates with their own
instructions in their knowledge base; check the result with  sudo framework_tool --versions.

See also: firmware, kernel, graphics, filesystems, sleep (hibernation) ;
https://github.com/NixOS/nixos-hardware/tree/master/framework/13-inch/intel-core-ultra-series3 ;
https://github.com/FrameworkComputer/linux-docs ; https://frame.work/laptop13pro ;
https://community.frame.work/

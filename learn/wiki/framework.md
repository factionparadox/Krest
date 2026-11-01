# Framework Laptop 13 Pro (Intel Core Ultra Series 3)

The laptop Pustota is built for: Framework's 2026 redesign of the 13, with Intel's Core Ultra
Series 3 ("Panther Lake") processors.

## This one
  Processor   Core Ultra 5 325: 8 cores (4 performance, 4 low-power efficient), 8 threads,
              up to 4.5 GHz; Intel graphics with 4 Xe cores; an NPU (not used by Pustota)
  Memory      LPCAMM2 LPDDR5X, 6800 MT/s on the Ultra 5 325 (32 GB here)
  Display     13.5", 2880x1920 (3:2, 256 ppi), 30-120 Hz, touch
  Wi-Fi       Intel Wi-Fi 7 BE211 (PCI 8086:e440), driver iwlwifi; Bluetooth on the same card
  Graphics    PCI 8086:b082 (Xe3), kernel driver xe
  Battery     74 Wh
  Touchpad    haptic (no moving parts; the click is a vibration)
Check yours: lscpu ; lspci -nn ; sudo framework_tool --versions

## What it needs, and what Pustota sets
  Linux 7.x         Panther Lake needs a new kernel (Framework recommends the newest; 7.1
                    to 7.3 each brought speed-ups). linux-mainline (see: kernel)
  firmware          linux-firmware-intel (Wi-Fi, Bluetooth, graphics), sof-firmware (audio),
                    intel-ucode from nonfree (see: firmware)
  fwupd             BIOS and embedded-controller updates; Framework publishes them on the LVFS
  fprintd           the fingerprint reader, for sudo (see: users)
  framework_tool    the embedded controller: battery, charge limit, firmware versions

From nixos-hardware's module for this board (framework/13-inch/intel-core-ultra-series3,
which includes the common Framework 13 and Intel settings), Pustota also sets:
  nvme.noacpi=1     kernel option: lower SSD power use, also while suspended. The installer
                    adds it to /etc/default/grub (check: cat /proc/cmdline)
  weekly TRIM       /etc/cron.weekly/fstrim, run by the snooze-weekly service (see: time)
  blacklist cros_usbpd_charger   unused by Framework's EC; it only logs an error at boot
                    (/etc/modprobe.d/pustota-framework.conf)
  Ethernet card     the Expansion Card (Realtek 0bda:8156) suspends when idle
                    (/etc/udev/rules.d/50-pustota-framework.rules)
  TLP               battery tuning (nixos-hardware uses TLP too unless another tuner is on)

## Deliberately left out
  iio-sensor-proxy  the ambient light sensor; only GNOME and KDE use it for automatic
                    brightness, and ratpoison has nothing to read it
  framework-laptop-kmod   a community kernel module exposing the EC in /sys (charge limit, LEDs);
                    not packaged for Void. framework_tool does the same jobs from the command line
  speaker tuning    nixos-hardware's equaliser preset is for the classic 13's speakers; it says
                    the 13 Pro needs different tuning, and none is published yet
  Secure Boot       must stay off: Void's kernels are not signed, and hibernation needs it off

## Known issues (community reports, autumn 2026)
- The haptic touchpad has been reported, rarely, not to come back after sleep. Reloading its
  driver may bring it back (untested on Pustota):
      sudo modprobe -r hid_multitouch && sudo modprobe hid_multitouch
  If it happens often, report it on the Framework community forum with your BIOS version.
- Text size: Pustota uses 144 dpi (150%). Framework's own guides suggest 200% for this panel;
  for larger text set  Xft.dpi: 192  in ~/.Xresources and log in again (see: graphics).

## Updating the firmware
    fwupdmgr refresh ; fwupdmgr get-updates ; fwupdmgr update
On the charger, with Secure Boot off as usual. Framework's release notes for this board are on
the LVFS (device work.frame.Laptop.PTL.BIOS.firmware) and in their knowledge base.

See also: firmware, kernel, graphics, filesystems, elogind (hibernation) ;
https://github.com/NixOS/nixos-hardware/tree/master/framework/13-inch/intel-core-ultra-series3 ;
https://github.com/FrameworkComputer/linux-docs ; https://frame.work/laptop13pro ;
https://community.frame.work/

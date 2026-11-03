# Firmware and microcode

## Device firmware: linux-firmware
Many devices load a firmware file from the disk when their driver starts. Guix's own kernel
and channel carry none of these files (they are not free software), so Rassvet takes them from
Nonguix: system.scm's firmware field is (list linux-firmware), the whole collection: Intel
graphics, Wi-Fi (iwlwifi), Bluetooth and the rest. A missing file shows in dmesg:
  sudo dmesg | grep -i firmware      ("failed to load" names the file)
Nonguix also has smaller and separate firmware packages (sof-firmware for Intel's audio DSP,
among others); if a device asks for a file linux-firmware lacks, add that package to the
firmware field (see: system) and reconfigure.

## CPU microcode
Intel's corrections to the processor itself, loaded at every boot before anything else (they
do not change the chip permanently). Nonguix's microcode-initrd puts them at the front of the
initrd; a new version comes with an update, used from the next boot.
  dmesg | grep -i microcode        "microcode updated early to revision ..."

## The laptop's own firmware: fwupd
fwupd updates firmware in the laptop itself (BIOS/UEFI, the embedded controller, docks)
through the LVFS, where Framework publishes its releases. Rassvet runs no fwupd daemon, so use
fwupdtool, which works without one (it needs root):
  sudo fwupdtool refresh           fetch the list of releases
  sudo fwupdtool get-updates       what applies to this laptop
  sudo fwupdtool update            install (usually on the next reboot; keep it on the charger)
  sudo fwupdtool get-devices       what fwupd can see
Also in the menu: System -> Firmware updates. Framework's own notes on which BIOS versions
are on the LVFS: https://knowledgebase.frame.work/

## framework_tool
Framework's framework_tool (from framework-system) talks to the embedded controller: battery
and charger, charge limit, keyboard light, firmware versions. It is not packaged for Guix, so
Rassvet's menu hides its entries. Its source and releases:
https://github.com/FrameworkComputer/framework-system

See also: boot (microcode in the initrd), channels (Nonguix), graphics ;
man fwupdtool ; https://gitlab.com/nonguix/nonguix ; https://fwupd.org/

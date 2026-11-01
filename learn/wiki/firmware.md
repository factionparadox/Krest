# Firmware and microcode

## Device firmware: linux-firmware
Many devices load a firmware file from the disk when their driver starts. Void splits
linux-firmware so you install only what you need; Pustota installs
  linux-firmware-intel     Intel graphics, Wi-Fi (iwlwifi) and Bluetooth
  linux-firmware-network   other network cards (USB dongles, docks)
  sof-firmware             Intel's audio DSP (the Framework's speakers and microphones)
Files are in /usr/lib/firmware. A missing one shows in dmesg: dmesg | grep -i firmware
("failed to load" names the file; xlocate NAME finds the package that has it).

## CPU microcode: intel-ucode
Intel's corrections to the processor itself, loaded at every boot before anything else (they
do not change the chip permanently). intel-ucode is in the nonfree repository, which Pustota
enables (void-repo-nonfree). It updates with everything else; the new microcode is used from
the next boot.
  dmesg | grep -i microcode        "microcode updated early to revision ..."

## The laptop's own firmware: fwupd
fwupd updates firmware in the laptop itself (BIOS/UEFI, the embedded controller, docks)
through the LVFS, where Framework publishes its releases.
  fwupdmgr refresh                 fetch the list of releases
  fwupdmgr get-updates             what applies to this laptop
  fwupdmgr update                  install (usually on the next reboot; keep it on the charger)
Also in the menu: System -> Firmware updates. Framework's own notes on which BIOS versions
are on the LVFS: https://knowledgebase.frame.work/

## framework_tool
framework-system's framework_tool talks to the Framework's embedded controller:
  sudo framework_tool --power                 battery and charger
  sudo framework_tool --charge-limit 80       stop charging at 80% (kinder to the battery if it
                                              lives on the charger)
  sudo framework_tool --versions              firmware versions
framework_tool --help lists the rest.

See also: boot (microcode in the initramfs), repositories (nonfree), graphics ;
man fwupdmgr ; https://docs.voidlinux.org/config/firmware.html ;
https://github.com/FrameworkComputer/framework-system

# Firmware and microcode

## Device firmware: linux-firmware
Many devices load a firmware file from the disk when their driver starts: Intel graphics,
Wi-Fi (iwlwifi), Bluetooth, the audio DSP and more. The linux-firmware package has the whole
collection in /lib/firmware; the stick installed it ready-built with the kernel, so the Wi-Fi
works on the first boot. A missing file shows in dmesg:
  sudo dmesg | grep -i firmware      ("failed to load" names the file)
  pkginfo -o lib/firmware/iwlwifi    which package has a file
A newer linux-firmware arrives with rassvet-update like any port; it is used from the next
boot (or the next time the driver loads).

## CPU microcode
Intel's corrections to the processor itself, loaded at every boot before anything else (they
do not change the chip permanently). The intel-ucode package holds them; dracut's
--early-microcode puts them at the front of the initramfs. A new version needs the initramfs
remade (the linux port does it whenever the kernel is rebuilt; by hand, see: boot).
  dmesg | grep -i microcode        "microcode updated early to revision ..."

## The laptop's own firmware
fwupd (from contrib) reads the LVFS, where Framework publishes BIOS updates: the System menu's
"Firmware updates" runs  sudo fwupdtool refresh ; sudo fwupdtool get-updates. Framework also
publishes them as files with their own instructions:  https://knowledgebase.frame.work/

## framework_tool
Framework's own tool (from framework-system; Rassvet's framework-tool port installs Framework's
release build) talks to the embedded controller. It needs root:
  sudo framework_tool --versions              BIOS, EC and other firmware versions
  sudo framework_tool --power                 battery and charger
  sudo framework_tool --charge-limit 80       stop charging at 80 %
  sudo framework_tool --kblight 50            keyboard light
  sudo framework_tool --touchscreen-enable false
  sudo framework_tool --click-force high      the haptic touchpad's click
The menu's System list has the keyboard light, touchscreen and click force.
framework_tool --help lists the rest.

See also: boot (microcode in the initramfs), kernel, framework, graphics ;
https://github.com/FrameworkComputer/framework-system

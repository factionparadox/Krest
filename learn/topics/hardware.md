# The Framework Laptop 13 Pro

Intel Core Ultra series 3 (Panther Lake), LPCAMM2 memory, NVMe storage, an Intel Wi-Fi 7 card,
Intel audio DSP with SoundWire, and expansion cards (USB-C devices underneath).

What Rassvet does for it (all in system.scm):
- Nonguix's linux, the full kernel with every driver (Guix's own linux-libre leaves out the
  ones that need firmware), and linux-firmware (Wi-Fi, Bluetooth, graphics and the rest).
- Intel's CPU microcode, loaded first by Nonguix's microcode-initrd.
- Graphics through the modesetting driver without tearing, the touchpad (tap to click, natural
  scrolling, no clicks while typing): both in the X configuration ly starts. Mesa for 3D and
  Vulkan, intel-media-driver-nonfree for video decoding (LIBVA_DRIVER_NAME=iHD).
- The dense screen: 144 dpi (Xft.dpi in /etc/rassvet/Xresources; try 120 or 168 in ~/.Xresources).
- fwupd for BIOS and device firmware:  sudo fwupdtool refresh ; sudo fwupdtool get-updates
framework_tool (touchscreen, keyboard light, charge limit) is not packaged for Guix, so the
menu hides those entries.

## Look
    lspci -k ; lsusb                  devices and their drivers
    sudo dmesg | less                 kernel messages since boot
    vainfo                            video decoding
    cat /sys/class/backlight/*/brightness

Secure Boot must be off: the kernel and GRUB are not signed for it.

References: https://knowledgebase.frame.work/ ; rassvet-learn wiki framework

# The Framework Laptop 13 Pro

Intel Core Ultra series 3 (Panther Lake), LPCAMM2 memory, NVMe storage, an Intel Wi-Fi 7 card,
Intel audio DSP with SoundWire, and expansion cards (USB-C devices underneath).

What Pustota does for it:
- Linux 7.x (linux-mainline): the graphics (xe/i915), audio and power drivers arrive there.
- Firmware: linux-firmware-intel and -network (Wi-Fi, Bluetooth, graphics), sof-firmware
  (audio), intel-ucode (CPU fixes).
- Graphics through the modesetting driver without tearing (/etc/X11/xorg.conf.d/20-intel.conf),
  Mesa for 3D and Vulkan, intel-media-driver for video decoding (LIBVA_DRIVER_NAME=iHD).
- The touchpad: tap to click, natural scrolling, no clicks while typing (30-touchpad.conf).
- The dense screen: 144 dpi (Xft.dpi in /etc/pustota/Xresources: try 120 or 168).
- fwupd for BIOS and device firmware:  fwupdmgr refresh ; fwupdmgr get-updates

## Look
    lspci -k ; lsusb                  devices and their drivers
    sudo dmesg | less                 kernel messages since boot
    vainfo                            video decoding
    cat /sys/class/backlight/*/brightness

Secure Boot must be off: the kernel and GRUB are not signed for it.

References: https://knowledgebase.frame.work/ ; https://docs.voidlinux.org/config/graphical-session/graphics-drivers/intel.html

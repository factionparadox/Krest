# The Framework Laptop 13 Pro

Intel Core Ultra series 3 (Panther Lake), LPCAMM2 memory, NVMe storage, an Intel Wi-Fi 7 card,
Intel audio DSP with SoundWire, and expansion cards (USB-C devices underneath).

What Rassvet does for it:
- The `linux` port: kernel 7.3.1, built here from Arch Linux's laptop configuration plus
  Rassvet's few changes (ports/linux/rassvet.config), and linux-firmware (Wi-Fi, Bluetooth,
  graphics, the audio DSP and the rest).
- Intel's CPU microcode (intel-ucode), loaded first by dracut's --early-microcode.
- Graphics through the modesetting driver without tearing, the touchpad (tap to click, natural
  scrolling, no clicks while typing): both in /etc/X11/xorg.conf.d/30-rassvet.conf. Mesa for
  3D and Vulkan, intel-media-driver for video decoding (LIBVA_DRIVER_NAME=iHD).
- The dense screen: 144 dpi (Xft.dpi in /etc/rassvet/Xresources; try 120 or 168 in ~/.Xresources).
- framework_tool, Framework's own tool for the embedded controller: touchscreen off, keyboard
  light, touchpad click force, charge limit (menu: System).
The fingerprint reader is not used: fprintd is not included.

## Look
    lspci -k ; lsusb                  devices and their drivers
    sudo dmesg | less                 kernel messages since boot
    sudo framework_tool --versions    BIOS and embedded-controller versions
    cat /sys/class/backlight/*/brightness

Secure Boot must be off: the kernel and GRUB are not signed for it.

References: https://knowledgebase.frame.work/ ; rassvet-learn wiki framework

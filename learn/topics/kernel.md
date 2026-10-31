# The kernel: why linux-mainline

The Framework 13 Pro (Intel Core Ultra series 3, Panther Lake) needs Linux 7.x: older kernels
lack its graphics, audio and power drivers. Void's default kernel package "linux" follows a
long-term series (6.18 as of October 2026). "linux-mainline" follows Void's newest series
instead, so Pustota installs that, and keeps "linux" out with one line in
/etc/xbps.d/10-pustota-kernel.conf:   ignorepkg=linux

When Void packages a new series (7.4 ...), linux-mainline moves to it on the next update. The
old kernel stays installed until you remove it, and GRUB lists both: choose the older one under
"Advanced options" if a new one misbehaves.

## Look
    uname -r                          the running kernel (a newly installed one runs after a reboot)
    xbps-query -x linux-mainline      which series it points at
    xbps-query -s '^linux[0-9]'       installed kernels
    lsmod ; dmesg | less ; lspci -k   drivers, messages, which driver runs each device

## Tidy old kernels (once the new one works)
    sudo vkpurge list ; sudo vkpurge rm 7.2.9_1

Firmware (Wi-Fi, audio DSP, graphics microcode) is in linux-firmware-intel,
linux-firmware-network and sof-firmware; CPU microcode in intel-ucode.

References: https://docs.voidlinux.org/config/kernel.html ; man vkpurge ; https://docs.kernel.org/

# The kernel: Nonguix's linux

The Framework 13 Pro (Intel Core Ultra series 3, Panther Lake) needs a new kernel: older ones
lack its graphics, audio and power drivers. Guix's own kernel, linux-libre, removes every
driver that loads non-free firmware, which includes this laptop's Wi-Fi. Rassvet uses Nonguix's
"linux" instead: the same newest stable kernel series, unmodified, with linux-firmware and
Intel's microcode beside it. All three are named in system.scm (kernel, firmware, initrd).

When Nonguix moves linux to a new series, the next rassvet-update builds a generation with it.
The previous generation keeps its own kernel: GRUB's "GNU system, old configurations..." menu
boots it if the new one misbehaves, and sudo guix system roll-back makes it the default again.

## Look
    uname -r                          the running kernel (a new one runs after a reboot)
    guix show linux                   the version the channels now offer
    guix system list-generations      each generation's kernel
    lsmod ; sudo dmesg | less ; lspci -k   drivers, messages, which driver runs each device

## Old kernels
They are in the store as long as a generation uses them. Once a new one works:
    sudo guix system delete-generations 1m   generations older than a month
    sudo guix gc                             then free their space

References: info "(guix) operating-system Reference" ; https://gitlab.com/nonguix/nonguix ;
https://docs.kernel.org/

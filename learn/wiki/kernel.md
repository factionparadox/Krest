# Kernel

## Which kernel
Guix's own kernel is linux-libre: Linux with every driver that needs non-free firmware taken
out, and that includes this laptop's Wi-Fi. Rassvet's system.scm uses Nonguix instead:
  (kernel linux)               Nonguix's linux: the newest stable series, unmodified
  (firmware (list linux-firmware))
  (initrd microcode-initrd)    Guix's initrd with Intel's microcode in front
Nonguix also packages long-term series (linux-lts and versioned ones such as linux-6.12); a
different kernel is one field in /etc/config.scm (see: system).

  uname -r                              the running kernel
  guix show linux                       the version your guix would install now
  ls -l /run/current-system/kernel      the running generation's kernel, in the store

## Updates and old kernels
A kernel update arrives with rassvet-update like everything else: the new generation has the
new kernel, and runs it after a reboot. Every older generation keeps the kernel it was built
with, so GRUB's "old configurations" menu is also the list of older kernels. They stay on the
disk as long as a generation uses them:
  guix system list-generations           each generation (and its kernel)
  sudo guix system delete-generations 1m  drop the old ones once the new kernel has done well
  sudo guix gc                            free their space
Kernel builds are large: Nonguix's substitute server provides them, so a kernel update is a
download, not an hour of compiling.

## Modules
  lsmod                           loaded modules
  modinfo iwlwifi                 what a module is, its options
  sudo modprobe NAME              load one now
udev loads drivers for the hardware it finds. In the declaration:
  kernel-loadable-modules         extra (out-of-tree) modules, built for this kernel
  kernel-module-loader-service-type   modules to load at every boot
  kernel-arguments                options at boot: "snd_hda_intel.power_save=1",
                                  "modprobe.blacklist=pcspkr"
  initrd-modules                  what the initrd loads to reach the root
Rassvet blacklists cros_usbpd_charger in /etc/modprobe.d/rassvet-framework.conf, a file
system.scm writes (see: framework).

## Out-of-tree modules
Guix has no DKMS: a module from outside the kernel is a package built against the kernel
package, listed in kernel-loadable-modules; reconfigure builds it for each new kernel. Guix
and Nonguix package some (v4l2loopback-linux-module, for example); guix search module finds them.

## Kernel messages
  sudo dmesg ; sudo dmesg -w ; sudo dmesg --level=err,warn

See also: boot, firmware ; info "(guix) operating-system Reference" ;
info "(guix) Linux Services" ; https://gitlab.com/nonguix/nonguix ; https://docs.kernel.org/

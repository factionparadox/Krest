# Kernel

## Kernel packages
Void packages each kernel series separately, so several can be installed side by side:

  linux6.18, linux7.3 ...     a kernel series (the actual kernel, its modules)
  linux                       a meta package that follows Void's default series (older, stable)
  linux-mainline              a meta package that follows Void's newest series. Pustota uses it:
                              Panther Lake (the Framework 13 Pro) needs Linux 7.
  linux-lts                   follows the long-term series
  linuxN.M-headers            headers for building modules (DKMS); the meta packages have
                              matching -headers ones (linux-mainline-headers)

Pustota puts ignorepkg=linux and ignorepkg=linux-headers in /etc/xbps.d/10-pustota-kernel.conf
so the default series is never pulled back in as a dependency.

  uname -r                              the running kernel
  xbps-query -l | grep '^ii linux'      the installed ones

## Updates and old kernels
A kernel update installs the new series or version beside the old one; the old one stays in
GRUB's "Advanced options" until you remove it. vkpurge (from base-files, so always
installed) does that:

  vkpurge list                    kernels you could remove (never the running one)
  sudo vkpurge rm 7.2.4_1         one
  sudo vkpurge rm all             all but the running one: do it after a reboot into the new
                                  kernel has gone well

## Modules
  lsmod                           loaded modules
  modinfo iwlwifi                 what a module is, its options
  sudo modprobe NAME              load one now
  /etc/modules-load.d/*.conf      modules to load at every boot (one name per line); runit's
                                  stage 1 loads them
  /etc/modprobe.d/*.conf          options and blacklists:
                                    options snd_hda_intel power_save=1
                                    blacklist pcspkr
If a module is in the initramfs (graphics, storage), rebuild it after changing its options:
sudo xbps-reconfigure -f linux-mainline.

## DKMS
Modules from outside the kernel (for example, some VPN or VirtualBox modules) are built by
DKMS for each kernel. Install dkms and the -headers package for your kernel
(linux-mainline-headers); Void's kernel hooks then build them whenever a kernel is installed.

## Kernel messages
  dmesg ; dmesg -w ; dmesg --level=err,warn

See also: boot, firmware ; man modprobe.d ; man vkpurge ;
https://docs.voidlinux.org/config/kernel.html

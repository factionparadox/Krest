# Kernel

## Which kernel
CRUX expects you to build your own kernel. Krest's is a port, so prt-get builds and updates
it like any other: ports/linux in the repository.
  source       kernel.org's linux-7.3.1.tar.xz, base.config and krest.config
  base.config  Arch Linux's configuration for the same series: every driver a laptop may
               need, mostly as modules
  krest.config  Krest's changes, merged on top (scripts/kconfig/merge_config.sh, then
               make olddefconfig): LOCALVERSION -krest; no debug information, no BTF, no
               Rust; modules not signed; NVMe, VMD, XFS and VFAT built in; SELinux off,
               LSMs landlock, lockdown, yama, integrity
  build        make bzImage modules, with every core
  installs     /boot/vmlinuz-7.3.1-krest, System.map-7.3.1-krest, config-7.3.1-krest,
               /lib/modules/7.3.1-krest
  post-install dracut --early-microcode for /boot/initramfs-7.3.1-krest.img, then
               grub-mkconfig
The ISO's installer runs the same kernel, built ahead on the build machine.

  uname -r                              the running kernel
  prt-get info linux                    the version the port offers now
  less /boot/config-$(uname -r)         its full configuration

## Updates and old kernels
A new version of the port arrives with krest-update; prt-get sysup builds it, pkgadd -u
replaces the old kernel's files with the new one's, and post-install remakes the initramfs and
menu. Restart to run it. The previous kernel is gone from /boot and /lib/modules (its old
initramfs file stays until you delete it); its package file is still in /usr/ports/packages:
  sudo pkgadd -u -f /usr/ports/packages/linux#7.3.1-1.pkg.tar.zst
then the dracut and grub-mkconfig lines from post-install by hand (see: boot), and
sudo prt-get lock linux until the problem is solved. There is no "old kernels" menu in GRUB.

## Your own configuration
Copy the port to a collection of your own (see: pkgfiles), change krest.config there (one
CONFIG_ line per change; make menuconfig in an unpacked tree helps you find the names), run
sudo pkgmk -um in it and sudo prt-get update linux. Keep LOCALVERSION, or change the -krest
in post-install and the Pkgfile's install lines to match.

## Modules
  lsmod                           loaded modules
  modinfo iwlwifi                 what a module is, its options
  sudo modprobe NAME              load one now
udev loads drivers for the hardware it finds. Options and blacklists go in /etc/modprobe.d
(Krest blacklists cros_usbpd_charger in krest-framework.conf: see: framework); modules
to load at every boot go in /etc/rc.modules.

## Out-of-tree modules
There is no DKMS: a module from outside the kernel is a port that builds against
/lib/modules/$(uname -r)/build. Krest's linux port removes that link to save space, so such a
port needs your own kernel port that keeps the build tree.

## Kernel messages
  sudo dmesg ; sudo dmesg -w ; sudo dmesg --level=err,warn

See also: boot, firmware ; krest-handbook (the kernel chapter) ; https://docs.kernel.org/

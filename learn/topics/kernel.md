# The kernel: built here, from the `linux` port

The Framework 13 Pro (Intel Core Ultra series 3, Panther Lake) needs a new kernel: older ones
lack its graphics, audio and power drivers. CRUX builds its kernel from source like everything
else, and Rassvet's collection has its own `linux` port: kernel.org's 7.3.1, configured with
Arch Linux's configuration (base.config, everything a laptop may need) merged with
rassvet.config: no debug information, no Rust, unsigned modules, NVMe and XFS built in, the
version suffix -rassvet. It is built on this laptop with -march=native and all cores.

Installing it puts /boot/vmlinuz-7.3.1-rassvet, System.map and config there and the modules in
/lib/modules/7.3.1-rassvet; its post-install script runs dracut (the initramfs, microcode
first) and grub-mkconfig. When the port moves to a new version, rassvet-update rebuilds it with
everything else; restart to run it.

## Look
    uname -r                          the running kernel (a new one runs after a reboot)
    prt-get info linux                the version the port offers now
    less /boot/config-$(uname -r)     its configuration
    lsmod ; sudo dmesg | less ; lspci -k   drivers, messages, which driver runs each device

## Old kernels
There is no menu of older kernels: an upgrade replaces the old kernel and its modules. Its
package is still in /usr/ports/packages; to put it back (from a console, or the Rassvet stick:
learn recovery), pkgadd it and do the post-install script's two steps by hand:
    ls /usr/ports/packages/linux#*
    sudo pkgadd -u -f /usr/ports/packages/linux#7.3.1-1.pkg.tar.zst
    sudo dracut --force --early-microcode --kver 7.3.1-rassvet /boot/initramfs-7.3.1-rassvet.img
    sudo grub-mkconfig -o /boot/grub/grub.cfg
    sudo prt-get lock linux           keep sysup from rebuilding it (prt-get unlock linux later)

References: man dracut ; https://docs.kernel.org/ ; rassvet-learn wiki kernel (your own config)

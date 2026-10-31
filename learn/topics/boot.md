# Booting: UEFI, GRUB, kernel, initramfs

The disk is GPT. Its first partition (1 GiB, FAT32) is the EFI system partition, mounted at
/boot/efi; the firmware reads GRUB from it. GRUB shows the menu (kernels in /boot), loads the
chosen kernel and its initramfs, and passes the kernel line from /etc/default/grub.

The initramfs is a small early system made by dracut. It loads the drivers needed to reach the
root filesystem, checks whether to resume from hibernation (resume=UUID=... on the kernel line),
then mounts / and starts runit. Pustota asks dracut for a host-only initramfs (only this
computer's drivers: smaller and quicker) in /etc/dracut.conf.d/20-pustota.conf.

## Look (read-only)
    cat /proc/cmdline                the kernel line this boot used
    ls /boot                         kernels and initramfs images
    findmnt /boot/efi ; efibootmgr -v
    grep CMDLINE /etc/default/grub

## Change (deliberately)
    sudoedit /etc/default/grub ; sudo grub-mkconfig -o /boot/grub/grub.cfg
    sudo xbps-reconfigure -f linux7.3      rebuild that kernel's initramfs (use your version)
GRUB is installed twice: as "Pustota" in the firmware's boot list, and at the fallback path
EFI/BOOT/BOOTX64.EFI that firmware always tries. Secure Boot must stay off.

References: https://docs.voidlinux.org/config/kernel.html ; man dracut ; man grub-mkconfig

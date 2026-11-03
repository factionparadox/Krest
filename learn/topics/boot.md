# Booting: UEFI, GRUB, kernel, initramfs

The disk is GPT. Its first partition (1 GiB, FAT32) is the EFI system partition, mounted at
/boot/efi; the firmware reads GRUB from it. The installer put GRUB there twice: as "Rassvet" in
the firmware's boot list, and at the fallback path every UEFI firmware tries
(EFI/BOOT/BOOTX64.EFI). GRUB's menu is /boot/grub/grub.cfg, written by grub-mkconfig from
/etc/default/grub and whatever kernels it finds in /boot.

The kernel is the `linux` port, built on this laptop: /boot/vmlinuz-7.3.1-rassvet, its modules
in /lib/modules/7.3.1-rassvet. The initramfs is made by dracut with --early-microcode, so
Intel's microcode (the intel-ucode package) is loaded before anything else. It loads the
drivers needed to reach the root (NVMe and XFS are built into the kernel anyway), resumes from
hibernation if there is an image (resume=UUID=... on the kernel line), mounts / and starts init.

## Look (read-only)
    cat /proc/cmdline                the kernel line this boot used
    ls /boot                         kernel, System.map, config and initramfs
    findmnt /boot/efi ; efibootmgr -v
    grep -v '^#' /etc/default/grub

## Change (deliberately)
Kernel arguments are GRUB_CMDLINE_LINUX_DEFAULT in /etc/default/grub. The installer set
quiet, nvme.noacpi=1 and resume= (when there is swap). After editing it:
    sudo grub-mkconfig -o /boot/grub/grub.cfg
After a new kernel, the `linux` port's post-install script remakes the initramfs and the menu
itself; by hand it is
    sudo dracut --force --early-microcode --kver 7.3.1-rassvet /boot/initramfs-7.3.1-rassvet.img
At the GRUB menu, e edits an entry for this boot only; Ctrl+x boots it. Secure Boot must stay off.

References: man grub-mkconfig ; man dracut ; rassvet-learn wiki boot

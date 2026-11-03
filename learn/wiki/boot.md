# Boot

From power button to desktop, in order:

  1. UEFI firmware      finds the EFI system partition (FAT32, 1 GiB, mounted at /boot/efi)
                        and runs the boot loader named in its boot list ("Rassvet"), or the
                        fallback EFI/BOOT/BOOTX64.EFI
  2. GRUB               shows the menu and loads /boot/vmlinuz-7.3.1-rassvet and
                        /boot/initramfs-7.3.1-rassvet.img, with the kernel command line
  3. kernel + initramfs dracut's initramfs, Intel's microcode first: loads what is needed to
                        reach the root, resumes from hibernation if there is an image,
                        mounts / (XFS) and runs /sbin/init
  4. init               reads /etc/inittab: /etc/rc (filesystems, udev, hostname, keymap,
                        the system log), then /etc/rc.multi starts SERVICES (see: rc)
  5. ly on tty1         inittab runs ly instead of a text login (it logs you in by itself,
                        if you chose that); ly starts X and rassvet-session

## GRUB
grub-install put it in /boot/efi twice (--bootloader-id=Rassvet, and --removable for the
fallback path). Its settings are /etc/default/grub (GRUB_CMDLINE_LINUX_DEFAULT, GRUB_TIMEOUT
and the rest); /boot/grub/grub.cfg is generated from them and from the kernels in
/boot. After a change:
  sudo grub-mkconfig -o /boot/grub/grub.cfg
The linux port's post-install script runs that after every kernel build.
At the menu, e edits an entry for this boot only (remove quiet to see messages, or add an
argument), and Ctrl+x boots it.
  efibootmgr -v                        the firmware's boot list

## The initramfs
dracut builds it: /boot/initramfs-VERSION.img, with --early-microcode, so the intel-ucode
package's microcode is loaded before anything else. The kernel has NVMe and XFS built in
(rassvet.config), so it can even boot without it, but resuming from hibernation needs it.
  sudo dracut --force --early-microcode --kver 7.3.1-rassvet /boot/initramfs-7.3.1-rassvet.img
  lsinitrd /boot/initramfs-7.3.1-rassvet.img | less     what is inside
  dmesg | grep -i microcode            "microcode updated early to revision ..."

## The kernel command line
  cat /proc/cmdline                    what this boot used
The installer set quiet, nvme.noacpi=1 (lower SSD power use) and resume=UUID=... (when there
is a swap partition). Useful at the GRUB prompt:
  rd.break                             stop in the initramfs, before / is switched to
  modprobe.blacklist=NAME              keep a module from loading this once
  init=/bin/sh                         a root shell instead of init (mount -o remount,rw /)

## When it does not boot
There is no older system to pick in GRUB. Boot the Rassvet stick and chroot in
(rassvet-learn learn recovery): put the previous kernel package back, remake the initramfs or
reinstall GRUB.

See also: kernel, sleep (hibernation), rc ; man grub-mkconfig ; man dracut ; man efibootmgr ;
rassvet-handbook

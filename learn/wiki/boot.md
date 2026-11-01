# Boot

From power button to desktop, in order:

  1. UEFI firmware      finds the EFI system partition (FAT, 1 GiB, mounted at /boot/efi) and
                        runs the boot loader named in its boot list, or the fallback
                        EFI/BOOT/BOOTX64.EFI
  2. GRUB               shows the menu, loads the kernel (/boot/vmlinuz-VERSION) and its
                        initramfs (/boot/initramfs-VERSION.img), passes the command line
  3. kernel + initramfs dracut's small early system: loads the drivers needed to reach the
                        root filesystem, resumes from hibernation if there is an image,
                        mounts / (XFS) and hands over
  4. runit              stage 1 (start-up), stage 2 (services, logins) (see: runit)
  5. agetty on tty1     logs you in (automatically, if you chose that); ~/.bash_profile runs
                        startx, which runs pustota-session

## GRUB
  /etc/default/grub                    settings; the kernel command line is
                                       GRUB_CMDLINE_LINUX_DEFAULT="loglevel=4 resume=UUID=..."
  sudo grub-mkconfig -o /boot/grub/grub.cfg    write the menu after changing them
  /boot/grub/grub.cfg                  the generated menu (do not edit by hand)

Void's kernel packages run grub-mkconfig themselves when a kernel is installed or removed
(hooks in /etc/kernel.d), so the menu follows updates without help. "Advanced options" in the
menu lists every installed kernel: the way back if a new one misbehaves.

At the menu, e edits an entry for this boot only (add  single  for rescue mode, or remove
quiet to see messages), and Ctrl+x boots it.

The installer ran grub-install twice: once normally (an entry "Pustota" in the firmware's
boot list, files in /boot/efi/EFI/Pustota/) and once with --removable (EFI/BOOT/BOOTX64.EFI),
which firmware boots even if its boot list is reset.

  efibootmgr -v                        the firmware's boot list

## The initramfs: dracut
dracut builds the initramfs when a kernel is installed (or reconfigured). Its settings:

  /etc/dracut.conf.d/*.conf            Pustota's: hostonly="yes" (only this laptop's drivers:
                                       smaller and faster), the resume module, compression
  sudo xbps-reconfigure -f linux-mainline      rebuild after changing anything
  lsinitrd /boot/initramfs-$(uname -r).img | less     what is inside

## The kernel command line
  cat /proc/cmdline                    what this boot used
Useful additions (in GRUB_CMDLINE_LINUX_DEFAULT, then grub-mkconfig):
  loglevel=3 quiet                     fewer messages while booting
  single                               rescue runlevel (see: runit)
  rd.break                             stop inside the initramfs, before / is mounted

## Microcode
intel-ucode (from the nonfree repository) puts Intel's CPU fixes into the initramfs, loaded
before anything else (dracut's early_microcode). Check: dmesg | grep -i microcode

## When it does not boot
pustota-learn learn recovery: booting the install stick, xchroot and repairing GRUB.

See also: kernel, elogind (hibernation), filesystems ; man grub-mkconfig ; man dracut.conf ;
man efibootmgr ; https://docs.voidlinux.org/config/kernel.html ;
https://docs.voidlinux.org/installation/guides/fde.html (encrypted disks, for a future install)

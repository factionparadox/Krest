# Boot

From power button to desktop, in order:

  1. UEFI firmware      finds the EFI system partition (FAT32, 1 GiB, mounted at /boot/efi)
                        and runs the boot loader named in its boot list
  2. GRUB               shows the menu: the current generation, and every older one under
                        "GNU system, old configurations...". Loads that generation's kernel
                        and initrd straight from /gnu/store and passes its command line
  3. kernel + initrd    Guix's initrd, with Intel's microcode in front: loads the drivers
                        needed to reach the root, resumes from hibernation if there is an
                        image, mounts / (XFS) and starts the system named by gnu.system=
  4. Shepherd           process 1: activates the system (/etc, accounts, setuid programs)
                        and starts the services (see: shepherd)
  5. ly on tty1         agetty hands tty1 to ly, the login screen (it logs you in by itself,
                        if you chose that); ly starts X and rassvet-session

## GRUB
system.scm's bootloader-configuration: grub-efi-bootloader installed to /boot/efi, a 3-second
timeout, Rassvet's keyboard layout, white on red for the highlighted entry. Guix writes
/boot/grub/grub.cfg on every reconfigure (and installs GRUB when needed); do not edit it, it
is overwritten. guix system delete-generations also takes them out of the menu.

At the menu, e edits an entry for this boot only (remove quiet to see messages, or add an
argument), and Ctrl+x boots it.
  efibootmgr -v                        the firmware's boot list

## The initrd
Nonguix's microcode-initrd: Guix's base initrd (a small Guile program with the modules for
NVMe, XFS and the rest) with Intel's (and AMD's) CPU microcode prepended, so it is loaded before
anything else. It is built with each generation; nothing to rebuild by hand. Its modules are the
initrd-modules field of the operating system (Guix's defaults on Rassvet).
  dmesg | grep -i microcode            "microcode updated early to revision ..."

## The kernel command line
  cat /proc/cmdline                    what this boot used
Guix adds --root=, gnu.system= and gnu.load= itself; Rassvet adds nvme.noacpi=1 (lower SSD
power use), resume=UUID=... (when there is a swap partition) and Guix's default, quiet.
To add more, use kernel-arguments in /etc/config.scm (see: system). Useful at the GRUB prompt:
  --repl                               stop in the initrd with a Guile REPL, before / is mounted
  modprobe.blacklist=NAME              keep a module from loading this once

## When it does not boot
Pick an older generation in GRUB's "old configurations" menu; once it is up,
sudo guix system roll-back makes it the default. rassvet-learn learn recovery has the rest
(the install stick, chroot, reinstalling GRUB).

See also: kernel, elogind (hibernation), system ; info "(guix) Bootloader Configuration" ;
info "(guix) Initial RAM Disk" ; man efibootmgr

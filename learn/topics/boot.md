# Booting: UEFI, GRUB, kernel, initrd

The disk is GPT. Its first partition (1 GiB, FAT32) is the EFI system partition, mounted at
/boot/efi; the firmware reads GRUB from it. Guix writes GRUB's menu (/boot/grub/grub.cfg) at
every guix system reconfigure: the newest generation first, every older one under
"GNU system, old configurations...". The kernel and initrd are read straight from /gnu/store,
so each generation boots exactly the kernel it was built with.

The initrd is Guix's own small early system (a Guile program), with Intel's microcode added in
front by Nonguix's microcode-initrd. It loads the drivers needed to reach the root, resumes
from hibernation if there is an image (resume=UUID=... on the kernel line), mounts / and
starts Shepherd.

## Look (read-only)
    cat /proc/cmdline                the kernel line this boot used
    guix system list-generations     what GRUB offers
    findmnt /boot/efi ; efibootmgr -v
    guix system describe             this generation's kernel, root device and channels

## Change (deliberately)
Kernel arguments, the GRUB timeout and the rest are fields of the operating system, not files
in /etc. Rassvet sets nvme.noacpi=1, resume= (when there is swap) and Guix's defaults; to add
one, wrap the system in /etc/config.scm (rassvet-learn wiki system shows how), then
    sudo guix system reconfigure /etc/config.scm
At the GRUB menu, e edits an entry for this boot only; Ctrl+x boots it. Secure Boot must stay off.

References: info "(guix) Bootloader Configuration" ; info "(guix) Initial RAM Disk" ;
rassvet-learn wiki boot

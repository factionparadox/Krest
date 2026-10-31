# Repositories

A repository is a folder of packages plus a signed index for one architecture. Pustota uses
Void's main x86_64 glibc repository (configured by base-system in /usr/share/xbps.d). Void
offers more, each switched on by installing a package:
    sudo xbps-install void-repo-nonfree      software with non-free licences
    sudo xbps-install void-repo-multilib     32-bit libraries (Steam, Wine)
musl and other architectures cannot be mixed into this system.

The first time XBPS meets a repository's signing key it asks you to accept it; Void's own key
is already trusted (it came with the installer). Never switch signature checks off.

Pustota's three packages were installed from the ISO and are not in any online repository yet:
they update when you install from a newer Pustota ISO, or by building the packages yourself
(see: pustota-learn learn building).

Third-party repositories are not checked by Void and can replace official packages: add one
only if you trust who runs it, in a file of your own under /etc/xbps.d.

## Look
    xbps-query -L                    configured repositories and their package counts
    ls /usr/share/xbps.d /etc/xbps.d
    ls /var/db/xbps/keys             trusted signing keys

References: https://docs.voidlinux.org/xbps/repositories/

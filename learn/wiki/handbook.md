# The CRUX handbook, offline

The CRUX handbook is CRUX's official documentation, written by its developers for each
release: installing, configuring the system (rc.conf, the rc scripts, networking), the
package system (pkgutils, ports, prt-get), building a kernel, and writing ports. It is short
enough to read in an evening, and the rest of CRUX assumes you have. It lives online at
https://crux.nu/Main/Handbook3-8 and the CRUX team keeps improving it, so Krest keeps the
newest copy offline in /usr/share/doc/crux/handbook.txt: the installer fetches it once the
desktop is compiled, and krest-update fetches it again each time. The copy from the install
stick stays beside it (handbook-stick.txt), with CRUX 3.8's release notes.

## Reading it
  krest-handbook            the handbook in less (menu -> Learn -> CRUX handbook)
  krest-handbook mc         Midnight Commander with this wiki on one side and the
                              handbook's folder on the other
  krest-handbook notes      CRUX 3.8's release notes
  krest-handbook update     fetch the newest handbook now
  less /usr/share/doc/crux/handbook.txt     the same, in any terminal

less's keys:
  Space / b                   next and previous page
  /word, then n / N           search, next and previous match
  g / G                       the start / the end
  q                           quit

Searching is the quickest way in: /prt-get, /rc.conf, /footprint, /SERVICES ...

## The manual pages
The handbook explains; the manual pages give every option:
  man prt-get ; man prt-get.conf ; man ports ; man pkgmk ; man pkgmk.conf
  man pkgadd ; man pkgrm ; man pkginfo ; man rejmerge
  man init ; man inittab ; man start-stop-daemon

## Online
  https://crux.nu/                         the handbook, the FAQ, the wiki and the mailing lists
  https://crux.nu/portdb/                  every port in every collection, searchable
The CRUX wiki has pages on more than the handbook covers (hibernation, Wi-Fi, specific
hardware), written by its users.

## Where it fits
The handbook says how CRUX is meant to be used; this wiki explains the same system at shorter
length, with Krest's own choices; the lessons (krest-learn learn) are the short tour. When
they disagree, the handbook and the manual pages are right.

See also: index ; man less

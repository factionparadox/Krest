# Ports and collections

## The ports tree
A port is a folder: a Pkgfile (see: pkgfiles), and beside it the checksums (.md5sum, or a
.signature), the expected file list (.footprint) and any small files the build needs (patches,
rc scripts). A collection is a folder of ports under /usr/ports. Everything CRUX knows about
software comes from there, so "updating the package lists" is updating these folders, and
nothing is built until you ask (see: prt-get).

Krest's collections, in the order /etc/prt-get.conf lists them (prtdir lines; when two
collections have the same port, the first wins):
  krest    /usr/ports/krest    Krest's ports, from /usr/src/krest/ports
  core       /usr/ports/core       the base system: glibc, gcc, coreutils, pkgutils, prt-get ...
  opt        /usr/ports/opt        CRUX's optional ports: Firefox, NetworkManager, PipeWire ...
  xorg       /usr/ports/xorg       X11
  contrib    /usr/ports/contrib    maintained by CRUX's users
  compat-32  /usr/ports/compat-32  32-bit libraries
Krest's comes first, so its linux, acpid, tlp, thermald and the rest replace any port of the
same name further down.

## ports(8)
ports fetches CRUX's collections. Each has a file in /etc/ports (NAME.rsync, NAME.httpup or
similar) saying where it comes from; the installer activated the ones shipped as .inactive.
  sudo ports -u                     update every collection
  sudo ports -u opt                 just one
  ports -l                          list the ports in all collections
  ports -d                          installed packages whose port has a different version
CRUX signs its ports: each has a .signature (signify), and pkgmk checks it against the public
keys in /etc/ports before building.

## Krest's collection
Not fetched by ports: krest-update does it from the repository.
  git -C /usr/src/krest pull --ff-only
  sudo sh /usr/src/krest/build/krest-ports sync /usr/src/krest
  sudo sh /usr/src/krest/build/krest-ports verify
sync copies ports/ to /usr/ports/krest (keeping the .footprint and .md5sum files pkgmk wrote
there), packs Krest's own sources (krest-desktop, krest-learn, krest-russian) into
tarballs, and stamps their version from VERSION and their release from the Git history.
verify downloads every source of every port (pkgmk -do) and checks it against the port's
sha256 file; a "-" there means a GitHub archive that could not be pinned, whose hash is
recorded on first download in /var/lib/krest/sources.sha256 and must match ever after.
Then it writes the .md5sum that pkgmk itself checks. A port that fails is named, and the
command stops before anything is built.

## A collection of your own
  sudo mkdir /usr/ports/local         your ports, one folder each
and a  prtdir /usr/ports/local  line in /etc/prt-get.conf: first to override any port, last
to only add new ones. ports -u leaves it alone. This is also how to change one of Krest's
ports without your change being lost at the next sync (see: pkgfiles).

## Offline
The packages themselves are ordinary files: /usr/ports/packages/NAME#VERSION-RELEASE.pkg.tar.zst.
Copy one to another CRUX machine with the same processor and pkgadd installs it; that is how
the stick brought the kernel and NetworkManager.

See also: prt-get, pkgfiles, pkgutils ; man ports ; man prt-get ; krest-handbook

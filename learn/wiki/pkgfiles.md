# Writing a port: Pkgfiles, pkgmk and footprints

A port is a folder whose Pkgfile is a small bash script: comments with the metadata, four
variables and a build() function. pkgmk sources it, downloads source=() into
PKGMK_SOURCE_DIR, unpacks it in $SRC, runs build(), which installs into $PKG, and packs $PKG
into NAME#VERSION-RELEASE.pkg.tar.zst. Every Pkgfile in /usr/ports is an example; prt-get cat
NAME shows one.

## A Pkgfile
  # Description: Greet the world
  # URL: https://www.gnu.org/software/hello/
  # Maintainer: You, you at example dot org
  # Depends on: ncurses

  name=hello
  version=2.12.1
  release=1
  source=(https://ftp.gnu.org/gnu/$name/$name-$version.tar.gz)

  build() {
  	cd $name-$version
  	./configure --prefix=/usr
  	make
  	make DESTDIR=$PKG install
  	rm -rf $PKG/usr/share/info $PKG/usr/share/doc   # CRUX ships man pages, not these
  }

- Depends on: names ports, not package versions; prt-get reads it, pkgmk does not.
- release starts at 1 and goes up when the port changes but the version does not.
- source can name local files beside the Pkgfile (patches, an rc script, a config).
- $CFLAGS and $MAKEFLAGS come from /etc/pkgmk.conf; a port that ignores them is built
  without -march=native.
- Optional files beside it: pre-install and post-install (shell scripts prt-get runs with
  runscripts yes; the linux port's post-install remakes the initramfs and GRUB's menu), and
  README.

## Building
  cd /usr/ports/local/hello
  sudo pkgmk -d                        download and build
  sudo pkgmk -d -i                     and install it (or: sudo prt-get install hello)
The first build of a new port has no .md5sum or .footprint: run  sudo pkgmk -um  to record
the checksums, and pkgmk writes the .footprint itself after the first successful build.

## Footprints
.footprint is the list of every file the package should contain, with its mode and owner
(pkginfo -f shows the same for a built package). After each build pkgmk compares; a
difference is shown as NEW or MISSING lines. MISSING usually means something did not build
(a missing dependency, a changed option); NEW, that the program installs more than before. If
the change is right:  sudo pkgmk -uf.

## Rassvet's ports and their sha256 files
Rassvet's ports live in /usr/src/rassvet/ports and are copied to /usr/ports/rassvet by
rassvet-ports sync (see: ports). Each has a sha256 file, one line per source:
  fa595aad...  linux-7.3.1.tar.xz
  e673d8d2...  rassvet.config
Most hashes are pinned, and always those of the files kept in the port itself; a "-" in
place of the hash means a GitHub archive that could not be pinned when the port was written,
whose hash rassvet-ports records on first download (/var/lib/rassvet/sources.sha256) and holds
it to afterwards. rassvet-ports verify checks every source this way, then writes the .md5sum
pkgmk uses. Rassvet's own three (rassvet-desktop, rassvet-learn, rassvet-russian) are packed
from the repository by sync, which writes their sha256 and stamps @VERSION@ and @RELEASE@.

## Changing one of Rassvet's ports
An edit in /usr/ports/rassvet is overwritten at the next sync, and one in /usr/src/rassvet
must also update the sha256 file and conflicts with rassvet-update's git pull --ff-only.
The simple way is a copy in a collection of your own, listed first in /etc/prt-get.conf:
  sudo mkdir -p /usr/ports/local ; sudo cp -r /usr/ports/rassvet/x-terminal /usr/ports/local/
  (edit it; raise release=)
  cd /usr/ports/local/x-terminal && sudo pkgmk -um
  sudo prt-get update x-terminal
When Rassvet's port moves to a new version, yours still wins until you remove it.

See also: prt-get, pkgutils, ports ; man pkgmk ; man pkgmk.conf ; rassvet-handbook (the
chapter on writing ports)

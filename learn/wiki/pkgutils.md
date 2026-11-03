# pkgutils: pkgadd, pkgrm, pkginfo, pkgmk, rejmerge

pkgutils is CRUX's package layer: a package is a compressed tarball of files laid out from /,
named NAME#VERSION-RELEASE.pkg.tar.zst, and the database is one text file. prt-get uses these
tools; you can use them directly too.

## The database
/var/lib/pkg/db lists every installed package: its name, its version-release, and every file
it owns, one block per package. Nothing else records what is installed. Do not edit it; back
it up if you like (it is small).

## pkginfo: asking
  pkginfo -i                     every installed package and its version
  pkginfo -l foo                 the files of an installed package
  pkginfo -l FILE.pkg.tar.zst    the files inside a package file
  pkginfo -o usr/bin/mpv         which package owns a file (a regular expression, matched
                                 against paths without the leading /)
  pkginfo -f FILE.pkg.tar.zst    its footprint: files with modes and owners (see: pkgfiles)

## pkgadd and pkgrm
  sudo pkgadd FILE.pkg.tar.zst       install (refuses if a file belongs to another package)
  sudo pkgadd -u FILE.pkg.tar.zst    upgrade: replace the installed version
  sudo pkgadd -u -f FILE             force: also take over files another package claims, or
                                     reinstall an older version (the way back after an update)
  sudo pkgadd -r /mnt FILE           into another root (the installer did this)
  sudo pkgrm foo                     remove it and its files (not its dependencies)
pkgadd does not run a port's pre- or post-install script; prt-get does (runscripts yes).

## Configuration files and rejmerge
/etc/pkgadd.conf says which files an upgrade may overwrite. CRUX's rules keep files under /etc
(and some under /var): if the new package brings a different version, pkgadd leaves yours and
puts the new one in /var/lib/pkg/rejected.
  sudo rejmerge                      for each one: keep yours, take the new one, or merge
Run it after a large update (krest-update reminds you).

## pkgmk: building
pkgmk builds the port in the current folder (see: pkgfiles):
  pkgmk -d                           download what is missing, then build
  pkgmk -do                          download only
  pkgmk -d -i ; pkgmk -d -u          build, then install ; build, then upgrade
  pkgmk -um ; pkgmk -uf              update the .md5sum ; update the .footprint
  pkgmk -im ; pkgmk -if              ignore the checksum ; ignore the footprint
  pkgmk -f                           build again even if the package is up to date
  pkgmk -kw                          keep the work folder (/var/tmp/pkgmk-NAME) for a look
  pkgmk -c                           remove the downloaded sources and the package
Its settings are /etc/pkgmk.conf (CFLAGS, MAKEFLAGS, the folders).

## Other tools
  revdep                             programs with missing libraries; it and other helpers
                                     come in the prt-utils port (not installed by Krest)

See also: prt-get, pkgfiles, ports ; man pkgadd ; man pkgrm ; man pkginfo ; man pkgmk ;
man rejmerge ; man pkgadd.conf ; krest-handbook

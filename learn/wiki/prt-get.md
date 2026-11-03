# prt-get

prt-get is CRUX's package manager on top of the ports tree and pkgutils. It reads the
collections listed in /etc/prt-get.conf (in order: krest, core, opt, xorg, contrib,
compat-32; the first that has a port wins), follows the "# Depends on:" lines of the
Pkgfiles, and runs pkgmk and pkgadd for you. It never downloads binaries: every install and
update is a build on this laptop.

## Asking
  prt-get search word                  ports whose name contains word
  prt-get dsearch word                 names and descriptions
  prt-get fsearch FILE                 ports whose footprint has a file (where it is known)
  prt-get info foo                     version, description, dependencies, collection, URL
  prt-get path foo                     the port's folder (which collection wins)
  prt-get cat foo                      its Pkgfile ; prt-get readme foo: its README, if any
  prt-get depends foo ; deptree foo    what it needs (a list; a tree)
  prt-get dependent foo                installed packages that need foo
  prt-get quickdep foo                 the build order, just names (the installer uses it)
  prt-get isinst foo ; listinst        is it installed? everything installed
  prt-get diff                         installed packages whose port has a newer version
  prt-get listorphans                  installed packages nothing else depends on

## Installing and removing
  sudo prt-get depinst foo             build and install foo and every missing dependency
  sudo prt-get install foo             foo only (stops if a dependency is missing)
  sudo prt-get update foo              rebuild and reinstall (pkgadd -u) one package
  sudo prt-get remove foo              pkgrm it; dependencies stay (listorphans finds them)
  sudo prt-get sysup                   update every installed package with a newer port
  sudo prt-get lock foo ; unlock foo   keep sysup from touching foo ; prt-get listlocked
Useful flags: --test (show what would happen), -fr (force a rebuild of the same version),
-im (ignore the checksum), -if (ignore the footprint), --install-scripts (run pre- and
post-install scripts: Krest's prt-get.conf already sets runscripts yes).

## Updating the whole system
krest-update does it: the Krest repository and collection, ports -u, then prt-get sysup.
  krest-update --dry                 stop after prt-get diff: what would be rebuilt
sysup rebuilds in dependency order. A failed build stops at that port; what was built
before it is installed, nothing after. Read /var/log/pkgbuild/NAME.log, fix or wait, and run
it again: it carries on.

## No generations
An update replaces a package; there is no profile to roll back. The package files stay in
/usr/ports/packages (NAME#VERSION-RELEASE.pkg.tar.zst), each until the same name and version
is built again, so going back to the version before is
  sudo pkgadd -u -f /usr/ports/packages/foo#1.2-1.pkg.tar.zst ; sudo prt-get lock foo
A library update can leave programs pointing at a library version that is gone; revdep (in
the prt-utils port) lists them, and prt-get update rebuilds them.

## Build settings and logs
/etc/pkgmk.conf: CFLAGS -O2 -march=native -pipe, MAKEFLAGS -j(all cores), sources in
/usr/ports/distfiles, packages in /usr/ports/packages, work in /var/tmp/pkgmk-NAME, zstd
packages. /etc/prt-get.conf: writelog enabled, one log per port in /var/log/pkgbuild/NAME.log,
kept even on success.

## Errors you may meet
  "Package 'foo' not found"     sudo ports -u first, or the name differs: prt-get search
  footprint mismatch            the build made other files than the port expects: new files
                                (NEW) are usually harmless (-if, or pkgmk -uf to accept);
                                MISSING ones mean a build option or dependency is wrong
  md5sum or signature mismatch  the download changed: check, do not just -im it
  a build fails                 /var/log/pkgbuild/NAME.log ; the work folder is
                                /var/tmp/pkgmk-NAME (pkgmk -kw keeps it)

See also: pkgutils, pkgfiles, ports, from-arch ; man prt-get ; man prt-get.conf ;
krest-handbook

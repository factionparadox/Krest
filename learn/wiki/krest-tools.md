# Krest's own tools

CRUX gives you small, sharp tools (prt-get, pkgmk, pkgadd, pkginfo, ports) and expects you to
remember them. Krest adds a few of its own on top: one page to look the others up, a way to
use Arch's AUR, a way to take back a bad update, fingerprint for sudo, and the commands that
keep the system and its handbook current. They are plain shell scripts in /usr/bin: read
them with  less /usr/bin/NAME  whenever you want to know exactly what one does.

## port-help: every package command on one page
  port-help                       all of them, one line each, in plain English (q quits)
  port-help prt-get               one tool's section; also pkgmk, pkgadd, pkginfo, ports,
                                  port-undo, port-aurum, krest-update

Use it whenever you can't remember which of CRUX's tools does what: prt-get finds, builds and
installs ports; pkgmk builds one by hand; pkgadd and pkgrm install and remove a package file;
pkginfo says what's installed; ports fetches the recipes.

## port-aurum: software from Arch's AUR
The AUR (Arch User Repository) holds recipes, called PKGBUILDs, for software Arch doesn't
package. A PKGBUILD and a CRUX Pkgfile are close cousins: both are short shell scripts with a
name, a version, the sources and the steps to build. port-aurum turns one into the other.

  port-aurum foo                  fetch foo's recipe, show it to you, convert it, check its
                                  downloads, then build and install it (prt-get depinst)
  port-aurum -c foo               convert only, so you can read or edit the port first:
                                  then  sudo prt-get depinst foo

What it does, in order:
  1. Downloads foo's recipe from aur.archlinux.org and shows you its PKGBUILD. Nothing
     happens until you answer y: AUR recipes are written by anyone, and they run as root
     while they are converted and built. Read it first.
  2. Writes a CRUX port to /usr/ports/aur/foo: a Pkgfile whose build() runs the recipe's own
     prepare(), build() and package() steps, with Arch's names for the folders ($srcdir,
     $pkgdir) pointing at pkgmk's ($SRC, $PKG). The PKGBUILD itself sits beside it.
  3. Gives the dependencies CRUX's names: python-foo becomes python3-foo, libx11 becomes
     xorg-libx11, qt5-base becomes qt5, and the ones CRUX doesn't need (glibc, gcc-libs ...)
     are dropped. A dependency that's only on the AUR is converted too, after you've seen its
     recipe. One that's nowhere is listed at the top of the Pkgfile for you to port.
  4. Downloads the sources and checks each one against the recipe's own sha256sums. If one
     doesn't match, nothing is built.

Things to know:
  - /usr/ports/aur comes last in /etc/prt-get.conf: CRUX's and Krest's own ports always win
    over a converted one with the same name.
  - Recipes that need systemd say so in the Pkgfile ("# Note: needs systemd"); they may need
    editing, or may not work on Krest at all.
  - Sources the recipe marks SKIP (git checkouts, mostly) can't be checked; port-aurum says so.
  - After it has built once, the port is an ordinary CRUX port: prt-get update foo, prt-get
    remove foo and port-undo foo all work. To pick up a newer AUR version, run port-aurum foo
    again.
  - A port that's worth keeping can be tidied into a proper Pkgfile (see: pkgfiles) and put in
    Krest's own collection.

## port-undo: taking back a bad update
CRUX has no snapshots, but every package prt-get builds is kept in /usr/ports/packages, one
file per version (foo#1.2-1.pkg.tar.zst). Going back is reinstalling the older file: seconds,
with nothing compiled.

  port-undo                       packages that have an older version kept, newest first
  sudo port-undo foo              reinstall foo's previous version, then lock foo
  sudo port-undo foo FILE         reinstall that exact package file
  sudo prt-get unlock foo         let updates rebuild foo again (once its next version is out)

port-undo locks foo so the next krest-update doesn't rebuild the version that broke. To see
what's locked: prt-get listlocked. Old package files take disk space; clear ones you're sure
you won't need with  sudo rm /usr/ports/packages/foo#OLD-VERSION.pkg.tar.*

## krest-fingerprint: fingerprint for sudo
The Framework's fingerprint reader works through fprintd and libfprint. krest-fingerprint
sets it up for sudo, and for programs that ask for your password through polkit.

  krest-fingerprint               enrol a finger (touch the reader about 10 times), then
                                  switch fingerprint on for sudo
  krest-fingerprint add           enrol another finger
  krest-fingerprint off           back to passwords only (enrolled fingers are kept)
  krest-fingerprint forget        delete your enrolled fingers

With it on, sudo asks for a finger first; give it 10 seconds or press Ctrl+C, and it asks
for your password as usual. The login screen (ly) and the screen lock (slock) keep using
your password. It works by adding one line, pam_fprintd, to the top of /etc/pam.d/sudo and
/etc/pam.d/polkit-1, and telling pkgadd (/etc/pkgadd.conf) not to overwrite those two files
when sudo or polkit is upgraded. See: users (PAM).

## krest-update: keeping everything current
  krest-update                    Krest's ports (git pull), CRUX's (ports -u), then
                                  prt-get sysup: every update, built here; then the newest
                                  CRUX handbook
  krest-update --dry              only show what would be rebuilt

After it rebuilds the kernel ("linux"), restart to use the new one. If an update breaks
something: port-undo. Files an update wanted to replace but kept aside: sudo rejmerge.

## krest-handbook: the CRUX handbook, offline
  krest-handbook                  the handbook in less (/ searches, q quits)
  krest-handbook mc               beside this wiki, in Midnight Commander
  krest-handbook notes            CRUX 3.8's release notes
  krest-handbook update           fetch the newest handbook from crux.nu now
See: handbook.

## krest-wifi: Wi-Fi without NetworkManager
The install stick has no NetworkManager (CRUX's own stick doesn't carry it), so the installer
gets online with krest-wifi: a menu over wpa_supplicant and dhcpcd. Pick a network, type its
password. It's on the installed system too, for the rare time NetworkManager isn't running
(say, carrying on an interrupted install with  sudo krest-install --continue). Day to day,
Wi-Fi is NetworkManager: nmtui, or the network menu (networkmanager-dmenu).

See also: prt-get, pkgutils, pkgfiles, ports, from-arch, users, handbook ; port-help

# xtools

xtools is a collection of small shell scripts by Leah Neukirchen, a Void developer, that make
XBPS and xbps-src quicker to use. Pustota installs it. Each script is short: read one with
less "$(command -v xdowngrade)".

## Using packages
  xi foo              xbps-install with sudo built in; also finds packages you built in
                      ./hostdir/binpkgs (inside a void-packages checkout)
  xq foo ; xq -R foo  information about a package, installed ; in the repositories
  xrs word            search the repositories, like xbps-query -Rs (also packages you built)
  xlocate PATH        which package, installed or not, has a file. Needs its index first:
                      xlocate -S (downloads it; run again now and then to refresh)
  xls foo             the files of a package
  xhog                installed packages, largest first
  xdowngrade FILE     install an older version from /var/cache/xbps (see: xbps)
  xcheckrestart       programs still running old, deleted libraries after an update:
                      restart those (or log out and in, or reboot after a kernel update)
  xetcchanges         the differences between your /etc and what the packages installed
  xilog               installed packages by install date, newest last: what came in with
                      the last update (xilog firefox: when it was installed or updated)
  xuname              uname -a plus the Void details: kernel package, libc, repository

## System administration
  xchroot DIR         chroot into an installed system with /dev, /proc, /sys and /run mounted:
                      the rescue tool (see: pustota-learn learn recovery)
  xgenfstab -U DIR    write an /etc/fstab for what is mounted under DIR, by UUID (the installer
                      uses it)

  xmksv NAME          create /etc/sv/NAME with a run script to fill in (-l: and a log/)

## Writing packages (see: xbps-src)
  xnew NAME           start a new template
  xgensum -i FILE     fill in a template's checksum
  xbump NAME          commit a template change with Void's commit message style
  xlint FILE          check a template against Void's rules
  xsubpkg NAME        list a package's subpackages

See also: xbps, xbps-src ; man xtools (one page for all of them) ;
https://github.com/leahneukirchen/xtools

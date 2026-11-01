# XBPS

XBPS, the X Binary Package System, is Void's package manager, written for Void. It is a set
of small programs, one per job, rather than one program with many modes. All of them have a
manual page; man xbps-install is the place to start.

## The tools
  xbps-install       install and update (-S sync the repository index, -u update)
  xbps-remove        remove packages, orphans (-o) and old cached packages (-O)
  xbps-query         ask anything: installed (default) or in the repositories (-R)
  xbps-reconfigure   run a package's configure step again (-f force, -a all)
  xbps-pkgdb         check the package database; mark packages (hold, manual, auto ...)
  xbps-alternatives  choose between packages that provide the same command
  xbps-rindex        build and sign a repository index (Pustota's build uses it)
  xbps-create        make a package from a folder (Pustota's own packages are made with it)
  xbps-uhelper       small helpers: xbps-uhelper arch, xbps-uhelper cmpver 1.2 1.10
  xbps-fetch, xbps-digest, xbps-checkvers, xbps-uchroot, xbps-uunshare  (mostly for xbps-src)

## Everyday use
  sudo xbps-install -Su                 update everything (the only supported way to update)
  sudo xbps-install foo bar             install
  sudo xbps-remove -R foo               remove foo and what it pulled in that nothing else needs
  sudo xbps-remove -o                   remove orphans (dependencies nothing needs any more)
  xbps-query -Rs word                   search names and descriptions in the repositories
  xbps-query -R foo                     details of a package you have not installed
  xbps-query foo                        details of an installed package
  xbps-query -f foo                     its files
  xbps-query -o /usr/bin/ls             which installed package owns a file
  xbps-query -x foo ; -X foo            what foo depends on ; what depends on foo
  xbps-query -m                         what you installed on purpose (not as dependencies)
  xbps-query -l | wc -l                 how many packages are installed
  xbps-query -L                         the repositories in use

Add -n to install or remove to see what would happen without doing it.

When an update includes XBPS itself, xbps-install -Su updates only XBPS and stops: run it
again for the rest. Partial upgrades (updating one package against an old system) are not
supported; install new packages after an update, not instead of one.

## Configuration: /etc/xbps.d and /usr/share/xbps.d
XBPS reads every *.conf in both folders. A file in /etc/xbps.d replaces the file of the same
name in /usr/share/xbps.d, so packages ship defaults in /usr/share and you override in /etc.

  repository=URL      use a repository (see: repositories)
  ignorepkg=NAME      never install NAME as a dependency, never update it
                      (Pustota: ignorepkg=linux, so Void's older default kernel stays out)
  virtualpkg=A:B      satisfy dependency A with package B
  noextract=/path/*   never install these files (for example, documentation you do not want)
  preserve=/path      keep this file when the package that owns it is updated or removed
  syslog=true         log transactions to syslog (default; see: logging)

man xbps.d lists every key.

## Configuration files you have changed
Files a package marks as configuration (conf_files in its template) are protected: if you
have edited one and an update brings a new version, XBPS keeps yours and saves the new one
beside it as NAME.new-VERSION. Compare them (diff), merge what you need, delete the .new file.
xetcchanges (xtools) lists what in /etc differs from the packaged files.

## Holds, manual and automatic
  sudo xbps-pkgdb -m hold foo           never update foo (until -m unhold foo)
  xbps-query -H                         list holds
  sudo xbps-pkgdb -m manual foo         keep foo even if nothing depends on it
  sudo xbps-pkgdb -m auto foo           foo is only a dependency: xbps-remove -o may remove it
  sudo xbps-pkgdb -m repolock foo       only ever update foo from the repository it came from

## The cache and going back
Every downloaded package stays in /var/cache/xbps until you clean it, which is what makes
downgrading possible (there are no snapshots on XFS):

  ls /var/cache/xbps/foo-*                              the versions you have
  sudo xdowngrade /var/cache/xbps/foo-1.2_1.x86_64.xbps   (xtools) install an older one
  sudo xbps-pkgdb -m hold foo                           keep it there for now
  sudo xbps-remove -O                                   clean the cache: only when all is well
  du -sh /var/cache/xbps

## Reconfigure
xbps-reconfigure runs a package's configure step again. Configure is where a package does its
setup: the kernel builds its initramfs and updates GRUB, glibc-locales compiles locales,
fonts rebuild the font cache.

  sudo xbps-reconfigure -f linux-mainline     rebuild the initramfs (after changing dracut)
  sudo xbps-reconfigure -f glibc-locales      after editing /etc/default/libc-locales
  sudo xbps-reconfigure -fa                   everything (what the installer runs at the end)

## Alternatives
Some commands can come from more than one package (vi from vim or nvi, for example).
  xbps-alternatives -l                  what is provided by whom
  sudo xbps-alternatives -s nvi -g vi   choose
The chosen package's files become links in /usr/bin.

## Keys
Repositories are signed. The first time XBPS meets a key it shows the fingerprint and asks;
the answer is stored in /var/db/xbps/keys/ as FINGERPRINT.plist. Pustota's installer copies
Void's keys and Pustota's own there, so an installed system never asks.

## Errors you may meet
  "unresolvable shlib"        the repository is half-updated (a mirror mid-sync). Wait an hour,
                              or try another mirror (see: repositories).
  "transaction aborted ... conflicts"   two packages want the same file; read which, remove one.
  "package is on hold"        you held it: xbps-query -H.
  "not enough free space"     clean the cache: sudo xbps-remove -O.
  Repairing the database:     sudo xbps-pkgdb -a   (checks every package's files and deps)

See also: xtools, xbps-src, repositories, from-arch ; man xbps-install ; man xbps-query ;
man xbps-remove ; man xbps-pkgdb ; man xbps.d ; https://docs.voidlinux.org/xbps/

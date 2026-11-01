# Repositories

A repository is a folder (local or on a web server) of .xbps packages with an index,
x86_64-repodata, that XBPS downloads with xbps-install -S. Repositories are listed by
repository= lines in /etc/xbps.d and /usr/share/xbps.d (see: xbps).

## Void's repositories
  current             the main one: free software, glibc, x86_64
  current/nonfree     software that is not free (Intel microcode, some firmware). Pustota
                      enables it: intel-ucode lives here (package void-repo-nonfree)
  current/multilib    32-bit libraries for 64-bit systems, mostly for Steam and Wine
                      (void-repo-multilib, and void-repo-multilib-nonfree)
  current/debug       -dbg packages with debugging symbols (void-repo-debug)
  current/bootstrap   only what xbps-src's build container needs
  current/musl, current/aarch64   the other editions: not for this machine

Each extra repository is enabled by installing its void-repo-* package, which only drops a
.conf file into /usr/share/xbps.d. Removing the package disables it.

  xbps-query -L                      the repositories in use, with package counts

## Mirrors
repo-default.voidlinux.org sends you to a nearby mirror. To choose one yourself:

  sudo xbps-install xmirror ; sudo xmirror           a menu of every mirror, with locations

or by hand: copy /usr/share/xbps.d/00-repository-main.conf to /etc/xbps.d/ (same name, so it
replaces the default) and change the address, then sudo xbps-install -S. Do the same for
10-repository-nonfree.conf. Pustota's installer does this if the default mirror does not answer.
The mirror list with locations: https://xmirror.voidlinux.org

## Pustota's repository
Pustota's own packages (pustota-desktop, pustota-learn, pustota-russian, x-terminal, ani-cli,
ollama-bin) come from its signed repository:

  /usr/share/xbps.d/20-pustota-repository.conf
      repository=https://github.com/factionparadox/Pustota/releases/download/repo-x86_64

Its key is in /var/db/xbps/keys/ (the installer put it there). The install stick also carries
a copy of the repository in /usr/lib/pustota/repo.

## A repository of your own
Any folder of packages can be one:

  xbps-rindex -a /path/to/folder/*.xbps        index it
  sudo xbps-install -R /path/to/folder foo     install from it once
  echo 'repository=/path/to/folder' | sudo tee /etc/xbps.d/50-mine.conf    or always

Signing (needed for a repository on the network): xbps-rindex --sign and --sign-pkg with an
RSA key; Pustota's build/sign-repo.sh shows the whole process.

See also: xbps, xbps-src ; man xbps.d ; man xbps-rindex ;
https://docs.voidlinux.org/xbps/repositories/

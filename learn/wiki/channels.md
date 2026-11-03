# Channels and substitutes

## Channels
A channel is a Git repository of Guix modules: package definitions, service types, system
code. guix pull fetches the newest commit of each channel in your list, checks it, and builds a
guix command from them into ~/.config/guix/current. Everything Guix knows about packages comes
from there, so "updating the package lists" and "updating Guix" are the same step.

Rassvet's list is %rassvet-channels in system.scm; guix-service-type writes it to
/etc/guix/channels.scm:
  guix      https://codeberg.org/guix/guix.git          branch master
  nonguix   https://gitlab.com/nonguix/nonguix          branch master
  rassvet   https://github.com/factionparadox/Pustota   branch main
guix pull reads ~/.config/guix/channels.scm if you have one, and /etc/guix/channels.scm if not.

  guix pull                          update your guix (rassvet-update does this first)
  guix describe                      the commit of each channel you are on now
  guix pull -l                       every pull; guix pull --roll-back undoes the last
  guix pull --commit=COMMIT          the guix channel at a given commit
  guix time-machine -C file.scm -- CMD   run CMD with other channels, without pulling

Each user pulls their own guix; root has its own too. rassvet-update runs
sudo -E ~/.config/guix/current/bin/guix system reconfigure, so the system is built from what
you just pulled, not from root's guix.

The first guix pull takes a while (it compiles Guix, a few minutes and a few hundred MB);
later ones only rebuild what changed.

## Authentication
guix and nonguix carry an introduction: the commit where authentication starts, and the
OpenPGP fingerprint of the key that signed it. From there, each commit must be signed by a key
listed in the channel's own .guix-authorizations at the time, or guix pull refuses it; a
mirror or a man in the middle cannot slip a commit in. Rassvet's channel has no introduction in
%rassvet-channels, so it is fetched from GitHub over HTTPS without that check.
The repository's channels.scm pins Guix and Nonguix to exact commits for building the ISO
(guix time-machine -C channels.scm); guix describe on an up-to-date system shows newer ones.

## Substitutes
A substitute is a prebuilt store item from a server. Rassvet uses, in this order:
  https://substitutes.nonguix.org    Nonguix's packages (the kernel, Firefox, Steam ...)
  https://bordeaux.guix.gnu.org      Guix's build farms
  https://ci.guix.gnu.org
(substitute-urls in system.scm's guix-configuration). Every substitute is signed; guix-daemon
accepts only those signed by a key in /etc/guix/acl, which system.scm makes: Guix's two keys
and Nonguix's (guix/rassvet/files/nonguix-signing-key.pub). Because a store item's name is a
hash of its inputs, a substitute is the same thing your own build would produce.

  guix weather firefox                      is it available, and from where
  guix build --no-substitutes foo           build it yourself anyway
  sudo guix archive --authorize < key.pub   trust another server (or add it in the declaration)

## Offline
guix archive --export and --import move store items without a network: the installer
imported the whole system from the stick that way (see: rassvet-learn learn install).

See also: guix-packages, guix-packaging, system ; info "(guix) Channels" ;
info "(guix) Invoking guix pull" ; info "(guix) Substitutes" ; info "(guix) Channel Authentication"

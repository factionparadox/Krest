# The Guix manual and Cookbook, offline

The GNU Guix Reference Manual is Guix's official documentation, written by its developers and
kept in step with the code: installation, package management, channels, the system
declaration, every service type and its fields, the store, packaging. The GNU Guix Cookbook is
its companion of worked examples and tutorials (packaging, custom kernels, system
configurations). Both come with Guix itself, as info manuals: the system's, and a newer copy
with every guix pull (~/.config/guix/current/share/info).

## Reading it
  rassvet-handbook            the Guix manual in info (menu -> Learn -> Guix manual)
  rassvet-handbook cookbook   the Cookbook
  rassvet-handbook mc         Midnight Commander with this wiki on one side and the info files
                              on the other
  info guix                   the same, in any terminal
  info "(guix) Invoking guix system"      straight to one node
  info shepherd               Shepherd's manual (herd, writing services)

info's keys:
  arrows, Enter               move to a link and follow it
  n / p / u                   next, previous and up node
  l                           back to where you were
  s                           search the whole manual; s again (or }) for the next match
  i                           the index: type a word (a command, a service type, a field)
  q                           quit

The index is the quickest way in: i, then nftables-service-type, guix gc, kernel-arguments ...
For any command, guix NAME --help prints its options.

## Online
  https://guix.gnu.org/manual/            the manual, also in other languages
  https://guix.gnu.org/cookbook/          the Cookbook
  https://packages.guix.gnu.org/          every package, with its versions
Nonguix's README covers its kernel, firmware and substitutes:
https://gitlab.com/nonguix/nonguix

## Where it fits
The manual says how Guix is meant to be used; this wiki explains the same system at shorter
length, with Rassvet's own choices; the lessons (rassvet-learn learn) are the short tour. When
they disagree, the manual and the manual pages are right.

See also: index ; info info ; https://guix.gnu.org/en/help/

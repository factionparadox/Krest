# xbps-src

xbps-src builds Void packages from source. Every package in Void's repositories is built by
it, from a template in the void-packages repository on GitHub. It is the Void counterpart of
Arch's makepkg and PKGBUILD, but it always builds in a clean container (a "masterdir") that
holds only base-chroot and the dependencies the template names, so a build does not depend on
what happens to be installed on your machine.

## Getting started
  git clone --depth 1 https://github.com/void-linux/void-packages
  cd void-packages
  ./xbps-src binary-bootstrap        make the clean build container (once)
  ./xbps-src pkg htop                build htop and everything it needs
  xi -f htop                         install what you built (xtools; or the line below)
  sudo xbps-install -R hostdir/binpkgs -f htop

Built packages go to hostdir/binpkgs/, which is itself a repository (xbps-rindex has indexed it).

## A template
srcpkgs/NAME/template is a shell file of variables and functions:

  pkgname=hello
  version=2.12
  revision=1
  build_style=gnu-configure          how to build: gnu-configure, meson, cmake, cargo, go ...
  hostmakedepends="pkg-config"       needed on the build machine
  makedepends="ncurses-devel"        libraries to build against
  depends="ncurses"                  needed at run time (shared libraries are found by themselves)
  short_desc="Prints a friendly greeting"   (72 characters at most)
  maintainer="You <you@example.org>"
  license="GPL-3.0-or-later"
  homepage="https://www.gnu.org/software/hello/"
  distfiles="${GNU_SITE}/hello/hello-${version}.tar.gz"
  checksum=...                       (xgensum -i srcpkgs/hello/template fills it in)

Where build_style is not enough, define do_build, do_install and so on, or pre_/post_ versions
of each step. Inside them, helpers such as vbin, vman, vlicense, vsv (install a runit service
from files/) and vsed (sed that fails if nothing changed) keep templates short.
srcpkgs/*/template is thousands of worked examples: grep for what you need.

The steps run in order: fetch, extract, patch (files in srcpkgs/NAME/patches/), configure,
build, check, install, then packaging. ./xbps-src -h lists the commands; ./xbps-src show NAME
prints a template's variables.

## Useful commands
  ./xbps-src show-build-deps NAME    what it needs
  ./xbps-src -C pkg NAME             build without cleaning up afterwards (inspect masterdir)
  ./xbps-src clean                   remove leftovers from failed builds
  ./xbps-src -f pkg NAME             rebuild even if already built
  xnew NAME                          start a new template (xtools)
  xlint srcpkgs/NAME/template        check it against Void's style rules

## Restricted packages
Some templates (Discord, for example) are marked restricted=yes: Void may not redistribute
them as binaries, so they are not in the repositories, but you may build them for yourself:

  echo XBPS_ALLOW_RESTRICTED=yes >> etc/conf
  ./xbps-src pkg discord

## Pustota's own templates
Pustota's repository has srcpkgs/ with templates for what Void lacks: x-terminal
(X-терминал), intel-lpmd, ani-cli and ollama-bin. Pustota's build copies them into a void-packages
checkout pinned to one commit, builds them with xbps-src and signs the result into Pustota's
repository. To change one (X-терминал's colours, for example), edit it and build it like any
other: pustota-learn learn building has the steps.

See also: xbps, xtools ; void-packages/README.md and Manual.md (every variable and helper) ;
https://github.com/void-linux/void-packages ;
https://docs.voidlinux.org/xbps/repositories/restricted.html

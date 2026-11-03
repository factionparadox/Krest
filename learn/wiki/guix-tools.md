# Guix's tools

guix is one command with many subcommands, each documented in the manual (info "(guix) Invoking
guix NAME") and by guix NAME --help. These are the ones for looking, trying and tracing.

## Looking
  guix show foo          a package's version, inputs, licence, home page, description
  guix search word       packages whose name or description matches
  guix edit foo          opens the package's definition in $EDITOR (mcedit), read-only: the
                         recipe that built it, the best way to learn how Guix packages work
  guix size foo          foo and everything it needs, with the size of each
  guix graph foo         its dependency graph, as Graphviz text:
                           guix graph foo | guix shell graphviz -- dot -Tpdf > foo.pdf
                         --type=references shows the built store items instead of packages
  guix describe          the channels and commits your guix comes from
  guix system describe   the same for the running system, with its kernel and config file
  guix locate FILE       which package has a file (guix locate --update builds its index)
  guix weather foo       whether substitutes are available for it
  guix processes         the Guix sessions and builds running now

## Trying, without installing
  guix shell python python-requests -- python3
                         a shell (or one command) with those packages, gone when it exits
  guix shell -D foo      everything needed to build foo: a development environment
  guix shell --container firefox
                         isolated from your home folder and the rest of the system
                         (--network, --share=DIR to let some of it in)
  guix shell -m manifest.scm   a project's packages, from its manifest
Nothing is added to your profile; what was downloaded stays in the store until guix gc.

## Travelling in time
  guix time-machine --commit=dda299a -- show foo
                         run the guix of another commit (here: an older one)
  guix time-machine -C channels.scm -- system build config.scm
                         exactly the channels in that file: Rassvet's build uses this, with
                         channels.scm in the repository pinning Guix and Nonguix
  guix describe -f channels > pinned.scm      today's channels, written out to pin them

## Packaging helpers (see: guix-packaging)
  guix download URL      fetch a file into the store and print its hash
  guix hash -rx .        the hash of a Git checkout (for git-fetch sources)
  guix import pypi foo   a first package definition from PyPI (also crate, gem, cran ...)
  guix lint foo          check a definition against Guix's rules
  guix refresh foo       is there a newer upstream release?
  guix build --check foo build again and compare: is it reproducible?
  guix challenge foo     compare your build with the substitute servers'
  guix repl              a Guile REPL with Guix's modules loaded

See also: guix-packages, guix-packaging, channels ; info "(guix) Utilities" ;
info "(guix) Invoking guix shell" ; info "(guix) Invoking guix time-machine"

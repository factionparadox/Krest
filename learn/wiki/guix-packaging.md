# Writing Guix packages

A Guix package is a Scheme value: a package record giving the source (with its hash), the
build system, the inputs and some metadata. Guix's own packages are in gnu/packages/*.scm of
the guix channel, Nonguix's in nongnu/packages, Rassvet's in guix/rassvet/packages.scm. Every
build happens in an isolated container holding only the declared inputs, so it does not depend
on what is installed on your machine. guix edit NAME shows any package's definition: thousands
of worked examples.

## A package
  (use-modules (guix packages) (guix download) (guix build-system gnu)
               ((guix licenses) #:prefix license:))

  (define-public hello
    (package
      (name "hello")
      (version "2.12.1")
      (source (origin
                (method url-fetch)
                (uri (string-append "mirror://gnu/hello/hello-" version ".tar.gz"))
                (sha256 (base32 "..."))))   ; guix download URL prints it
      (build-system gnu-build-system)     ; ./configure && make && make install
      ;; (inputs (list ncurses))          ; libraries it links against, if any
      ;; (native-inputs (list pkg-config)) ; tools needed only to build
      (synopsis "Greet the world")
      (description "GNU Hello prints a friendly greeting.")
      (home-page "https://www.gnu.org/software/hello/")
      (license license:gpl3+)))

Build systems: gnu, cmake, meson, python (pyproject), cargo, go, zig, copy (just install
files), trivial, and more. Each has standard phases (unpack, configure, build, check, install);
#:phases with modify-phases adds, replaces or deletes one, as Rassvet's x-terminal does to
copy in its config.h and rename st to x-terminal.

## Building and trying
  guix build -L ~/mypkgs hello         build from a folder of modules (-L adds it to the path)
  guix build -f hello.scm              build the package a file returns
  guix install -L ~/mypkgs hello       and install it in your profile
  guix shell -L ~/mypkgs hello -- hello
  guix build --keep-failed hello       on failure, keep the build folder (/tmp/guix-build-...)
  guix lint -L ~/mypkgs hello          style and common mistakes
  guix shell -D hello                  a shell with hello's build inputs, to work by hand

## Rassvet's channel
guix/rassvet/packages.scm defines what Guix and Nonguix lack:
  x-terminal        st 0.9.3 through st-flexipatch, Rassvet's config.h and patches.h
  ly                the login screen, with Zig 0.16 and its six Zig libraries, each pinned
  rassvet-desktop   desktop/root: the session, menus, scripts, keys, bar (copy-build-system,
                    with /usr paths rewritten to /run/current-system/profile)
  rassvet-learn     these lessons and this wiki
  rassvet-russian   the Russian kit
  piper-tts         Piper's own release build, its loader paths pointed into the store
The repository's .guix-channel makes it a channel (directory "guix", depending on Nonguix), and
system.scm's %rassvet-channels adds it to guix pull. From a checkout:
  guix build -L guix x-terminal        (rassvet-learn learn building has the steps)

## A channel of your own
Put your modules in a Git repository (a .guix-channel file is optional), then copy
/etc/guix/channels.scm to ~/.config/guix/channels.scm and add yours to the list:
  (channel (name 'mine) (url "https://example.org/mine.git") (branch "main"))
Your file replaces the system one for your guix pull, so keep Rassvet's three in it.

Non-free software: Guix's own channel takes only free software; Nonguix is where the
rest lives (the kernel with firmware, Firefox, Steam). Its packages are built the same way.

See also: guix-tools, channels ; info "(guix-cookbook) Packaging Tutorial" ;
info "(guix) Defining Packages" ; info "(guix) Build Systems" ; info "(guix) Channels"

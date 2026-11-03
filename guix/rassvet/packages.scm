;;; Рассвет / Rassvet: the packages Guix and Nonguix do not have, and Rassvet's own files.
;;;
;;;   x-terminal        X-терминал: st 0.9.3 through st-flexipatch, with a Plan 9 look
;;;   rassvet-desktop   the session, the menus and scripts (rassvet-*), keys, bar, branding
;;;   rassvet-learn     rassvet-learn: lessons and the wiki, offline
;;;   rassvet-russian   the Russian kit (the material itself downloads later)
;;;   piper-tts         Piper's speech, from its release (for the Russian voices)
;;;
;;; Every source is pinned: a git commit with its hash, or this repository's own files.
(define-module (rassvet packages)
  #:use-module (guix packages)
  #:use-module (guix gexp)
  #:use-module (guix git-download)
  #:use-module (guix utils)
  #:use-module (guix build-system gnu)
  #:use-module (guix build-system copy)
  #:use-module (guix build-system zig)
  #:use-module (guix download)
  #:use-module (gnu packages base)
  #:use-module (gnu packages elf)
  #:use-module (gnu packages gcc)
  #:use-module ((guix licenses) #:prefix license:)
  #:use-module (gnu packages fontutils)
  #:use-module (gnu packages ncurses)
  #:use-module (gnu packages pkg-config)
  #:use-module (gnu packages python)
  #:use-module (gnu packages linux)
  #:use-module (gnu packages xorg)
  #:use-module (gnu packages zig)
  #:use-module (gnu packages zig-xyz)
  #:export (rassvet-file))

;; This repository's files, wherever it is: a checkout (guix ... -L guix) or the rassvet channel
;; in the store after guix pull (the channel's modules are a link into the whole checkout).
;; A relative local-file would be taken relative to the current directory instead.
(define %rassvet-root
  (dirname (dirname (dirname (canonicalize-path
                              (search-path %load-path "rassvet/packages.scm"))))))

(define (rassvet-file . parts)
  (string-join (cons %rassvet-root parts) "/"))

(define-public x-terminal
  (package
    (name "x-terminal")
    (version "0.9.3")
    (source
     (origin
       (method git-fetch)
       (uri (git-reference
             (url "https://github.com/bakkeby/st-flexipatch")
             (commit "9c733c4b78bf3a145f25a737beac38c52ad63b76")))
       (file-name (git-file-name "st-flexipatch" version))
       (sha256
        (base32 "0464ckqqvhb9w5i88w50qjb7pgp0i3a6q2ccrmdx69jhzj54nvz6"))))
    (build-system gnu-build-system)
    (arguments
     (list
      #:tests? #f                       ;st has no tests
      #:make-flags
      #~(list (string-append "CC=" #$(cc-for-target))
              (string-append "PKG_CONFIG=" #$(pkg-config-for-target))
              (string-append "TERMINFO=" #$output "/share/terminfo")
              (string-append "PREFIX=" #$output))
      #:phases
      #~(modify-phases %standard-phases
          (delete 'configure)
          (add-after 'unpack 'rassvet-look
            (lambda _
              ;; patches.h picks the patches; config.h is the look and the keys
              (copy-file #$(local-file (rassvet-file "extras/x-terminal/config.h") "config.h") "config.h")
              (copy-file #$(local-file (rassvet-file "extras/x-terminal/patches.h") "patches.h") "patches.h")
              ;; the window's name and class: X-терминал, not st
              (substitute* "x.c"
                (("\\(opt_line \\|\\| !opt_cmd\\) \\? \"st\" : opt_cmd\\[0\\]")
                 "(opt_line || !opt_cmd) ? \"X-терминал\" : opt_cmd[0]")
                (("opt_name \\? opt_name : \"st\"")
                 "opt_name ? opt_name : \"x-terminal\""))))
          (add-after 'install 'rename
            (lambda _
              ;; installed as x-terminal, so it never clashes with any other st
              (rename-file (string-append #$output "/bin/st")
                           (string-append #$output "/bin/x-terminal"))
              (let ((man (string-append #$output "/share/man/man1/")))
                (rename-file (string-append man "st.1")
                             (string-append man "x-terminal.1"))))))))
    (inputs (list libx11 libxft fontconfig freetype))
    (native-inputs (list ncurses pkg-config))
    (home-page "https://github.com/factionparadox/Pustota")
    (synopsis "X-терминал: Rassvet's terminal (st with scrollback, Plan 9 look)")
    (description
     "X-терминал is st, the suckless terminal, built from st-flexipatch with
scrollback, clickable links and Plan 9's acme colours and Go Mono font.")
    (license (list license:x11 license:expat))))

(define-public rassvet-desktop
  (package
    (name "rassvet-desktop")
    (version "0.2")
    (source (local-file (rassvet-file "desktop/root") "rassvet-desktop" #:recursive? #t))
    (build-system copy-build-system)
    (arguments
     (list
      #:install-plan
      #~'(("usr/bin/" "bin/")
          ("usr/share/rassvet/" "share/rassvet/")
          ("usr/share/pixmaps/" "share/pixmaps/")
          ("etc/rassvet/" "share/rassvet/etc/")
          ("etc/xdg/fastfetch/" "share/rassvet/fastfetch/")
          ("etc/firefox/" "share/rassvet/firefox/"))
      #:phases
      #~(modify-phases %standard-phases
          (add-after 'unpack 'guix-paths
            (lambda _
              ;; On Guix, programs live in the system profile, not /usr.
              (substitute* (append (find-files "usr/bin")
                                   (find-files "usr/share/rassvet/skel")
                                   (find-files "etc/rassvet"))
                (("/usr/share/rassvet") "/run/current-system/profile/share/rassvet")
                (("/usr/share/xsessions") "/run/current-system/profile/share/xsessions")
                (("/usr/share/zoneinfo") "/run/current-system/profile/share/zoneinfo")
                (("/usr/lib/plan9") "/run/current-system/profile/plan9")
                (("/usr/bin/") "/run/current-system/profile/bin/"))
              (substitute* "etc/xdg/fastfetch/config.jsonc.in"
                (("@VERSION@") #$version))))
          (add-after 'install 'session
            (lambda _
              ;; ly's session list: one entry, Rassvet's
              (let ((dir (string-append #$output "/share/xsessions")))
                (mkdir-p dir)
                (call-with-output-file (string-append dir "/rassvet.desktop")
                  (lambda (port)
                    (display "[Desktop Entry]
Name=Rassvet
Comment=ratpoison, polybar and the Rassvet tools
Exec=/run/current-system/profile/bin/rassvet-session
Type=Application
DesktopNames=rassvet
" port)))))))))
    (home-page "https://github.com/factionparadox/Pustota")
    (synopsis "Rassvet's desktop: ratpoison session, menus, keys and scripts")
    (description "The Rassvet session (rassvet-session), its dmenu menus, the
ratpoison keys, polybar's bar, X resources, home-folder defaults and branding.")
    (license license:gpl3+)))

(define-public rassvet-learn
  (package
    (name "rassvet-learn")
    (version "0.2")
    (source (local-file (rassvet-file "learn") "rassvet-learn" #:recursive? #t))
    (build-system copy-build-system)
    (arguments
     (list #:install-plan
           #~'(("rassvet-learn" "bin/")
               ("topics/" "share/rassvet/learn/topics/" #:include-regexp ("\\.md$"))
               ("wiki/" "share/rassvet/learn/wiki/" #:include-regexp ("\\.md$")))))
    (inputs (list python))
    (home-page "https://github.com/factionparadox/Pustota")
    (synopsis "Rassvet Learn: understand and inspect the system")
    (description "Lessons and a wiki about Rassvet and Guix System, with search,
@command{explain} (what a command would do, without running it) and a read-only map
of the running system.")
    (license license:gpl3+)))

(define-public piper-tts
  ;; Piper's own Linux build (its onnxruntime and espeak-ng included), with the loader and
  ;; library paths pointed into the store.
  (package
    (name "piper-tts")
    (version "2023.11.14-2")
    (source
     (origin
       (method url-fetch)
       (uri (string-append "https://github.com/rhasspy/piper/releases/download/"
                           version "/piper_linux_x86_64.tar.gz"))
       (sha256
        (base32 "14jr49pa58x7sbkcpj4c745blxvqf5hb7haqszvg2yjv6mgv8355"))))
    (build-system copy-build-system)
    (arguments
     (list
      #:install-plan #~'(("." "lib/piper/"))
      #:validate-runpath? #f
      #:phases
      #~(modify-phases %standard-phases
          (add-after 'install 'patchelf
            (lambda* (#:key inputs #:allow-other-keys)
              (let* ((dir (string-append #$output "/lib/piper"))
                     (ld (search-input-file inputs "/lib/ld-linux-x86-64.so.2"))
                     (rpath (string-append dir ":" (dirname ld) ":"
                                           #$gcc:lib "/lib")))
                (for-each (lambda (file)
                            (when (elf-file? file)
                              (invoke "patchelf" "--set-rpath" rpath file)))
                          (find-files dir))
                (for-each (lambda (exe)
                            (invoke "patchelf" "--set-interpreter" ld
                                    (string-append dir "/" exe)))
                          '("piper" "piper_phonemize" "espeak-ng"))))))))
    (native-inputs (list patchelf))
    (inputs (list glibc `(,gcc "lib")))
    (supported-systems '("x86_64-linux"))
    (home-page "https://github.com/rhasspy/piper")
    (synopsis "Fast local neural text to speech")
    (description "Piper speaks text with neural voices (ONNX models), on the CPU.")
    (license license:expat)))

(define-public rassvet-russian
  (package
    (name "rassvet-russian")
    (version "0.2")
    (source (local-file (rassvet-file "russian") "rassvet-russian" #:recursive? #t))
    (build-system copy-build-system)
    (arguments
     (list #:phases
           #~(modify-phases %standard-phases
               (add-after 'unpack 'piper
                 (lambda _
                   (substitute* "rassvet-russian"
                     (("/usr/lib/rassvet/piper/piper")
                      #$(file-append piper-tts "/lib/piper/piper"))))))
           #:install-plan
           #~'(("rassvet-russian" "bin/")
               ("rassvet-content" "bin/")
               ("." "lib/rassvet/content/" #:include-regexp ("^\\./fetch-.*\\.py$" "mirror\\.json$"))
               ("." "share/rassvet/russian/"
                #:include-regexp ("\\.tsv$" "VOCAB-SOURCES\\.md$")))))
    (inputs (list python))
    (home-page "https://github.com/factionparadox/Pustota")
    (synopsis "Rassvet's Russian kit: A1 to B2, offline")
    (description "Constellation's Russian kit: a 10,000-word drill, courses, a
dictionary, audiobooks and an optional local AI tutor; the material downloads with
@command{rassvet-content}.")
    (license license:gpl3+)))

;;; ly, the login screen (a text box on tty1). Not in Guix. ly 1.4.1 builds with Zig 0.16 and
;;; six Zig libraries, each pinned here at the commit ly's build.zig.zon names.
(define (zig-source name version url commit hash)
  (origin
    (method git-fetch)
    (uri (git-reference (url url) (commit commit)))
    (file-name (git-file-name name version))
    (sha256 (base32 hash))))

(define zig-clap-for-ly
  (package
    (inherit zig-clap)
    (version "0.11.0-fc1e5cc")
    (source (zig-source "zig-clap" version "https://github.com/Hejsil/zig-clap"
                        "fc1e5cc3f6d9d3001112385ee6256d694e959d2f"
                        "0bq32n0i7r6wcck76vmcgcks8r7smfg8q2c0rcq19x1adrjw505h"))
    (arguments (list #:zig zig-0.16 #:tests? #f))))

(define zig-ini-for-ly
  (package
    (name "zig-ini")
    (version "0.1.0-3b733e1")
    (source (zig-source name version "https://github.com/AshAmetrine/ziglibs-ini"
                        "3b733e10adc6c4c48050709b97a22258bc2e6156"
                        "1mfyn1adhaq8qhx3xl7nmp679kfjih072098acmh6gi9rhab7vmp"))
    (build-system zig-build-system)
    (arguments (list #:zig zig-0.16 #:tests? #f))
    (home-page "https://github.com/AshAmetrine/ziglibs-ini")
    (synopsis "INI parser for Zig")
    (description "A small INI file parser for Zig (ly's fork, for Zig 0.16).")
    (license license:expat)))

(define zig-zigini-for-ly
  (package
    (name "zig-zigini")
    (version "0.5.0-a665d08")
    (source
     (origin
       (inherit (zig-source name version "https://github.com/AshAmetrine/zigini"
                            "a665d081dda42664a96da2840ea09c5ccf9d0692"
                            "1zq2ywk3ansxbhvnfjja602x09d0dpcbkpza6k2kl5chaf42fg7k"))
       (snippet (rename-zig-dependencies '(("ini" . "zig-ini"))))))
    (build-system zig-build-system)
    (arguments (list #:zig zig-0.16 #:tests? #f))
    (propagated-inputs (list zig-ini-for-ly))
    (home-page "https://github.com/AshAmetrine/zigini")
    (synopsis "INI files to and from Zig structs")
    (description "Reads and writes INI files as Zig structs (used by ly).")
    (license license:expat)))

(define zig-termbox2-for-ly
  (package
    (name "zig-termbox2")
    (version "2.5.0-c7f241e")
    (source (zig-source name version "https://github.com/AnErrupTion/termbox2"
                        "c7f241e8888ce243e1748b05c26a42fcfaaad936"
                        "1c0ir2n7b67w7b8a3rz3chvd3pvcsbc2njknjb3s0v1cpvk3nl7f"))
    (build-system zig-build-system)
    ;; a single C header: nothing to build, only the source to hand to ly
    (arguments (list #:zig zig-0.16 #:tests? #f #:skip-build? #t))
    (home-page "https://github.com/AnErrupTion/termbox2")
    (synopsis "Terminal rendering library (ly's fork of termbox2)")
    (description "termbox2, a header-only library for text user interfaces.")
    (license license:expat)))

(define-public ly
  (package
    (name "ly")
    (version "1.4.1")
    (source
     (origin
       (inherit (zig-source name version "https://github.com/fairyglade/ly"
                            "afb1dc62a0568743c9a7952623ec179128c73340"
                            "10p0i18s98l90yffnrla5as7ddss4nc95i758bjyl9iil19d488n"))
       (snippet
        #~(begin
            #$(rename-zig-dependencies '(("clap" . "zig-clap")))
            #$(rename-zig-dependencies '(("termbox2" . "zig-termbox2")
                                         ("translate_c" . "zig-translate-c"))
                                       '("ly-ui"))
            #$(rename-zig-dependencies '(("zigini" . "zig-zigini")
                                         ("translate_c" . "zig-translate-c"))
                                       '("ly-core"))
            (use-modules (guix build utils))
            ;; build.zig also imports translate-c by name
            (substitute* (find-files "." "^build\\.zig$")
              (("@import\\(\"translate_c\"\\)") "@import(\"zig-translate-c\")"))))))
    (build-system zig-build-system)
    (arguments
     (list
      #:zig zig-0.16
      #:tests? #f
      #:install-source? #f
      #:zig-release-type "safe"
      ;; ly translates C headers (PAM, XCB) itself: tell it where they are
      #:zig-build-flags
      #~(list "-Ddefault_tty=1" "-Denable_x11_support=true"
              "--search-prefix" #$(this-package-input "linux-pam")
              "--search-prefix" #$(this-package-input "libxcb"))
      #:phases
      #~(modify-phases %standard-phases
          (add-after 'install 'install-files
            (lambda _
              ;; what ly's own "installexe" step would put in /etc: Rassvet's system
              ;; configuration installs them there from here (share/ly)
              (let ((share (string-append #$output "/share/ly")))
                (mkdir-p share)
                (for-each (lambda (f) (install-file f share))
                          '("res/config.ini" "res/setup.sh" "res/startup.sh"))
                (copy-recursively "res/lang" (string-append share "/lang"))
                (copy-recursively "res/pam.d" (string-append share "/pam.d"))))))))
    (inputs (list linux-pam libxcb))
    (native-inputs (list zig-clap-for-ly zig-termbox2-for-ly zig-translate-c zig-zigini-for-ly))
    (home-page "https://github.com/fairyglade/ly")
    (synopsis "Console login manager")
    (description "Ly is a lightweight text-mode login manager: a box on a virtual
console where you pick a session and type your password.")
    (license license:wtfpl2)))


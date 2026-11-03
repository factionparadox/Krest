;;; Рассвет / Rassvet: the USB stick. Guix's own installation system (the same live system
;;; the official ISO boots), with Nonguix's kernel and firmware so Wi-Fi and everything else
;;; on the Framework work, and Rassvet's installer on tty1 in place of Guix's.
;;;
;;; build/build-iso.sh builds it with
;;;   guix time-machine -C channels.scm -- system image -t iso9660 -L guix guix/rassvet/installer.scm
;;; and then adds the system archive (every package of the installed system) to the ISO, so
;;; installing needs no network.
(define-module (rassvet installer)
  #:use-module (gnu)
  #:use-module (gnu system)
  #:use-module (gnu system install)
  #:use-module (gnu services base)
  #:use-module (gnu packages admin)
  #:use-module (gnu packages bash)
  #:use-module (gnu packages compression)
  #:use-module (gnu packages disk)
  #:use-module (gnu packages ncurses)
  #:use-module (gnu packages linux)
  #:use-module (gnu packages python)
  #:use-module (gnu packages tls)
  #:use-module (guix gexp)
  #:use-module (guix packages)
  #:use-module (guix build-system trivial)
  #:use-module ((guix licenses) #:prefix license:)
  #:use-module (nongnu packages linux)
  #:use-module (nongnu system linux-initrd)
  #:use-module (rassvet packages)
  #:use-module (srfi srfi-1)
  #:export (rassvet-installation-os))

;; Rassvet's channel and Nonguix, exactly as the system in the archive was built from them:
;; the installer's "guix system init" loads (rassvet system) from here.
(define nonguix-source
  ;; where the nongnu modules were loaded from (guix time-machine's Nonguix checkout)
  (let ((file (canonicalize-path (search-path %load-path "nongnu/packages/linux.scm"))))
    (local-file (dirname (dirname (dirname file))) "nonguix-channel" #:recursive? #t
                #:select? (lambda (name stat)
                            (not (string-suffix? ".go" name))))))

(define rassvet-source
  (local-file (rassvet-file) "rassvet-channel" #:recursive? #t
              #:select? (lambda (name stat)
                          (not (or (string-contains name "/.git")
                                   (string-contains name "/build/work")
                                   (string-contains name "/out/")
                                   (string-contains name "/local/")
                                   (string-suffix? ".go" name)
                                   (string-contains name "__pycache__"))))))

(define rassvet-installer
  (package
    (name "rassvet-installer")
    (version "0.2")
    (source #f)
    (build-system trivial-build-system)
    (arguments
     (list
      #:modules '((guix build utils))
      #:builder
      #~(begin
          (use-modules (guix build utils))
          (let* ((bin (string-append #$output "/bin"))
                 (share (string-append #$output "/share/rassvet-installer"))
                 (script (string-append share "/rassvet-install.py")))
            (mkdir-p bin)
            (mkdir-p share)
            (copy-file #$(local-file (rassvet-file "installer/rassvet-install.py") "rassvet-install.py") script)
            (symlink #$nonguix-source (string-append share "/nonguix"))
            (symlink #$rassvet-source (string-append share "/rassvet"))
            ;; the installer, with everything it calls on its PATH
            (call-with-output-file (string-append bin "/rassvet-installer")
              (lambda (port)
                (format port "#!/bin/sh
export PATH=~a:/run/current-system/profile/bin:/run/current-system/profile/sbin
export RASSVET_CHANNELS=~a TERM=${TERM:-linux}
exec ~a ~a \"$@\"
"
                        (string-join
                         (map (lambda (p) (string-append p "/bin"))
                              (list #$dialog #$gptfdisk #$parted #$xfsprogs
                                    #$dosfstools #$util-linux #$zstd #$openssl))
                         ":")
                        share #$(file-append python "/bin/python3") script)))
            (chmod (string-append bin "/rassvet-installer") #o755)))))
    (home-page "https://github.com/factionparadox/Pustota")
    (synopsis "Rassvet's installer")
    (description "Installs Rassvet (Guix System with Rassvet's desktop) on a whole disk,
offline, from the system archive on the USB stick.")
    (license license:gpl3+)))

;; tty1: Rassvet's installer, then a shell if you leave it
(define rassvet-installer-login
  (program-file "rassvet-installer-login"
    #~(begin
        (system* #$(file-append rassvet-installer "/bin/rassvet-installer"))
        (execl #$(file-append bash "/bin/bash") "bash" "--login"))))

(define rassvet-installation-os
  (let ((base (make-installation-os #:efi-only? #t)))
    (operating-system
      (inherit base)
      (host-name "rassvet")
      (timezone "Europe/London")
      (locale "en_GB.utf8")
      (label "Rassvet installer")
      (kernel linux)
      (initrd microcode-initrd)
      (firmware (list linux-firmware))
      (kernel-arguments '("quiet"))
      (packages (cons rassvet-installer (operating-system-packages base)))
      (services
       (cons*
        ;; archives exported by the build machine are signed with its key
        (simple-service 'rassvet-archive-key guix-service-type
                        (guix-extension
                         (authorized-keys
                          (list (local-file (or (getenv "RASSVET_SIGNING_KEY")
                                                "/etc/guix/signing-key.pub")
                                            "build-machine-signing-key.pub")))))
        (modify-services (operating-system-user-services base)
          (kmscon-service-type
           config => (kmscon-configuration
                      (inherit config)
                      (login-program rassvet-installer-login)))))))))

rassvet-installation-os

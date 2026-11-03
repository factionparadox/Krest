;; The system build/build-iso.sh puts on the stick (answers do not matter: the installer
;; writes your own /etc/config.scm; this one only fixes what is built in advance).
(use-modules (rassvet system))
(rassvet-operating-system
  #:host-name "rassvet"
  #:user "stephen"
  #:full-name "Stephen"
  #:autologin? #t
  #:efi-uuid "1234-ABCD"
  #:root-uuid "11111111-2222-3333-4444-555555555555"
  #:swap-uuid "66666666-7777-8888-9999-000000000000")

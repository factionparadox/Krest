;; A second set of answers, all different from template-config.scm: building it shows what
;; a laptop must build for itself at install time (build/offline-items.py).
(use-modules (rassvet system))
(rassvet-operating-system
  #:host-name "variant-host"
  #:user "variantuser"
  #:full-name ""
  #:timezone "America/New_York"
  #:autologin? #f
  #:efi-uuid "ABCD-1234"
  #:root-uuid "99999999-8888-7777-6666-555555555555"
  #:swap-uuid "12121212-3434-5656-7878-909090909090")

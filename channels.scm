;; The exact Guix and Nonguix that Rassvet is built from. build/build-iso.sh uses this file:
;;   guix time-machine -C channels.scm -- system image ...
;; Both channels are authenticated: Guix checks every commit against the signing keys
;; introduced below, so a tampered mirror is refused. To move to newer ones, change the two
;; commits (guix describe on an up-to-date system shows them) and build again.
(list (channel
        (name 'guix)
        (url "https://codeberg.org/guix/guix.git")
        (branch "master")
        (commit "dda299a16d352a68f3c9bbc59d8deebc150f395b")
        (introduction
         (make-channel-introduction
          "9edb3f66fd807b096b48283debdcddccfea34bad"
          (openpgp-fingerprint
           "BBB0 2DDF 2CEA F6A8 0D1D  E643 A2A0 6DF2 A33A 54FA"))))
      (channel
        (name 'nonguix)
        (url "https://gitlab.com/nonguix/nonguix")
        (branch "master")
        (commit "63d83b22615e7a97a4fb0c3d9f6419e9a7fc4fe0")
        (introduction
         (make-channel-introduction
          "897c1a470da759236cc11798f4e0a5f7d4d59fbc"
          (openpgp-fingerprint
           "2A39 3FFF 68F4 EF7A 3D29  12AF 6F51 20A0 22FB B2D5")))))

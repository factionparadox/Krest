;;; Рассвет / Rassvet: the whole system, as one Guix operating system.
;;;
;;; The installer writes /etc/config.scm, a few lines that call rassvet-operating-system with
;;; your disk's UUIDs, your name and your choices. Everything else is here. After a change:
;;;   sudo guix system reconfigure /etc/config.scm      (a new generation; the old one stays)
;;;   sudo guix system roll-back                        (back to the previous generation)
;;; GRUB lists every generation, so a bad one is never more than a reboot away.
(define-module (rassvet system)
  #:use-module (gnu)
  #:use-module (gnu system)
  #:use-module (gnu system keyboard)
  #:use-module (gnu system locale)
  #:use-module (gnu bootloader grub)
  #:use-module (gnu system pam)
  #:use-module (gnu system setuid)
  #:use-module (gnu services base)
  #:use-module (gnu services dbus)
  #:use-module (gnu services desktop)
  #:use-module (gnu services linux)
  #:use-module (gnu services networking)
  #:use-module (gnu services pm)
  #:use-module (gnu services authentication)
  #:use-module (gnu services xorg)
  #:use-module (gnu services sound)
  #:use-module (gnu services shepherd)
  #:use-module (gnu packages machine-learning)
  #:use-module (gnu packages)
  #:use-module (gnu packages admin)
  #:use-module (gnu packages freedesktop)
  #:use-module (gnu packages linux)
  #:use-module (gnu packages xorg)
  #:use-module (gnu packages suckless)
  #:use-module (guix gexp)
  #:use-module (guix channels)
  #:use-module (nongnu packages linux)
  #:use-module (nongnu system linux-initrd)
  #:use-module (rassvet packages)
  #:use-module (srfi srfi-1)
  #:export (rassvet-operating-system
            %rassvet-packages
            %rassvet-channels
            %rassvet-keyboard
            rassvet-xorg-configuration))

;; British keyboard with Russian phonetic (я on q, в on w, ж on v); Alt+Shift switches.
(define %rassvet-keyboard
  (keyboard-layout "gb,ru" ",phonetic" #:options '("grp:alt_shift_toggle")))

(define %intel-and-touchpad "
Section \"Device\"
    Identifier \"Rassvet Intel\"
    Driver \"modesetting\"
    Option \"TearFree\" \"true\"
EndSection
Section \"InputClass\"
    Identifier \"Rassvet touchpad\"
    MatchIsTouchpad \"on\"
    Driver \"libinput\"
    Option \"Tapping\" \"on\"
    Option \"NaturalScrolling\" \"true\"
    Option \"DisableWhileTyping\" \"true\"
    Option \"ClickMethod\" \"clickfinger\"
EndSection
")

(define rassvet-xorg-configuration
  (xorg-configuration
   (keyboard-layout %rassvet-keyboard)
   (extra-config (list %intel-and-touchpad))))

;; Where updates come from: Guix, Nonguix and Rassvet itself (this repository).
(define %rassvet-channels
  (list (channel
          (name 'guix)
          (url "https://codeberg.org/guix/guix.git")
          (branch "master")
          (introduction
           (make-channel-introduction
            "9edb3f66fd807b096b48283debdcddccfea34bad"
            (openpgp-fingerprint
             "BBB0 2DDF 2CEA F6A8 0D1D  E643 A2A0 6DF2 A33A 54FA"))))
        (channel
          (name 'nonguix)
          (url "https://gitlab.com/nonguix/nonguix")
          (branch "master")
          (introduction
           (make-channel-introduction
            "897c1a470da759236cc11798f4e0a5f7d4d59fbc"
            (openpgp-fingerprint
             "2A39 3FFF 68F4 EF7A 3D29  12AF 6F51 20A0 22FB B2D5"))))
        (channel
          (name 'rassvet)
          (url "https://github.com/factionparadox/Pustota")
          (branch "main"))))

(define %rassvet-packages
  (append
   (list x-terminal ly rassvet-desktop rassvet-learn rassvet-russian)
   (map specification->package
        '(;; X11 and Intel graphics (video decoding: Intel's media driver, from Nonguix)
          "xinit" "xauth" "xrdb" "xset" "xsetroot" "xprop" "xinput" "xdpyinfo" "xrandr"
          "setxkbmap" "mesa" "intel-media-driver-nonfree" "libva-utils"
          ;; the desktop: ratpoison, polybar, dmenu, notifications, the screen lock
          "ratpoison" "polybar" "dmenu" "dunst" "libnotify" "xss-lock" "xbanish" "xclip"
          "xsel" "maim" "xterm" "feh" "clipmenu" "clipnotify" "redshift"
          ;; fingerprint reader, passwords for programs
          "fprintd" "gnome-keyring"
          ;; battery, heat, Bluetooth, network and sound in the terminal
          "powertop" "brightnessctl" "bluez" "network-manager" "iw" "pipewire"
          "wireplumber" "pamixer" "pulsemixer" "alsa-utils"
          ;; disks
          "xfsprogs" "dosfstools" "exfatprogs" "ntfs-3g" "udiskie"
          ;; fonts: Latin, Cyrillic, Japanese (reading), Go Mono for X-терминал
          "font-dejavu" "font-google-noto" "font-google-noto-emoji" "font-terminus"
          "font-ibm-plex" "font-go" "font-ipa" "font-ipa-mj-mincho"
          ;; writing, files and Plan 9
          "mc" "neovim" "plan9port" "texinfo"
          "libreoffice" "hunspell-dict-en-gb"
          ;; everyday programs (Firefox and Steam from Nonguix)
          "firefox" "steam" "mpv" "yt-dlp" "ffmpeg" "zathura" "zathura-pdf-poppler"
          "htop" "openssh" "nftables" "fwupd" "fastfetch-minimal" "ani-cli" "aria2" "fzf" "git" "curl"
          "wget" "rsync" "unzip" "gnupg" "xdg-utils" "tzdata" "man-pages"
          ;; the Russian kit's runtime (its material downloads later)
          "python" "kiwix-tools" "espeak-ng" "llama-cpp"))
   %base-packages))

;; The Russian kit's AI tutor: llama.cpp's server, on this computer only (127.0.0.1), running as
;; nobody. It starts at boot once rassvet-content has downloaded the model, and not before.
(define %tutor-model "/var/lib/rassvet/russian/tutor/tutor.gguf")

(define rassvet-tutor-service
  (simple-service
   'rassvet-tutor shepherd-root-service-type
   (list (shepherd-service
          (provision '(rassvet-tutor))
          (requirement '(user-processes loopback))
          (documentation "The Russian tutor's language model (llama.cpp's llama-server).")
          (start #~(lambda args
                     (and (file-exists? #$%tutor-model)
                          (apply
                           (make-forkexec-constructor
                            (list #$(file-append llama-cpp "/bin/llama-server")
                                  "--model" #$%tutor-model "--alias" "qwen3.6-35b-a3b"
                                  "--host" "127.0.0.1" "--port" "11434"
                                  "--jinja" "--ctx-size" "16384")
                            #:user "nobody" #:group "nogroup"
                            #:log-file "/var/log/rassvet-tutor.log")
                           args))))
          (stop #~(make-kill-destructor))
          (respawn? #f)))))

;; ly's settings: Rassvet's look (black, white, red), and the paths of
;; this system. ly keeps its defaults for anything not listed.
(define (ly-config autologin-user)
  (mixed-text-file "ly-config.ini"
   "animation = none\n"
   "bg = 0x00000000\n"
   "fg = 0x00FFFFFF\n"
   "border_fg = 0x00CC0000\n"
   "error_fg = 0x01FF3333\n"
   "box_title = РАССВЕТ\n"
   "clock = %a %d %b  %H:%M\n"
   "hide_version_string = true\n"
   "default_input = password\n"
   "xinitrc = null\n"
   "waylandsessions = null\n"
   "xsessions = /run/current-system/profile/share/xsessions\n"
   "x_cmd = " (xorg-wrapper rassvet-xorg-configuration) "\n"
   "xauth_cmd = " xauth "/bin/xauth\n"
   "setup_cmd = /etc/ly/setup.sh\n"
   "path = /run/setuid-programs:/run/current-system/profile/bin:/run/current-system/profile/sbin\n"
   "shutdown_cmd = /run/current-system/profile/sbin/shutdown\n"
   "restart_cmd = /run/current-system/profile/sbin/reboot\n"
   "brightness_down_cmd = /run/current-system/profile/bin/brightnessctl -q -n s 10%-\n"
   "brightness_up_cmd = /run/current-system/profile/bin/brightnessctl -q -n s +10%\n"
   (if autologin-user
       (string-append "auto_login_user = " autologin-user "\n"
                      "auto_login_session = rassvet\n")
       "")))

;; setup.sh with this system's paths (ly runs it to start each session)
(define ly-setup
  (computed-file "ly-setup.sh"
    (with-imported-modules '((guix build utils))
      #~(begin
          (use-modules (guix build utils))
          (copy-file #$(file-append ly "/share/ly/setup.sh") #$output)
          (substitute* #$output (("\\$CONFIG_DIRECTORY") "/etc"))
          (chmod #$output #o755)))))

(define (rassvet-etc autologin-user)
  `(("rassvet/ratpoisonrc" ,(file-append rassvet-desktop "/share/rassvet/etc/ratpoisonrc"))
    ("rassvet/Xresources" ,(file-append rassvet-desktop "/share/rassvet/etc/Xresources"))
    ("rassvet/polybar.ini" ,(file-append rassvet-desktop "/share/rassvet/etc/polybar.ini"))
    ;; Firefox: uBlock Origin offered on first start, hardware video decoding
    ("firefox/policies/policies.json"
     ,(file-append rassvet-desktop "/share/rassvet/firefox/policies/policies.json"))
    ("ly/config.ini" ,(ly-config autologin-user))
    ("ly/setup.sh" ,ly-setup)
    ("ly/lang" ,(file-append ly "/share/ly/lang"))
    ;; the Framework Laptop's USB-C charger driver would wake the laptop; Realtek Ethernet
    ;; expansion card: let it sleep
    ("modprobe.d/rassvet-framework.conf" ,(plain-file "rassvet-framework.conf"
                                                     "blacklist cros_usbpd_charger\n"))
    ("NetworkManager/conf.d/50-rassvet-wifi-powersave.conf"
     ,(plain-file "wifi-powersave.conf" "[connection]\nwifi.powersave = 3\n"))
    ("profile.d/rassvet.sh"
     ,(plain-file "rassvet.sh" "export EDITOR=mcedit VISUAL=mcedit
export LIBVA_DRIVER_NAME=iHD          # Intel video decoding in Firefox and mpv
export MOZ_USE_XINPUT2=1              # smooth touchpad scrolling in Firefox
"))))

;; The firewall: everything coming in is dropped unless it answers something this laptop asked
;; for; everything going out is allowed.
(define %rassvet-nftables
  (plain-file "rassvet-nftables.conf" "
flush ruleset
table inet rassvet {
  chain input {
    type filter hook input priority 0; policy drop;
    ct state { established, related } accept
    ct state invalid drop
    iif lo accept
    meta l4proto { icmp, ipv6-icmp } accept
    udp dport 5353 accept comment \"mDNS\"
  }
  chain forward { type filter hook forward priority 0; policy drop; }
  chain output { type filter hook output priority 0; policy accept; }
}
"))

(define (ly-pam-services)
  (list (unix-pam-service "ly" #:login-uid? #t #:allow-empty-passwords? #f)
        ;; automatic login: no password asked, the rest exactly as a normal login
        (pam-service
         (inherit (unix-pam-service "ly-autologin" #:login-uid? #t))
         (auth (list (pam-entry (control "required") (module "pam_permit.so")))))))

;; sudo and the screen lock accept an enrolled finger (fprintd-enroll) before asking for the
;; password; with no finger enrolled, or no reader, they go straight to the password.
(define %fingerprint-pam
  (pam-extension
   (transformer
    (lambda (pam)
      (if (member (pam-service-name pam) '("sudo" "slock"))
          (pam-service
           (inherit pam)
           (auth (cons (pam-entry
                        (control "sufficient")
                        (module (file-append fprintd "/lib/security/pam_fprintd.so")))
                       (pam-service-auth pam))))
          pam)))))

(define* (rassvet-operating-system
          #:key
          (host-name "rassvet")
          (user "rassvet")
          (full-name "")
          (timezone "Europe/London")
          (locale "en_GB.utf8")
          (autologin? #f)
          efi-uuid root-uuid swap-uuid
          (root-type "xfs"))
  "The Rassvet system for one laptop. EFI-UUID, ROOT-UUID and SWAP-UUID are the
partitions' UUIDs (strings); SWAP-UUID may be #f (no swap, so no hibernation)."
  (operating-system
    (host-name host-name)
    (timezone timezone)
    (locale locale)
    (locale-definitions
     (list (locale-definition (name "en_GB.utf8") (source "en_GB"))
           (locale-definition (name "en_US.utf8") (source "en_US"))
           (locale-definition (name "ru_RU.utf8") (source "ru_RU"))))
    (keyboard-layout %rassvet-keyboard)

    ;; Nonguix: the full Linux kernel (with every driver this laptop needs), its firmware and
    ;; the Intel microcode
    (kernel linux)
    (initrd microcode-initrd)
    (firmware (list linux-firmware sof-firmware))   ; sof: the Intel audio DSP
    ;; nvme.noacpi=1: the Framework's SSD uses less power, also while suspended (from
    ;; nixos-hardware's Framework 13 Intel settings); resume: hibernation
    (kernel-arguments
     (append (list "nvme.noacpi=1")
             (if swap-uuid (list (string-append "resume=UUID=" swap-uuid)) '())
             %default-kernel-arguments))

    (bootloader
     (bootloader-configuration
      (bootloader grub-efi-bootloader)
      (targets '("/boot/efi"))
      (timeout 3)
      (keyboard-layout %rassvet-keyboard)
      (theme (grub-theme
              (inherit (grub-theme))
              (color-normal '((fg . light-gray) (bg . black)))
              (color-highlight '((fg . white) (bg . red)))))))

    (file-systems
     (cons* (file-system
              (mount-point "/")
              (device (uuid root-uuid (string->symbol root-type)))
              (type root-type))
            (file-system
              (mount-point "/boot/efi")
              (device (uuid efi-uuid 'fat32))
              (type "vfat"))
            %base-file-systems))
    (swap-devices
     (if swap-uuid
         (list (swap-space (target (uuid swap-uuid))))
         '()))

    (users
     (cons (user-account
             (name user)
             (comment full-name)
             (group "users")
             (supplementary-groups
              '("wheel" "netdev" "audio" "video" "input" "lp" "kvm")))
           %base-user-accounts))
    ;; the home-folder files every new account starts with (.xinitrc, .ratpoisonrc ...)
    (skeletons
     (let ((ours (map (lambda (name)
                        (list name (file-append rassvet-desktop "/share/rassvet/skel/" name)))
                      '(".bash_profile" ".bashrc" ".xinitrc" ".ratpoisonrc"
                        ".config/polybar/config.ini" ".config/dunst/dunstrc"
                        ".config/mpv/mpv.conf"))))
       ;; Guix's own defaults, except where Rassvet has its own file of the same name
       (append ours
               (remove (lambda (entry) (assoc (car entry) ours)) (default-skeletons)))))

    (packages %rassvet-packages)

    (services
     (append
      (list
       ;; ly on tty1: the login screen (agetty hands the console to ly instead of login)
       (service agetty-service-type
                (agetty-configuration
                 (tty "tty1")
                 (login-program (file-append ly "/bin/ly"))
                 (skip-login? #t)
                 (no-clear? #t)))
       (simple-service 'rassvet-ly-pam pam-root-service-type (ly-pam-services))
       (simple-service 'rassvet-fingerprint pam-root-service-type (list %fingerprint-pam))
       (simple-service 'rassvet-etc etc-service-type (rassvet-etc (and autologin? user)))

       ;; sessions, suspend and hibernation
       (service elogind-service-type
                (elogind-configuration
                 (handle-lid-switch (if swap-uuid 'suspend-then-hibernate 'suspend))
                 (handle-lid-switch-external-power 'suspend)
                 (handle-power-key 'suspend)
                 (hibernate-delay-seconds 7200)))
       (service dbus-root-service-type)
       (service polkit-service-type)
       (service upower-service-type)
       (service udisks-service-type)
       (service x11-socket-directory-service-type)
       (service screen-locker-service-type
                (screen-locker-configuration
                 (name "slock")
                 (program (file-append slock "/bin/slock"))))
       (service gnome-keyring-service-type)
       (service fprintd-service-type)

       ;; network, Bluetooth, time, firewall
       (service network-manager-service-type)
       (service wpa-supplicant-service-type)
       (service bluetooth-service-type)
       (service ntp-service-type)
       (service nftables-service-type
                (nftables-configuration (ruleset %rassvet-nftables)))

       ;; battery and heat: tlp (Intel's energy-performance hints, low-power platform
       ;; profile and Wi-Fi power saving on battery), thermald, compressed swap in RAM,
       ;; earlyoom, weekly TRIM for the SSD
       (service tlp-service-type
                (tlp-configuration
                 (cpu-energy-perf-policy-on-ac "balance_performance")
                 (cpu-energy-perf-policy-on-bat "power")
                 (platform-profile-on-ac "balanced")
                 (platform-profile-on-bat "low-power")
                 (wifi-pwr-on-bat? #t)))
       (service thermald-service-type)
       (service zram-device-service-type
                (zram-device-configuration
                 (size "16G")
                 (compression-algorithm 'zstd)
                 (priority 100)))
       (service earlyoom-service-type)
       rassvet-tutor-service
       (service fstrim-service-type)

       ;; the Realtek Ethernet expansion card: let it sleep when idle
       (udev-rules-service 'rassvet-framework
                           (udev-rule "50-rassvet-framework.rules"
                                      "ACTION==\"add\", SUBSYSTEM==\"usb\", ATTR{idVendor}==\"0bda\", ATTR{idProduct}==\"8156\", ATTR{power/autosuspend}=\"20\"\n"))
       ;; Steam's Proton opens many files per game
       (service pam-limits-service-type
                (list (pam-limits-entry "*" 'both 'nofile 524288))))

      ;; Guix's base services, without the plain login on tty1 (ly has it) and with Nonguix's
      ;; substitutes (prebuilt packages) beside Guix's own
      (modify-services
          (remove (lambda (s)
                    (and (eq? (service-kind s) mingetty-service-type)
                         (string=? "tty1" (mingetty-configuration-tty (service-value s)))))
                  %base-services)
        (guix-service-type
         config => (guix-configuration
                    (inherit config)
                    (channels %rassvet-channels)
                    (substitute-urls
                     (append (list "https://substitutes.nonguix.org")
                             %default-substitute-urls))
                    (authorized-keys
                     (append (list (local-file (rassvet-file "guix/rassvet/files/nonguix-signing-key.pub")
                                             "nonguix-signing-key.pub"))
                             %default-authorized-guix-keys)))))))))

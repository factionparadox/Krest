# The system declaration

On Guix System the whole operating system is one Scheme value: an operating-system record
naming the kernel, boot loader, file systems, users, packages and services. Guix builds it into
/gnu/store, and "switching to it" means pointing /run/current-system at the result, writing
/etc and the GRUB menu, and telling Shepherd about the services. Nothing is installed or
configured by hand in between, so the declaration is always the truth.

## Rassvet's two files
  /etc/config.scm            this laptop. The installer wrote it: a few lines calling
                             rassvet-operating-system with your choices
  (rassvet system)           everything else: guix/rassvet/system.scm in Rassvet's channel,
                             arriving with guix pull

rassvet-operating-system takes these keywords (the defaults in brackets):
  #:host-name ["rassvet"]  #:user ["rassvet"]  #:full-name [""]
  #:timezone ["Europe/London"]  #:locale ["en_GB.utf8"; also en_US.utf8, ru_RU.utf8]
  #:autologin? [#f]  #:efi-uuid  #:root-uuid  #:swap-uuid [#f: no swap, no hibernation]
  #:root-type ["xfs"]
Change one in /etc/config.scm (sudoedit /etc/config.scm), then reconfigure.

## Reconfigure and generations
  sudo guix system reconfigure /etc/config.scm   build and switch to a new generation
  guix system build /etc/config.scm              build only: check it before switching
  guix system list-generations                   every generation, the current one marked
  sudo guix system roll-back                     back to the previous one
  sudo guix system switch-generation 12          to any one
  sudo guix system delete-generations 2m         drop those older than two months
  sudo guix gc                                   then free what only they used
GRUB lists every generation that has not been deleted. A reconfigure with an error in the file
stops before changing anything and says where the error is.

rassvet-update is guix pull followed by the reconfigure, as you (the pulled guix), so a new
Rassvet arrives the same way as a change of your own.

## Changing more than the keywords
Wrap Rassvet's system and change the fields you want: inherit takes everything else from it.
Keep the installer's call as it is, and give it a name:

  (use-modules (gnu) (rassvet system))
  (use-service-modules pm ssh)

  (define base
    (rassvet-operating-system #:host-name "rassvet" #:user "you" ...))   ; the installer's lines

  (operating-system
    (inherit base)
    (packages (cons (specification->package "gimp")
                    (operating-system-packages base)))
    (kernel-arguments (cons "loglevel=3"
                            (operating-system-user-kernel-arguments base)))
    (services
     (cons (service openssh-service-type)                  ; an ssh server
           (modify-services (operating-system-user-services base)
             (tlp-service-type config =>                   ; one tlp setting changed
               (tlp-configuration (inherit config) (cpu-boost-on-bat? #f)))))))

modify-services changes a service's configuration; remove (from SRFI-1) with service-kind takes
one away. Every service type, field and default is in the Guix manual: info "(guix) Services";
guix system search WORD finds service types.

## /etc
Most of /etc is generated: files from the declaration are links into /etc/static, itself a
link into the store, and they are rewritten on every reconfigure and boot. What stays yours:
/etc/config.scm, the passwords in /etc/shadow, NetworkManager's saved connections, and other
state programs keep there.

See also: shepherd, boot, channels, guix-packages ; info "(guix) System Configuration" ;
info "(guix) Invoking guix system" ; info "(guix) operating-system Reference"

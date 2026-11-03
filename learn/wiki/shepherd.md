# Shepherd

GNU Shepherd is Guix System's init and service manager: process 1, the program that starts
everything else, restarts services that die (when they are set to) and shuts the machine down.
It is written in Guile Scheme, like Guix, and its services are Scheme objects that Guix
generates from the operating system declaration. herd is the command that talks to it.

## Services are declared, not enabled
There is no folder of links and no "enable": a service runs because the operating system lists
it. Guix's service types (network-manager-service-type, tlp-service-type ...) each turn a
configuration record into one or more Shepherd services, plus whatever else they need: files in
/etc, accounts, PAM entries, D-Bus or udev rules. To add, remove or change a service, change
/etc/config.scm (see: system) and reconfigure; the previous generation keeps the old set.

## herd
  sudo herd status                 every service: started (+), stopped (-), with a summary
  sudo herd status NAME            one service: its state, process, dependencies and recent
                                   messages from its log
  sudo herd start NAME             start (and what it requires)
  sudo herd stop NAME              stop (and what depends on it)
  sudo herd restart NAME           stop and start
  sudo herd doc NAME               what the service is for
  sudo herd schedule mcron         the scheduled jobs and when they next run (see: time)
herd's changes last until the next boot or reconfigure. A reconfigure starts services that
are new and updates stopped ones, but leaves running ones alone: restart them (or reboot) to
run their new version.

Without sudo, herd talks to your own Shepherd, if you run one (Guix Home does); Rassvet does
not start one, so plain herd status says it cannot connect.

## A real service: the tutor
system.scm declares rassvet-tutor like this:

  (simple-service 'rassvet-tutor shepherd-root-service-type
   (list (shepherd-service
          (provision '(rassvet-tutor))
          (requirement '(user-processes loopback))
          (documentation "The Russian tutor's language model (llama.cpp's llama-server).")
          (start #~(lambda args
                     (and (file-exists? "/var/lib/rassvet/russian/tutor/tutor.gguf")
                          (apply (make-forkexec-constructor
                                  (list #$(file-append llama-cpp "/bin/llama-server") ...)
                                  #:user "nobody" #:group "nogroup"
                                  #:log-file "/var/log/rassvet-tutor.log")
                                 args))))
          (stop #~(make-kill-destructor))
          (respawn? #f))))

- provision is its name; requirement, what must be up first (Shepherd orders the boot from these).
- start is code Shepherd runs: here it does nothing until the model exists, then starts the
  server in the foreground as nobody, its output into a log file.
- make-forkexec-constructor and make-kill-destructor are Shepherd's ordinary start and stop.
- respawn? #f: if it exits, it stays down (the default is to restart it).
The same shape, in /etc/config.scm's services, gives you a service of your own.

## Rassvet's services
From system.scm: elogind, dbus, NetworkManager, wpa-supplicant, bluetooth, ntpd, nftables,
tlp, thermald, a zram device, earlyoom, rassvet-tutor, ly on tty1 (through agetty), and mcron
for the weekly fstrim. From Guix's base services: udev, guix-daemon, nscd, the system log,
the file systems and swap, the other consoles (tty2 to tty6), urandom-seed and more.
polkit, upower, udisks and fprintd are started by D-Bus when something asks for them, so herd
does not list them.

## Shutting down
  loginctl poweroff ; loginctl reboot     through elogind (works for you in your session)
  sudo shutdown ; sudo reboot             Shepherd's own (halt and reboot)

## Services for your user
Guix Home (guix home) runs a Shepherd of your own with services declared per user. Rassvet
does not use it; programs that need your X session belong in ~/.config/rassvet/autostart.

See also: system, logging, elogind ; info shepherd ; info "(guix) Services" ;
info "(guix) Shepherd Services" ; man herd ; https://www.gnu.org/software/shepherd/manual/

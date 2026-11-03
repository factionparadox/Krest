# Logging

Guix System has no journal. Messages are plain text: programs send them to syslog, the system
log service writes them into files in /var/log, and you read them with less, tail and grep.
Shepherd also keeps each service's own output, either in a log file of its own or in the
system log.

## The system log
Part of Guix's base services. Messages are sorted by kind:
  /var/log/messages          almost everything (start here): daemons, the kernel, Shepherd
  /var/log/secure            logins, sudo (authentication)
  /var/log/debug             debug-level messages, when programs send them
Reading them needs root:
  sudo tail -f /var/log/messages               follow live (Ctrl+C stops)
  sudo grep -i error /var/log/messages
  sudo less +G /var/log/messages               (the menu: System -> The log)
The files are rotated by Guix's log rotation, so the disk never fills.

## A service's own log
A Shepherd service started with #:log-file writes its output there; many of Guix's do, as
/var/log/NAME.log, and Rassvet's tutor writes /var/log/rassvet-tutor.log. The rest go to the
system log. Either way, recent lines show in
  sudo herd status NAME
  ls /var/log                                 which services have their own file
When something fails silently, its status and these lines are the first place to look.

## The kernel
  sudo dmesg                 the kernel's ring buffer since boot
  sudo dmesg -w              follow
  sudo dmesg --level=err,warn

## Other logs
  /var/log/rassvet-install.log      every command the installer ran, with its output
  /var/log/guix-daemon.log          what the Guix daemon did (builds, downloads)
  /var/log/guix/drvs/               each build's full log (guix build prints which)
  ~/.local/share/xorg/Xorg.0.log    the X server (X runs without root, so the log is yours)

See also: shepherd ; info "(guix) Base Services" ; man syslog.conf ; man dmesg

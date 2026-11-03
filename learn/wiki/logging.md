# Logging

CRUX has no journal. Messages are plain text: programs send them to syslog, the system log
daemon (sysklogd, started by /etc/rc) writes them into files in /var/log, and you read them
with less, tail and grep.

## The system log
/etc/syslog.conf decides which messages go where. The ones to know:
  /var/log/messages          almost everything (start here): daemons, the kernel, logins
Reading it needs root:
  sudo tail -f /var/log/messages               follow live (Ctrl+C stops)
  sudo grep -i error /var/log/messages
  sudo less +G /var/log/messages               (the menu: System -> The log)
  ls /var/log                                  what else is there
Old logs are rotated by a cron job, so the disk does not fill.

## A service's own log
Services started from /etc/rc.d log through syslog unless their script sends the output
elsewhere; Krest's tutor writes /var/log/krest-tutor.log. When a service fails silently,
run its script by hand to see what it says:
  sudo /etc/rc.d/NAME status
  sudo sh -x /etc/rc.d/NAME start              every command the script runs

## Builds
  /var/log/pkgbuild/NAME.log        every prt-get build's full output, one file per port,
                                    overwritten by the next build of that port
  /var/log/krest-install.log      every command the installer ran, with its output

## The kernel
  sudo dmesg                 the kernel's ring buffer since boot
  sudo dmesg -w              follow
  sudo dmesg --level=err,warn

## Other logs
  /var/log/Xorg.0.log               the X server (it runs as root, through the setuid wrapper)
  ~/.local/share/xorg-session.log   the session's output, when started with startx

See also: rc ; man syslog.conf ; man syslogd ; man dmesg

# Logging

Void has no journal. Messages are plain text: programs send them to syslog, a syslog daemon
writes them into files, and you read them with less, tail and grep.

## socklog (Pustota's syslog)
socklog-void provides two runit services, both enabled on Pustota:

  socklog-unix   listens on /dev/log, where programs send syslog messages
  nanoklogd      passes the kernel's messages (/proc/kmsg) on to syslog

Messages are sorted by facility into folders under /var/log/socklog/, each holding a
"current" file plus older rotated ones:

  /var/log/socklog/everything/current    all of it (start here)
  /var/log/socklog/kernel/current        the kernel
  /var/log/socklog/daemon/current        services (most runit services log here via vlogger)
  /var/log/socklog/secure/current        logins, sudo (authentication)
  /var/log/socklog/errors/current        only errors, from anything
  /var/log/socklog/xbps/current          what XBPS installed, updated and removed
  (also cron, debug, lpr, mail, messages, user, remote-udp, tty12)

Reading them needs root or the socklog group:

  sudo tail -f /var/log/socklog/everything/current       follow live (Ctrl+C stops)
  sudo grep -i error /var/log/socklog/everything/current
  svlogtail                                              follow everything, shorter to type
  svlogtail xbps                                         one folder
  sudo usermod -aG socklog YOU                           read without sudo (log in again)

The files rotate on their own (svlogd keeps a few of a fixed size), so the disk never fills.

## A service's own log
runit services that have a log/ folder pass their output to vlogger (into syslog, above) or to
svlogd (their own folder in /var/log/NAME). cat /etc/sv/NAME/log/run shows which. A service
with no log/ folder sends its output to the console of runsvdir, which you rarely see: when
something fails silently, run its run script by hand in a terminal (as root) to watch it.

## The kernel
  dmesg                 the kernel's ring buffer since boot (sudo dmesg if it is restricted)
  dmesg -w              follow
  dmesg --level=err,warn

## Other logs
  /var/log/pustota-install.log      every command the installer ran, with its output
  ~/.local/share/xorg-session.log   Pustota's X session (ratpoison, polybar ...)
  ~/.local/share/xorg/Xorg.0.log    the X server (rootless X writes it to your home)

See also: runit, man socklog ; man svlogd ; man vlogger ; man svlogtail ;
https://docs.voidlinux.org/config/services/logging.html

# runit

runit is Void's init system and service supervisor: process 1, the program that starts
everything else, restarts services that die and shuts the machine down. Its whole design fits
in a few small programs (runit, runsvdir, runsv, sv, chpst, svlogd), each with a short manual
page, and Void's boot scripts are plain shell you can read in /etc/runit.

## The three stages
runit (process 1) runs three scripts, one after another:

  /etc/runit/1   one-time start-up: runs every script in /etc/runit/core-services/ in
                 alphabetical order. They mount /proc, /sys, /dev and the filesystems, check
                 them, load modules, set the hostname, clock, keymap and console font (from
                 /etc/rc.conf). Your own one-off start-up scripts can go there too.
  /etc/runit/2   the long-running stage: sources /etc/rc.local (your commands to run before
                 login), then starts runsvdir, which watches a folder of services and keeps
                 each one running. The machine spends its life here.
  /etc/runit/3   shutdown: stops the services, sources /etc/rc.shutdown, syncs and unmounts.

Read them: they are shell scripts, about a page each.

## Where services live
  /etc/sv/NAME/                every service that is installed (one folder each)
  /etc/runit/runsvdir/default/ links to the services that are enabled
  /var/service                 a link to the running service folder (the "current" runlevel)

A service is enabled by putting a link to it in /var/service. runsvdir notices within five
seconds and starts it; removing the link stops it and leaves it disabled.

  sudo ln -s /etc/sv/sshd /var/service/       enable and start
  sudo rm /var/service/sshd                   stop and disable
  ls -l /var/service                          what is enabled

During an install, before runit is running, link into /etc/runit/runsvdir/default instead:
there is no /var/service yet. (Pustota's installer does exactly that.)

## A service folder
  run      required: an executable that starts the program and stays in the foreground.
           It must not fork into the background: runsv watches the process it started.
  finish   optional: runs after run exits (clean up; its exit code is ignored)
  check    optional: exits 0 when the service is really ready (used by sv check / sv -w)
  conf     Void's convention: run scripts source it, so settings live outside the script
  down     if this file exists, the service is not started at boot (sv up still starts it)
  log/     optional: a second service whose input is run's output (see Logs below)
  supervise/  runsv's state; on Void a link into /run/runit (it is runtime state)

A real run script, /etc/sv/NetworkManager/run:

  #!/bin/sh
  exec 2>&1
  sv check dbus >/dev/null || exit 1
  exec NetworkManager -n >/dev/null 2>&1

- exec 2>&1 sends errors to the same place as normal output.
- sv check dbus ... || exit 1 is how runit does dependencies: if D-Bus is not up yet, the script
  exits, and runsv simply tries again a second later. No dependency graph, no ordering file.
- exec replaces the shell with the program, so runsv's child is the daemon itself. -n is
  NetworkManager's "stay in the foreground" option; almost every daemon has one (-f, -n, -F,
  --nodaemon): look for it in the man page.
- Many Void run scripts also read a conf file first ([ -r conf ] && . ./conf) and pass $OPTS:
  that is where to put options, so an update to the run script never overwrites them.

## Controlling services: sv
  sudo sv status NAME         run: NAME: (pid 812) 3601s  running for an hour
                              down: NAME: 5s, normally up  stopped, but enabled: look at it
  sudo sv up NAME             start (and restart it if it dies)
  sudo sv down NAME           stop (and do not restart it) until sv up or reboot
  sudo sv restart NAME        stop, then start
  sudo sv once NAME           start, but do not restart it if it exits
  sudo sv reload NAME         send SIGHUP (many daemons reread their settings)
  sudo sv check NAME          wait until the check script says it is ready
  sudo sv status /var/service/*   everything

"normally up" or "normally down" tells you whether the down file is present. "want up" means
runsv is trying to start it and it keeps failing: read its log.

## Writing your own service
Example: keep a small web server for a folder running.

  sudo mkdir -p /etc/sv/share-folder
  sudo tee /etc/sv/share-folder/run <<'EOF'
  #!/bin/sh
  exec 2>&1
  exec chpst -u nobody python3 -m http.server 8000 --bind 127.0.0.1 --directory /srv/share
  EOF
  sudo chmod +x /etc/sv/share-folder/run          (xmksv share-folder makes the skeleton)
  sudo ln -s /etc/sv/share-folder /var/service/
  sudo sv status share-folder

chpst ("change process state") runs the program as another user (-u), with limits (-m memory,
-o open files) or with a folder of environment variables (-e DIR). man chpst.

## Logs
A service's output (stdout and stderr, hence exec 2>&1) is lost unless a log service reads it.
Void's services mostly use a log/run of

  #!/bin/sh
  exec vlogger -t NAME -p daemon

vlogger sends each line to syslog, which socklog writes to /var/log/socklog/ (see: logging).
Alternatively svlogd writes the service's own rotated log files:

  #!/bin/sh
  exec svlogd -tt /var/log/NAME       (mkdir /var/log/NAME first; svlogd rotates "current")

## Runlevels
A runlevel is just another folder of links in /etc/runit/runsvdir/. Void ships "default" and
"single" (rescue: only the essentials). Choose at boot by adding  single  to the kernel command
line in GRUB (press e), or switch on a running system with  sudo runsvchdir single.

## Services for your user
runsvdir can supervise a folder you own, so your own programs can be services too (the Void
Handbook's "per-user services"). Create /etc/sv/runsvdir-YOU/run:

  #!/bin/sh
  export USER=YOU HOME=/home/YOU
  groups="$(id -Gn "$USER" | tr ' ' ':')"
  exec chpst -u "$USER:$groups" runsvdir "$HOME/service"

then enable it (ln -s /etc/sv/runsvdir-YOU /var/service/) and put service folders in
~/service the same way. They start at boot, before you log in; anything that needs your X
session belongs in ~/.config/pustota/autostart instead.

## Shutting down
  loginctl poweroff ; loginctl reboot     through elogind (works for your user in the session)
  sudo poweroff ; sudo reboot ; sudo shutdown -h now   runit's own

## Pustota's services
dbus, elogind, NetworkManager, bluetoothd, tlp, thermald, chronyd, socklog-unix, nanoklogd,
zramen, earlyoom, ufw, the agetty-ttyN consoles; ollama once the tutor is installed (it ships
with a down file until then). pustota-learn learn services has what each one does.

See also: logging, elogind, man runit ; man runsvdir ; man runsv ; man sv ; man chpst ;
man svlogd ; https://docs.voidlinux.org/config/services/ ; http://smarden.org/runit/

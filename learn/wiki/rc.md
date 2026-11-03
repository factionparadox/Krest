# rc: init and services

CRUX's init is SysVinit's /sbin/init, process 1, used in the BSD style: no runlevel folders
full of links, just a handful of shell scripts you can read in a few minutes. init starts
what /etc/inittab says, respawns the consoles, and runs the shutdown scripts.

## The scripts
  /etc/inittab       the runlevels: 1 single user, 2 multi-user (the default), 0 halt, 6 reboot;
                     rc at boot, rc.multi for runlevel 2, ly on tty1 (c1), agetty on the others
  /etc/rc            boot: mounts /proc and /sys, starts udev, checks and mounts the
                     filesystems from fstab, turns on swap, sets the hostname, keymap, font
                     and timezone from rc.conf, starts the system log, loads /etc/rc.modules
  /etc/rc.multi      runlevel 2: runs /etc/rc.d/NAME start for each NAME in SERVICES, in order,
                     then /etc/rc.local
  /etc/rc.single     single-user mode: stops the services, leaves a root shell
  /etc/rc.shutdown   halt and reboot: stops SERVICES in reverse order, saves the random seed,
                     unmounts everything
  /etc/rc.local      your own commands at the end of boot
  /etc/rc.modules    modprobe lines for modules that should always load
  /etc/rc.conf       the settings (see: rc-conf)

## Services
A service is an executable script in /etc/rc.d taking start, stop, restart and, usually,
status. It runs at boot only if its name is in SERVICES in /etc/rc.conf.
  ls /etc/rc.d                         what is installed
  sudo /etc/rc.d/NAME status           is it running
  sudo /etc/rc.d/NAME start ; stop ; restart
  sudoedit /etc/rc.conf                add or remove a name in SERVICES=(...)
Order matters: a service comes after what it needs (networkmanager after dbus). Nothing
restarts a service that dies; its status says so, and start brings it back.

## A real service: the tutor
/etc/rc.d/krest-tutor, from krest-desktop:

  SSD=/sbin/start-stop-daemon
  PROG=/usr/bin/llama-server
  MODEL=/var/lib/krest/russian/tutor/tutor.gguf
  PID=/run/krest-tutor.pid
  case $1 in
  start)
  	[ -f $MODEL ] || exit 0
  	$SSD --start --background --make-pidfile --pidfile $PID --chuid nobody \
  		--startas /bin/sh -- -c "exec $PROG --model $MODEL ... >> $LOG 2>&1" ;;
  stop)    $SSD --stop --retry 10 --pidfile $PID --remove-pidfile ;;
  restart) $0 stop ; $0 start ;;
  status)  $SSD --status --pidfile $PID && echo running || echo "not running" ;;
  esac

- start-stop-daemon starts the program in the background as nobody, writes its process
  number to a pidfile, and finds it again by that pidfile to stop it or report on it.
- start does nothing until the model exists, so the service can sit in SERVICES from the
  first boot.
- Its output goes to its own log, /var/log/krest-tutor.log.
The same shape gives you a service of your own: copy it to /etc/rc.d/NAME, chmod +x, change
PROG and its arguments, and add NAME to SERVICES.

## Krest's services
SERVICES=(lo crond dbus networkmanager acpid tlp thermald bluetoothd chronyd krest-firewall
krest-tutor). acpid, tlp and thermald come from Krest's ports, krest-firewall and
krest-tutor from krest-desktop, the rest from CRUX's. CRUX's net script is not used:
NetworkManager configures the network. polkit, upower and udisks are started by D-Bus when
something asks for them, so they have no line here.

## Shutting down
  sudo poweroff ; sudo reboot          (no password: /etc/sudoers.d/krest)
  sudo shutdown -h now ; sudo init 1   halt ; single-user mode

## Services for your user
There are none at system level: programs that need your X session go in
~/.config/krest/autostart, which krest-session runs.

See also: rc-conf, logging, sleep ; man init ; man inittab ; man start-stop-daemon ;
krest-handbook

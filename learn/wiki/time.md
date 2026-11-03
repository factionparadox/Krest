# Time and scheduled jobs

## The clock: chronyd
/etc/rc.d/chronyd (in SERVICES, from CRUX's chrony port) keeps the clock right over the
network, with the servers in /etc/chrony.conf. It copes well with a laptop that sleeps and
changes networks.
  sudo /etc/rc.d/chronyd status
  chronyc tracking                  how far off the clock is, and how it is being corrected
  chronyc sources -v                the servers it uses
  date ; sudo hwclock --show
Other servers: server or pool lines in /etc/chrony.conf, then sudo /etc/rc.d/chronyd restart.
Time zone: see locale.

## Scheduled jobs: crond
crond (in SERVICES) runs crontab jobs. CRUX's root crontab runs the scripts in /etc/cron's
daily, weekly and monthly folders (log rotation among them).
  sudo crontab -l                   root's jobs
  crontab -e                        your own (also: sudo crontab -e for root's)
A line is minute, hour, day of month, month, day of week, then the command:
  30 3 * * *  rsync -a /home/you/ /media/backup/       every day at 03:30
  30 12 * * 0 /sbin/fstrim -a                          Sundays at 12:30 (root's crontab)
A job missed while the laptop was asleep or off is not run later.

## Once, later
  sleep 600 && notify-send 'Tea'     in a terminal

See also: rc, locale (time zone), filesystems (TRIM) ; man chronyc ; man chrony.conf ;
man crontab ; man crond

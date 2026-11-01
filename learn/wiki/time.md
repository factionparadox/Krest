# Time and scheduled jobs

## The clock: chrony
chronyd (a runit service) keeps the clock right over the network, gently, even with the laptop
asleep half the day.
  chronyc tracking          how far off the clock is, and how it is being corrected
  chronyc sources -v        the time servers it is using
  date ; sudo hwclock --show
Settings: /etc/chrony.conf (servers: pool lines). rc.conf's HARDWARECLOCK="UTC" says what the
hardware clock keeps.

## Scheduled jobs: there is no cron
Void installs no cron daemon; choose one if you want scheduled jobs. The common ones:

  snooze     the smallest: one runit service per schedule. Void's package includes services
             snooze-hourly, snooze-daily, snooze-weekly and snooze-monthly, which run the
             scripts in /etc/cron.hourly, /etc/cron.daily ... A job missed while the laptop was
             off or asleep runs when it next can.
  cronie     the classic cron with crontab -e (and anacron for missed jobs)
  fcron      cron that also catches up on missed jobs

With snooze, for example, a weekly TRIM (see: filesystems):
  sudo xbps-install snooze run-parts
  printf '#!/bin/sh\nfstrim -a\n' | sudo tee /etc/cron.weekly/fstrim
  sudo chmod +x /etc/cron.weekly/fstrim
  sudo ln -s /etc/sv/snooze-weekly /var/service/

A single job at a set time can also be its own runit service:  exec snooze -H3 -M30 backup.sh
(every day at 03:30; man snooze).

## Once, later
  sleep 600 && notify-send 'Tea'            in a terminal
  at                                        (package at) for jobs at a time, from a shell

See also: runit, locale (time zone) ; man chronyc ; man snooze ; man crontab ;
https://docs.voidlinux.org/config/date-time.html ; https://docs.voidlinux.org/config/cron.html

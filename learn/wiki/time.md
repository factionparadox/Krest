# Time and scheduled jobs

## The clock: ntpd
ntp-service-type in system.scm runs ntpd, which keeps the clock right over the network
(Guix's pool of servers, 0.guix.pool.ntp.org and so on, unless told otherwise). Guix keeps the hardware clock in UTC.
  sudo herd status ntpd
  date ; sudo hwclock --show
  guix shell ntp -- ntpq -p         the servers ntpd is using, and how far off each is
Other servers: (ntp-configuration (servers ...)) in the declaration; info "(guix) Networking
Services" has the fields. Time zone: see locale.

## Scheduled jobs: mcron
Guix's cron is mcron, written in Guile. Jobs are declared, like everything else; the service
runs them. Rassvet has one: fstrim-service-type adds a weekly TRIM of the SSD (see: filesystems).
  sudo herd schedule mcron          upcoming jobs and when they run
  sudo herd status mcron
To add your own, in /etc/config.scm's services (see: system):
  (simple-service 'my-jobs mcron-service-type
    (list #~(job "30 3 * * *" "rsync -a /home/you/ /media/backup/" #:user "you")))
The schedule is a crontab line (here: every day at 03:30), or Guile code such as
'(next-hour '(3)). A job missed while the laptop was asleep or off is not run later.

## Once, later
  sleep 600 && notify-send 'Tea'     in a terminal
  guix shell at                      the at command, for jobs at a time (it needs atd running)

See also: shepherd, locale (time zone) ; info "(guix) Scheduled Job Execution" ;
https://www.gnu.org/software/mcron/manual/ ; man ntpd

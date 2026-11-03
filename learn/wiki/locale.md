# Locale, keyboard, console and time zone

## Locales (language and formats)
glibc locales are built from the operating system's locale-definitions. Rassvet's system.scm
defines three: en_GB.utf8, en_US.utf8 and ru_RU.utf8. The system's own, LANG for everyone, is
the locale field: #:locale in /etc/config.scm, en_GB.utf8 unless you change it (English,
British spelling, dates, paper size).

  locale                                        what this shell uses
  locale -a                                     what is available

One part can differ, for just your account, in ~/.bash_profile:
  export LC_TIME=ru_RU.utf8                     Russian dates, English everything else
  export LANG=ru_RU.utf8                        Russian throughout, where programs have it
For the whole system:  #:locale "ru_RU.utf8"  in /etc/config.scm, then reconfigure. A locale
not among the three needs a locale-definition of its own (info "(guix) Locales").

Programs from your profile find the system's locales through GUIX_LOCPATH, which Guix System
sets; nothing to install.

## The keyboard
One keyboard-layout in system.scm serves GRUB, the text console and X:
  (keyboard-layout "gb,ru" ",phonetic" #:options '("grp:alt_shift_toggle"))
English (UK) and Russian phonetic, Alt+Shift to switch. setxkbmap -query shows what X uses;
try another layout for this session with
  setxkbmap -layout gb,ru -variant ,phonetic -option grp:alt_shift_toggle
A permanent change is a keyboard-layout of your own in the declaration (in X it is part of
rassvet-xorg-configuration; info "(guix) Keyboard Layout").

## The console
The text consoles (Ctrl+Alt+F2 ...) use Guix's console-font-service with its default font,
which has Cyrillic. setfont tries another for the moment.

## Time zone
The timezone field: #:timezone in /etc/config.scm ("Europe/London" unless you chose another),
then reconfigure. /etc/localtime follows it. For one shell:  TZ=Europe/Moscow date
The night light (rassvet-nightlight) works out sunset from this zone.

See also: time, system ; info "(guix) Locales" ; info "(guix) Keyboard Layout" ;
man setxkbmap ; man locale

# Locale, keyboard, console and time zone

## Locales (language and formats)
glibc's locales are generated with localedef; the installer made three: en_GB.UTF-8,
en_US.UTF-8 and ru_RU.UTF-8. Another one is one command:
  sudo localedef -i de_DE -f UTF-8 de_DE.UTF-8
The language itself is the LANG variable: en_GB.UTF-8 is meant (English, British spelling,
dates and paper size). The installer sets it only through a LANG line in /etc/rc.conf, if
CRUX's file has one; if  locale  shows POSIX or C, put  export LANG=en_GB.UTF-8  in a file of
your own in /etc/profile.d/.

  locale                                        what this shell uses
  locale -a                                     what is available

One part can differ, for just your account, in ~/.bash_profile:
  export LC_TIME=ru_RU.UTF-8                    Russian dates, English everything else
  export LANG=ru_RU.UTF-8                       Russian throughout, where programs have it
For every user, the same lines in a file of your own in /etc/profile.d/.

## The keyboard
X: /etc/X11/xorg.conf.d/30-krest.conf
  Option "XkbLayout" "gb,ru"   Option "XkbVariant" ",phonetic"
  Option "XkbOptions" "grp:alt_shift_toggle"
English (UK) and Russian phonetic, Alt+Shift to switch. setxkbmap -query shows what X uses;
try another layout for this session with
  setxkbmap -layout gb,ru -variant ,phonetic -option grp:alt_shift_toggle
and make it permanent in that file (it belongs to krest-desktop: an update keeps your
version and offers the new one through rejmerge).
The text console: KEYMAP=uk in /etc/rc.conf (loadkeys; the maps are in /usr/share/keymaps).
GRUB uses the firmware's US layout.

## The console
FONT in /etc/rc.conf; setfont tries another for the moment, from
/usr/share/kbd/consolefonts (Cyrillic ones included).

## Time zone
TIMEZONE in /etc/rc.conf ("Europe/London" unless you chose another), applied at boot by
linking /etc/localtime to /usr/share/zoneinfo/ZONE. For now as well:
  sudo ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime
For one shell:  TZ=Europe/Moscow date
The night light (krest-nightlight) works out sunset from this zone.

See also: time, rc-conf ; man localedef ; man setxkbmap ; man loadkeys ; man locale

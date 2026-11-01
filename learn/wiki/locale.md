# Locale, keyboard, console and time zone

## Locales (language and formats)
glibc compiles only the locales you ask for. The list is /etc/default/libc-locales: one per
line, a # in front means off. Pustota turns on en_GB.UTF-8, ru_RU.UTF-8 and en_US.UTF-8.

  sudo mcedit /etc/default/libc-locales         remove the # from a line, for example
                                                ja_JP.UTF-8 UTF-8
  sudo xbps-reconfigure -f glibc-locales        compile them
  locale -a                                     what is available

/etc/locale.conf chooses the system's: LANG=en_GB.UTF-8 (English, British spelling, dates,
paper size) and LC_COLLATE=C (sort file names byte by byte). One part can differ:
  LC_TIME=ru_RU.UTF-8                           Russian dates, English everything else
For just your account, put  export LANG=ru_RU.UTF-8  in ~/.bash_profile.

## /etc/rc.conf
Read by runit's stages 1 and 3, at boot and shutdown (see: runit):
  KEYMAP="uk"             the text console's keyboard (loadkeys; the names are in
                          /usr/share/kbd/keymaps)
  FONT="ter-v24n"         the console font: Terminus, 24 pixels (terminus-font; the list is
                          /usr/share/kbd/consolefonts)
  HARDWARECLOCK="UTC"     the hardware clock keeps UTC (right for Linux-only machines)
Try a font now without rebooting: setfont ter-v32n

## The keyboard in X
/etc/X11/xorg.conf.d/00-keyboard.conf sets English (UK) and Russian (phonetic) with
Alt+Shift switching. setxkbmap -query shows the current settings; try another layout with
  setxkbmap -layout gb,ru -variant ,phonetic -option grp:alt_shift_toggle
and make it permanent in that file.

## Time zone
/etc/localtime is a link into /usr/share/zoneinfo:
  sudo ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime
  date                                         check
The night light (pustota-nightlight) works out sunset from this zone.

See also: time ; man locale.conf ; man rc.conf (Void's rc.conf is commented) ; man setxkbmap ;
https://docs.voidlinux.org/config/locales.html ; https://docs.voidlinux.org/config/rc-files.html

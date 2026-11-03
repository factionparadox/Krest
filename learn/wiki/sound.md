# Sound

## PipeWire on Guix
PipeWire is the sound server: programs talk to it, and it talks to the hardware through ALSA
(the kernel's sound layer). It is not a system service: it runs as you, inside your session,
and it needs a session bus and XDG_RUNTIME_DIR, which dbus-run-session (in rassvet-session) and
elogind provide. Three programs make it complete, all installed by system.scm:
  pipewire          the server
  wireplumber       the session manager: picks devices, remembers volumes
  pipewire-pulse    the PulseAudio replacement, for programs that speak PulseAudio (Firefox)

Guix usually starts them with Guix Home's home-pipewire-service-type. Rassvet uses no Guix
Home, and neither system.scm nor rassvet-session starts them, so if  pgrep -a pipewire  is
empty, start them from ~/.config/rassvet/autostart (an executable script):
  #!/bin/sh
  pipewire & sleep 1 ; wireplumber & pipewire-pulse &
Plain ALSA programs (aplay) then still go straight to the hardware, not through PipeWire.

## Using it
  volume keys, mute, mic mute        pamixer (bound in ratpoison)
  Ctrl+Super+m                       pulsemixer: per-program volume, inputs, outputs
  wpctl status                       every device and stream, with numbers
  wpctl set-default 52               make device 52 the output
  wpctl set-volume @DEFAULT_AUDIO_SINK@ 50%
  pw-top                             what is playing, and the load

## Laptop audio
The Framework's speakers and microphones sit behind Intel's audio DSP: the kernel's SOF and
SoundWire drivers run it, with firmware from linux-firmware. Bluetooth headphones go through
PipeWire too; pair them with bluetoothctl (Ctrl+Super+b).

## When there is no sound
  pgrep -a pipewire ; pgrep -a wireplumber     are they running?
  wpctl status                                  is the right output the default (marked *)?
  sudo dmesg | grep -i -e sof -e snd            did the DSP's firmware load? (see: firmware)
  aplay -l                                      the cards the kernel found
Then pkill pipewire wireplumber pipewire-pulse and start them again from a terminal, to read
their messages.

See also: elogind, firmware ; man pipewire ; man wpctl ; man pamixer ;
https://docs.pipewire.org/

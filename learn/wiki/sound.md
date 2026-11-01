# Sound

## PipeWire on Void
PipeWire is the sound server: programs talk to it, and it talks to the hardware through ALSA
(the kernel's sound layer). On Void it is not a system service: it runs as you, started with
your session, and it needs a session bus and XDG_RUNTIME_DIR, which dbus-run-session and
elogind provide. Pustota's session starts it with one line, pipewire &.

PipeWire then starts its helpers because of two links that Pustota's package installs, as the
Void Handbook describes:
  /etc/pipewire/pipewire.conf.d/10-wireplumber.conf    WirePlumber, the session manager:
                                                       picks devices, remembers volumes
  /etc/pipewire/pipewire.conf.d/20-pipewire-pulse.conf the PulseAudio replacement, for
                                                       programs that speak PulseAudio (Firefox)
and two more make plain ALSA programs use PipeWire:
  /etc/alsa/conf.d/50-pipewire.conf, 99-pipewire-default.conf

## Using it
  volume keys, mute, mic mute        pamixer (bound in ratpoison)
  Ctrl+Super+m                       pulsemixer: per-program volume, inputs, outputs
  wpctl status                       every device and stream, with numbers
  wpctl set-default 52               make device 52 the output
  wpctl set-volume @DEFAULT_AUDIO_SINK@ 50%
  pw-top                             what is playing, and the load

## Laptop audio
The Framework's speakers and microphones need sof-firmware (Intel's Sound Open Firmware),
which is installed. Bluetooth headphones work through PipeWire (libspa-bluetooth); pair them
with Ctrl+Super+b.

## When there is no sound
  pgrep -a pipewire ; pgrep -a wireplumber     are they running?
  wpctl status                                  is the right output the default (marked *)?
  dmesg | grep -i -e sof -e snd                 did the firmware load?
Then log out and in (restarts the session's PipeWire), or pkill pipewire and start it again
from a terminal to read its messages: pipewire &

See also: elogind ; man pipewire ; man wpctl ; man pamixer ;
https://docs.voidlinux.org/config/media/pipewire.html

# Sound

## PipeWire without systemd
PipeWire is the sound server: programs talk to it, and it talks to the hardware through ALSA
(the kernel's sound layer). It is not a system service: it runs as you, inside your session,
and it needs a session bus and XDG_RUNTIME_DIR. Elsewhere systemd's user services start it;
here krest-session does, before anything else:
  dbus-run-session    the session bus (the session restarts itself inside one)
  pipewire          the server
  wireplumber       the session manager: picks devices, remembers volumes
  pipewire-pulse    the PulseAudio replacement, for programs that speak PulseAudio (Firefox)
XDG_RUNTIME_DIR (/run/user/UID, where the sockets go) is made at login by the
dumb_runtime_dir PAM module, which does the one part of logind's job PipeWire needs. All
three stop when the session ends. The PulseAudio package is installed for its libraries and
pactl; /etc/pulse/client.conf.d/50-krest.conf (autospawn = no) keeps its daemon from
starting. Plain ALSA programs (aplay) go straight to the hardware, not through PipeWire.

## Using it
  volume keys, mute, mic mute        wpctl (bound in ratpoison)
  Ctrl+Super+m                       pulsemixer: per-program volume, inputs, outputs
  wpctl status                       every device and stream, with numbers
  wpctl set-default 52               make device 52 the output
  wpctl set-volume @DEFAULT_AUDIO_SINK@ 50%
  pw-top                             what is playing, and the load

## Laptop audio
The Framework's speakers and microphones sit behind Intel's audio DSP: the kernel's SOF and
SoundWire drivers run it, with firmware from linux-firmware. Bluetooth headphones go through
PipeWire too; pair them in bluetuith (Ctrl+Super+b).

## When there is no sound
  pgrep -a pipewire ; pgrep -a wireplumber     are they running?
  echo $XDG_RUNTIME_DIR ; ls -ld /run/user/$(id -u)   does the runtime folder exist?
  wpctl status                                  is the right output the default (marked *)?
  sudo dmesg | grep -i -e sof -e snd            did the DSP's firmware load? (see: firmware)
  aplay -l                                      the cards the kernel found
Then pkill pipewire wireplumber pipewire-pulse and start them again from a terminal, to read
their messages.

See also: sleep (what logind would have done), firmware ; man pipewire ; man wpctl ;
https://docs.pipewire.org/

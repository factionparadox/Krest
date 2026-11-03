# Sound: PipeWire

PipeWire carries all audio. It runs as YOUR program, not as a system service: system.scm
installs pipewire, wireplumber (which picks devices and remembers volumes) and pipewire-pulse
(for programs that expect PulseAudio, Firefox among them), and they run inside your session,
using the session's D-Bus and the XDG_RUNTIME_DIR elogind makes.

Nothing in system.scm starts them. If  pgrep -a pipewire  shows nothing after logging in, start
all three from ~/.config/rassvet/autostart (an executable script the session runs):
    #!/bin/sh
    pipewire & sleep 1 ; wireplumber & pipewire-pulse &

The Framework's speakers and microphones sit behind Intel's audio DSP, run by the kernel's SOF
and SoundWire drivers with firmware from linux-firmware.

## Use
    the volume and mute keys          (pamixer, bound in ratpoison)
    Ctrl+Super+m                      pulsemixer: per-program volumes, inputs, outputs
    pamixer --get-volume ; pamixer --list-sinks

## Look
    pgrep -a pipewire ; pgrep -a wireplumber
    wpctl status                      everything PipeWire sees
    aplay -l                          the sound cards the kernel found

References: rassvet-learn wiki sound ; man pipewire ; https://docs.pipewire.org/

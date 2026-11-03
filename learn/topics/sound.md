# Sound: PipeWire

PipeWire carries all audio. It runs as YOUR program, not as a system service: krest-session
starts the three pieces when you log in, and they stop when the session ends:
    pipewire          the server
    wireplumber       picks devices and remembers volumes
    pipewire-pulse    for programs that expect PulseAudio, Firefox among them
They use the session's D-Bus (dbus-run-session) and your XDG_RUNTIME_DIR, /run/user/UID, which
the dumb_runtime_dir PAM module makes at login (there is no elogind to do it). The PulseAudio
daemon itself is installed for its libraries but never starts (autospawn = no in
/etc/pulse/client.conf.d/50-krest.conf).

The Framework's speakers and microphones sit behind Intel's audio DSP, run by the kernel's SOF
and SoundWire drivers with firmware from linux-firmware.

## Use
    the volume and mute keys          (wpctl, bound in ratpoison)
    Ctrl+Super+m                      pulsemixer: per-program volumes, inputs, outputs
    wpctl set-volume @DEFAULT_AUDIO_SINK@ 50%
The volume keys run wpctl, WirePlumber's own tool: it changes the default output (or input).

## Look
    pgrep -a pipewire ; pgrep -a wireplumber
    wpctl status                      everything PipeWire sees
    aplay -l                          the sound cards the kernel found

References: krest-learn wiki sound ; man pipewire ; https://docs.pipewire.org/

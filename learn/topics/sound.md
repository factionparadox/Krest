# Sound: PipeWire

PipeWire carries all audio (and screen capture). It runs as YOUR program, started by
pustota-session, not as a system service. Two configuration links make it complete:
/etc/pipewire/pipewire.conf.d/10-wireplumber.conf starts WirePlumber (which picks devices and
remembers volumes) and 20-pipewire-pulse.conf serves programs that expect PulseAudio. ALSA
programs reach it through /etc/alsa/conf.d.

The Framework's speakers and microphones sit behind Intel's audio DSP: the SOF firmware
(sof-firmware) and SoundWire drivers in Linux 7.x run them.

## Use
    the volume and mute keys          (pamixer, bound in ratpoison)
    Ctrl+Super+m                      pulsemixer: per-program volumes, inputs, outputs
    pamixer --get-volume ; pamixer --list-sinks

## Look
    pgrep -a pipewire ; pgrep -a wireplumber
    wpctl status                      everything PipeWire sees
    aplay -l                          the sound cards the kernel found

References: https://docs.voidlinux.org/config/media/pipewire.html

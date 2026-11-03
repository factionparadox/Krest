# Graphics (Intel)

The Framework 13 Pro's Intel graphics need no drivers beyond what is installed: the kernel's
xe/i915 driver does the work, Xorg's built-in modesetting driver draws the screen, and Mesa
provides OpenGL and Vulkan.

## What is installed (system.scm)
  mesa                        OpenGL (iris) and Vulkan (anv)
  intel-media-driver-nonfree  VA-API video decoding and encoding (the "iHD" driver, for Intel
                              graphics from 2020 on), from Nonguix. LIBVA_DRIVER_NAME=iHD is
                              set in /etc/profile.d/rassvet.sh
  libva-utils                 vainfo
Rassvet's X configuration (rassvet-xorg-configuration, the one ly starts X with) chooses
modesetting with TearFree (no tearing in video), and sets the touchpad and keyboard.
xf86-video-intel, the old Intel X driver, is not used: it does not support recent chips well.

## Video decoding (battery life)
Decoding video on the GPU instead of the processor saves a lot of power.
  vainfo                                     lists what the GPU can decode (H.264, HEVC, VP9, AV1)
  mpv --hwdec=auto FILE                      watch the line "Using hardware decoding (vaapi)"
mpv does this by default here (~/.config/mpv/mpv.conf: hwdec=auto-safe). In Firefox,
about:support, section Media, shows whether hardware decoding is in use; Rassvet's policy
(/etc/firefox/policies/policies.json) switches media.ffmpeg.vaapi.enabled on.

## Looking
Tools that are not installed run straight from Guix, without installing:
  guix shell mesa-utils -- glxinfo -B        the OpenGL renderer and version
  guix shell vulkan-tools -- vulkaninfo --summary
  sudo guix shell intel-gpu-tools -- intel_gpu_top    how busy the GPU is, live
  xrandr                                     the screen and its modes
DPI: 144 (Xft.dpi in /etc/rassvet/Xresources), for the 13 Pro's 2880x1920 screen; set your own
in ~/.Xresources.

See also: kernel, firmware ; man modesetting ; man vainfo ; info "(guix) X Window"

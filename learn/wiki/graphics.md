# Graphics (Intel)

The Framework 13 Pro's Intel graphics need no drivers beyond what is installed: the kernel's
i915/xe driver does the work, Xorg's built-in modesetting driver draws the screen, and Mesa
provides OpenGL and Vulkan.

## What is installed
  mesa-dri             OpenGL (iris)
  mesa-vulkan-intel    Vulkan (anv)
  intel-media-driver   VA-API video decoding and encoding (the "iHD" driver, for Intel
                       graphics from 2020 on). LIBVA_DRIVER_NAME=iHD is set in
                       /etc/profile.d/pustota.sh
  libva-utils          vainfo
/etc/X11/xorg.conf.d/20-intel.conf chooses modesetting with TearFree (no tearing in video).
xf86-video-intel, the old Intel X driver, is not used: it does not support recent chips well.

## Video decoding (battery life)
Decoding video on the GPU instead of the processor saves a lot of power.
  vainfo                                     lists what the GPU can decode (H.264, HEVC, VP9, AV1)
  mpv --hwdec=auto FILE                      watch the line "Using hardware decoding (vaapi)"
In Firefox: about:support, section Media, shows whether hardware decoding is in use; the
setting media.ffmpeg.vaapi.enabled in about:config turns it on if it is not.

## Looking
  glxinfo -B (mesa-demos)          the OpenGL renderer and version
  sudo intel_gpu_top (intel-gpu-tools)   how busy the GPU is, live
  xrandr                           the screen, its modes; xrandr --dpi 144 (Pustota's setting,
                                   for the 13 Pro's 2880x1920 screen; also in Xresources)

See also: kernel, firmware ; man modesetting ; man vainfo ;
https://docs.voidlinux.org/config/graphical-session/graphics-drivers/intel.html

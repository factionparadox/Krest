// Pustota: hardware video decoding (VA-API, Intel's iHD driver): video in Firefox uses the GPU,
// not the processor, which saves a lot of battery. about:support -> Media shows what is used.
pref("media.ffmpeg.vaapi.enabled", true);
pref("media.hardware-video-decoding.enabled", true);

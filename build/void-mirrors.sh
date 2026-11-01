# Void's mirrors, nearest-first for the UK (Tier 1, then Tier 2 in Europe), from
# https://xmirror.voidlinux.org (1 November 2026). Sourced by the build scripts.
VOID_MIRRORS="https://repo-default.voidlinux.org
https://repo-de.voidlinux.org
https://repo-fi.voidlinux.org
https://repo-fastly.voidlinux.org
https://mirrors.dotsrc.org/voidlinux
https://ftp.lysator.liu.se/pub/voidlinux
https://mirrors.summithq.com/voidlinux"

# pick_void_mirror: print the first mirror that serves Void's x86_64 index ($VOID_MIRROR wins).
pick_void_mirror() {
  local m
  if [ -n "${VOID_MIRROR:-}" ]; then echo "${VOID_MIRROR%/}"; return 0; fi
  for m in $VOID_MIRRORS; do
    if curl -fsS -o /dev/null --max-time 15 -r 0-0 "$m/current/x86_64-repodata" 2>/dev/null; then
      echo "$m"; return 0
    fi
    echo "    Void mirror not reachable: $m" >&2
  done
  return 1
}

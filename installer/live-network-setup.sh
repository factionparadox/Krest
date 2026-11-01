#!/usr/bin/env bash
# Live-only network setup: nmtui first, then the installer once Void's repository is reachable.
# The installer must never proceed to disk erase when offline.
set -Eeuo pipefail
[[ $EUID == 0 ]] ||
  { echo "Pustota network setup must run as root." >&2; exit 2; }
for command in sv nmcli nmtui dialog python3; do
  command -v "$command" >/dev/null ||
    { echo "the Pustota ISO is missing: $command" >&2; exit 2; }
done
# Ensure runit has started the D-Bus and NetworkManager services.
for service in dbus NetworkManager; do
  sv -w 30 up "$service" ||
    { echo "Could not start $service on the live ISO." >&2; exit 2; }
done
ready=no
for _ in $(seq 1 20); do
  if nmcli -t -f RUNNING general 2>/dev/null | grep -qx running; then
    ready=yes
    break
  fi
  sleep 1
done
[[ $ready == yes ]] ||
  { echo "NetworkManager failed to become ready." >&2; exit 2; }

check_repository() {
  # Any of Void's mirrors will do (the installer picks the same way). No disk operations.
  for m in https://repo-default.voidlinux.org https://repo-de.voidlinux.org https://repo-fi.voidlinux.org \
           https://repo-fastly.voidlinux.org https://mirrors.dotsrc.org/voidlinux \
           https://ftp.lysator.liu.se/pub/voidlinux https://mirrors.summithq.com/voidlinux; do
    python3 -c "import urllib.request; urllib.request.urlopen('$m/current/x86_64-repodata', timeout=10).read(1)" \
      >/dev/null 2>&1 && return 0
  done
  return 1
}

while :; do
  clear
  printf '%s\n' \
    "Pustota network setup" \
    "Connect to Wi-Fi using nmtui, or exit nmtui if Ethernet is already connected." \
    "The disk installer will start only when the Void XBPS repository is reachable."
  # Always show nmtui before the first installer screen. Return/cancel is
  # allowed: connectivity is independently checked afterwards.
  nmtui connect || :
  if check_repository; then
    echo "Void repository reachable. Starting the Pustota installer."
    exec /usr/bin/pustota-installer
  fi
  if ! dialog --clear --stdout --backtitle "Pustota network setup" \
      --title "Network required" --defaultno --yes-label "Open nmtui" \
      --no-label "Exit" --yesno \
      "Cannot reach the Void XBPS package repository.\n\nReconnect Wi-Fi or Ethernet using nmtui?\nNo disk has been erased." \
      12 73; then
    clear
    echo "Network setup cancelled. the Pustota installer was not started."
    exit 1
  fi
done

#!/usr/bin/env bash
# Run by pinned void-mklive AFTER enabling services, before SquashFS creation.
# Base live variant normally enables dhcpcd and wpa_supplicant as standalone
# daemons. They must not compete with NetworkManager for the same interfaces.
set -Eeuo pipefail
[[ $# == 1 && -d $1/etc/runit/runsvdir/default ]] ||
  { echo "Invalid Pustota live rootfs" >&2; exit 2; }
rootfs="$1"
services="$rootfs/etc/runit/runsvdir/default"
for service in dbus NetworkManager; do
  [[ -d $rootfs/etc/sv/$service ]] ||
    { echo "Missing live runit service: $service" >&2; exit 2; }
  ln -sfn "/etc/sv/$service" "$services/$service"
done
# Keep the wpa_supplicant package as a NetworkManager dependency, but do not
# start its independent runit service. Same applies to dhcpcd.
# sshd too: the live image has a published password, so nothing should listen for logins.
for service in dhcpcd wpa_supplicant sshd; do
  rm -f "$services/$service"
done
[[ -x $rootfs/usr/bin/nmtui && -x $rootfs/usr/bin/nmcli ]] ||
  { echo "NetworkManager was not bundled with nmtui/nmcli" >&2; exit 2; }
[[ -x $rootfs/usr/lib/pustota/live-network-setup.sh ]] ||
  { echo "Missing Pustota network setup" >&2; exit 2; }
printf '%s\n' "Pustota live networking: dbus and NetworkManager enabled; nmtui bundled."

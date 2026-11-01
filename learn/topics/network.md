# Network and Bluetooth

NetworkManager manages Wi-Fi, Ethernet (USB-C dongles, docks) and VPNs; dhcpcd and
wpa_supplicant do not run as their own services, so nothing fights over the card. The
Framework's Wi-Fi 7 card needs linux-firmware-intel, which is installed.

## Use
    Ctrl+Super+n                      pick a network (networkmanager_dmenu)
    nmtui                             a full-screen menu in a terminal
    nmcli device wifi list ; nmcli device wifi connect NAME --ask
    nmcli connection show             saved networks

## VPN (Proton VPN or any WireGuard service)
NetworkManager runs WireGuard itself (it is in the kernel), so no VPN app is needed. Once:
in your Proton account, Downloads -> WireGuard configuration, pick a server and download the
file. Give it a short name (NetworkManager uses it for the interface: 15 characters at most):
    nmcli connection import type wireguard file ~/Downloads/proton-uk.conf
Then Ctrl+Super+p switches it on and off (pustota-vpn), or:
    nmcli connection up id proton-uk ; nmcli connection down id proton-uk
It stays off at boot unless you ask:  nmcli connection modify proton-uk autoconnect yes

## Look
    ip -br addr ; ip route ; ping -c 3 voidlinux.org
    iw dev                            the Wi-Fi card
    sudo sv status NetworkManager

## Bluetooth
bluetoothd is the service; bluetuith (Ctrl+Super+b) is a menu in the terminal for pairing headphones
and keyboards. PipeWire handles Bluetooth audio (libspa-bluetooth).
    bluetoothctl                      the plain command-line tool

References: https://docs.voidlinux.org/config/network/networkmanager.html ; man nmcli ;
https://docs.voidlinux.org/config/bluetooth.html

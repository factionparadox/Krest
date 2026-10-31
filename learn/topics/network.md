# Network and Bluetooth

NetworkManager manages Wi-Fi, Ethernet (USB-C dongles, docks) and VPNs; dhcpcd and
wpa_supplicant do not run as their own services, so nothing fights over the card. The
Framework's Wi-Fi 7 card needs linux-firmware-intel, which is installed.

## Use
    Super+n                           pick a network (networkmanager_dmenu)
    nmtui                             a full-screen menu in a terminal
    nmcli device wifi list ; nmcli device wifi connect NAME --ask
    nmcli connection show             saved networks

## Look
    ip -br addr ; ip route ; ping -c 3 voidlinux.org
    iw dev                            the Wi-Fi card
    sudo sv status NetworkManager

## Bluetooth
bluetoothd is the service; bluetuith (Super+b) is a menu in the terminal for pairing headphones
and keyboards. PipeWire handles Bluetooth audio (libspa-bluetooth).
    bluetoothctl                      the plain command-line tool

References: https://docs.voidlinux.org/config/network/networkmanager.html ; man nmcli ;
https://docs.voidlinux.org/config/bluetooth.html

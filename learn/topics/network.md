# Network and Bluetooth

NetworkManager manages Wi-Fi, Ethernet (USB-C dongles, docks) and VPNs; it drives
wpa_supplicant itself (both are services in system.scm), so nothing fights over the card. The
Framework's Wi-Fi 7 card needs Nonguix's kernel and linux-firmware, which are installed.

## Use
    Ctrl+Super+n                      nmtui: pick a network in a terminal (networkmanager_dmenu,
                                      the dmenu picker, is not packaged for Guix)
    nmcli device wifi list ; nmcli device wifi connect NAME --ask
    nmcli connection show             saved networks

## VPN (Proton VPN or any WireGuard service)
NetworkManager runs WireGuard itself (it is in the kernel), so no VPN app is needed; the Proton
VPN app is not packaged for Guix. Once: in your Proton account, Downloads -> WireGuard
configuration, pick a server and download the file. Give it a short name (NetworkManager uses
it for the interface: 15 characters at most):
    nmcli connection import type wireguard file ~/Downloads/proton-uk.conf
Then Ctrl+Super+p or the menu's "VPN on/off" (rassvet-vpn) switches it, or:
    nmcli connection up id proton-uk ; nmcli connection down id proton-uk
It stays off at boot unless you ask:  nmcli connection modify proton-uk autoconnect yes

## Look
    ip -br addr ; ip route ; ping -c 3 guix.gnu.org
    iw dev                            the Wi-Fi card
    sudo herd status NetworkManager
    sudo nft list ruleset             the firewall (rassvet-learn learn security)

## Bluetooth
bluetoothd is the service (bluetooth-service-type). Ctrl+Super+b opens bluetoothctl in a
terminal (bluetuith, the friendlier menu, is not packaged for Guix):
    power on ; scan on ; pair XX:XX:... ; connect XX:XX:... ; trust XX:XX:...

References: man nmcli ; man nmtui ; rassvet-learn wiki network ;
info "(guix) Networking Setup"

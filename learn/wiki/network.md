# Network

## NetworkManager
Rassvet uses NetworkManager for Wi-Fi, Ethernet (USB-C docks and dongles) and VPNs:
network-manager-service-type in system.scm, with wpa-supplicant-service-type beside it, which
NetworkManager drives over D-Bus for Wi-Fi. It runs its own DHCP, so no other network service is
declared: two at once fight over the card.

  Ctrl+Super+n                       nmtui in a terminal (networkmanager_dmenu, the dmenu
                                     picker, is not packaged for Guix)
  nmcli device wifi list
  nmcli device wifi connect NAME --ask
  nmcli connection show              saved connections (files in
                                     /etc/NetworkManager/system-connections/, root only)
  nmcli connection modify NAME connection.autoconnect no
  nmcli radio wifi off               flight mode for Wi-Fi
  sudo herd status NetworkManager

Wi-Fi power saving is kept on by /etc/NetworkManager/conf.d/50-rassvet-wifi-powersave.conf,
which system.scm writes.

## Names and DNS
  host-name                          this computer's name: #:host-name in /etc/config.scm
  /etc/hosts                         generated from the declaration (the hosts-file field)
  /etc/resolv.conf                   DNS servers: NetworkManager writes it; do not edit
  nmcli connection modify NAME ipv4.dns "9.9.9.9 1.1.1.1" ipv4.ignore-auto-dns yes
                                     choose your own DNS servers for one connection

## VPN
The Proton VPN app is not packaged for Guix; Ctrl+Super+p runs rassvet-vpn instead, which
switches VPN connections kept in NetworkManager. NetworkManager runs WireGuard itself (it is in
the kernel), so a WireGuard file from your Proton account, or any other service, is enough:
  nmcli connection import type wireguard file proton-uk.conf
then Ctrl+Super+p (or menu -> VPN on/off). The details: rassvet-learn learn network.

## Firewall: nftables
nftables-service-type loads Rassvet's ruleset at boot (%rassvet-nftables in system.scm):
  chain input    policy drop: accept replies to connections this laptop made, loopback,
                 ICMP and ICMPv6, and mDNS (UDP 5353); drop everything else
  chain forward  policy drop
  chain output   policy accept
  sudo nft list ruleset              the rules as loaded now
  sudo nft add rule inet rassvet input tcp dport 8000 accept     open a port until reboot
To open a port for good, give nftables-configuration your own ruleset in /etc/config.scm:
  (nftables-service-type config =>
    (nftables-configuration (ruleset (local-file "/etc/rassvet-nftables.conf"))))
inside modify-services (see: system), starting from a copy of Rassvet's rules
(sudo nft list ruleset > /etc/rassvet-nftables.conf, then add flush ruleset at the top).
Programs that listen only on 127.0.0.1 (the tutor, Kiwix) are not reachable from outside
whatever the firewall says.

## Looking
  ip -br addr ; ip route             addresses and the way out
  ping -c 3 guix.gnu.org
  iw dev ; iw dev wlan0 link         the Wi-Fi card and its signal (the name may differ)
  ss -tulpn                          what is listening (sudo for program names)

See also: users (groups), shepherd, system ; man nmcli ; man NetworkManager.conf ; man nft ;
info "(guix) Networking Setup" ; info "(guix) Networking Services"

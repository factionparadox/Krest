# Network

## NetworkManager
Krest uses NetworkManager for Wi-Fi, Ethernet (USB-C docks and dongles) and VPNs:
/etc/rc.d/networkmanager, in SERVICES after dbus. It drives wpa_supplicant itself over D-Bus
for Wi-Fi and runs its own DHCP, so CRUX's net script (/etc/rc.d/net, static settings) is
left out of SERVICES: two at once fight over the card.

  Ctrl+Super+n                       networkmanager_dmenu: networks and VPNs in dmenu
  nmtui                              the same in a terminal
  nmcli device wifi list
  nmcli device wifi connect NAME --ask
  nmcli connection show              saved connections (files in
                                     /etc/NetworkManager/system-connections/, root only)
  nmcli connection modify NAME connection.autoconnect no
  nmcli radio wifi off               flight mode for Wi-Fi
  sudo /etc/rc.d/networkmanager status

Wi-Fi power saving is kept on by /etc/NetworkManager/conf.d/50-krest-wifi-powersave.conf.

## Names and DNS
  HOSTNAME                           this computer's name: /etc/rc.conf (see: rc-conf)
  /etc/hosts                         the installer wrote localhost and the hostname
  /etc/resolv.conf                   DNS servers: NetworkManager writes it; do not edit
  nmcli connection modify NAME ipv4.dns "9.9.9.9 1.1.1.1" ipv4.ignore-auto-dns yes
                                     choose your own DNS servers for one connection

## VPN
Ctrl+Super+p runs the Proton VPN app (protonvpn-app, Krest's proton-vpn-gtk-app port); its
connections go through NetworkManager (WireGuard, or OpenVPN through the networkmanager-openvpn
port). Without the app, krest-vpn
switches VPN connections kept in NetworkManager; NetworkManager runs WireGuard itself (it is
in the kernel), so a WireGuard file from Proton or any other service is enough:
  nmcli connection import type wireguard file proton-uk.conf
then the menu's "VPN on/off (WireGuard files)". The details: krest-learn learn network.

## Firewall: nftables
/etc/rc.d/krest-firewall (in SERVICES) loads /etc/nftables.d/krest.nft at boot:
  chain input    policy drop: accept replies to connections this laptop made, loopback,
                 ICMP and ICMPv6, and mDNS (UDP 5353); drop everything else
  chain forward  policy drop
  chain output   policy accept
  sudo nft list ruleset              the rules as loaded now (also: krest-firewall status)
  sudo nft add rule inet krest input tcp dport 8000 accept     open a port until reboot
To open a port for good, add the rule to /etc/nftables.d/krest.nft (sudoedit), then
sudo /etc/rc.d/krest-firewall restart. The file belongs to krest-desktop; an update keeps
your version and offers Krest's new one through rejmerge. stop flushes every rule.
Programs that listen only on 127.0.0.1 (the tutor, Kiwix) are not reachable from outside
whatever the firewall says.

## Looking
  ip -br addr ; ip route             addresses and the way out
  ping -c 3 crux.nu
  iw dev ; iw dev wlan0 link         the Wi-Fi card and its signal (the name may differ)
  ss -tulpn                          what is listening (sudo for program names)

See also: users (groups), rc, rc-conf ; man nmcli ; man NetworkManager.conf ; man nft

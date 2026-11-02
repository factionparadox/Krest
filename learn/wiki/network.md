# Network

## NetworkManager
Pustota uses NetworkManager for Wi-Fi, Ethernet (USB-C docks and dongles) and VPNs. It is a
runit service (/etc/sv/NetworkManager) that runs its own DHCP and Wi-Fi handling, so Void's
other choices (dhcpcd, wpa_supplicant, iwd, each a service of its own) stay off: two of them at
once fight over the card.

  Ctrl+Super+n                       pick a Wi-Fi network (networkmanager_dmenu)
  nmtui                              a full-screen menu in a terminal
  nmcli device wifi list
  nmcli device wifi connect NAME --ask
  nmcli connection show              saved connections (files in
                                     /etc/NetworkManager/system-connections/, root only)
  nmcli connection modify NAME connection.autoconnect no
  nmcli radio wifi off               flight mode for Wi-Fi

Changing connections needs no password for members of the network group (Void's polkit rule
in /usr/share/polkit-1/rules.d/50-org.freedesktop.NetworkManager.rules).

## Names and DNS
  /etc/hostname                      this computer's name
  /etc/hosts                         names you fix by hand
  /etc/resolv.conf                   DNS servers: NetworkManager writes it; do not edit
  nmcli connection modify NAME ipv4.dns "9.9.9.9 1.1.1.1" ipv4.ignore-auto-dns yes
                                     choose your own DNS servers for one connection

## VPN
Ctrl+Super+p opens the Proton VPN app (protonvpn-app): Proton's own GTK app, which Void does
not package. Pustota builds it from five recipes adopted from ProtonVPN-Void (srcpkgs/
proton-vpn-gtk-app and its python3-proton-* libraries), which make it work without systemd:
- it connects through ProTun, Proton's NetworkManager plugin (/usr/libexec/nm-protun-service);
- it keeps your login in the Secret Service: gnome-keyring, started by Pustota's session
  (the first time, it asks you to choose a password for that keyring);
- not available: the kill switch (its permanent mode is a systemd unit) and split tunnelling.
Run it as yourself, never with sudo. Its logs: ~/.cache/Proton/VPN/logs/.

Without the app, WireGuard files work too: NetworkManager runs WireGuard itself.
  nmcli connection import type wireguard file proton-uk.conf
then menu -> VPN on/off (pustota-vpn). The details: pustota-learn learn network.

## Firewall: ufw
ufw ("uncomplicated firewall") writes iptables rules from simple commands. Pustota turns it on
at install (ENABLED=yes in /etc/ufw/ufw.conf, and the ufw runit service): everything coming in
is dropped, everything going out is allowed.
  sudo ufw status verbose
  sudo ufw allow 22/tcp              let ssh in (from anywhere)
  sudo ufw allow from 192.168.1.0/24 to any port 8000 proto tcp     only from your home network
  sudo ufw delete allow 22/tcp
  sudo ufw disable ; sudo ufw enable
Programs that listen only on 127.0.0.1 (Ollama, Kiwix in Pustota) are not reachable from
outside whatever the firewall says.

## Looking
  ip -br addr ; ip route             addresses and the way out
  ping -c 3 voidlinux.org
  iw dev ; iw dev wlan0 link         the Wi-Fi card and its signal (the name may differ)
  ss -tulpn                          what is listening (sudo for program names)

See also: users (groups), runit ; man nmcli ; man NetworkManager.conf ; man ufw ;
https://docs.voidlinux.org/config/network/networkmanager.html ;
https://docs.voidlinux.org/config/network/

# Users, sudo and trust

You are in the wheel group, so sudo works with your password (/etc/sudoers.d/krest); the
root account has the same password, for recovery from a console. Suspend, hibernate, reboot
and power off need no password, so the menu, Super+z and the lid work. Other groups give you
hardware without sudo: audio, video, input. Accounts are ordinary: useradd, passwd, usermod,
and /etc/passwd, /etc/group and /etc/shadow are the real files.

## Automatic login
If you chose it, ly (the login screen on tty1) logs you in at boot: auto_login_user and
auto_login_session in /etc/ly/config.ini. The screen still locks with your password on sleep,
lid close and Super+x (xss-lock + slock), so a stolen sleeping laptop is locked, but a stolen
powered-off one boots to your desktop. To turn it off, delete those two lines from
/etc/ly/config.ini (sudoedit). Without disk encryption, anyone with the laptop can read the
disk anyway: Krest does not encrypt it (yet). There is no fingerprint login: fprintd is not
included.

## Software
Everything is compiled here from source. CRUX's ports are signed (pkgmk checks each port's
.signature against the keys in /etc/ports); every source Krest's own ports download is
checked against the SHA-256 in the port's sha256 file, or, for the few marked "-", against the
hash recorded the first time it was downloaded (/var/lib/krest/sources.sha256). The Krest
repository itself comes from GitHub over HTTPS, without signed commits. The Russian material is
checked against published or pinned checksums.

## Network
The firewall is nftables: /etc/rc.d/krest-firewall loads /etc/nftables.d/krest.nft at
boot. Everything coming in is dropped unless it answers something this laptop asked for (plus
loopback, ICMP and mDNS); everything going out is allowed. Nothing else listens on the
network: the tutor (llama-server) and the dictionary server (kiwix-serve) listen on 127.0.0.1,
this computer only. openssh is installed, but no ssh server runs (sshd is not in SERVICES).

    sudo nft list ruleset             the firewall as it is now
    ss -tlnp                          what is listening
    id                                your groups

References: man sudo ; man nft ; man useradd ; krest-learn wiki users

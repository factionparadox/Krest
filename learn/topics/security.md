# Users, sudo and trust

You are in the wheel group, so sudo works with your password; the root account has the same
password, for recovery from a console. Other groups give you hardware without sudo: audio,
video, input, netdev (network devices), lp (printers), kvm (virtual machines). Accounts are
declared in system.scm; passwords are the one part you change by hand (passwd).

## Automatic login
If you chose it, ly (the login screen on tty1) logs you in at boot: auto_login_user and
auto_login_session in /etc/ly/config.ini, which system.scm writes from #:autologin? in
/etc/config.scm. The screen still locks with your password on sleep, lid close and Super+x
(xss-lock + slock), so a stolen sleeping laptop is locked, but a stolen powered-off one boots to
your desktop. To turn it off: #:autologin? #f in /etc/config.scm, then
sudo guix system reconfigure /etc/config.scm. Without disk encryption, anyone with the laptop
can read the disk anyway: Rassvet does not encrypt it (yet).

## Software
Every package is in the read-only store, named by a hash of its whole recipe. Guix and Nonguix
channel commits are checked against their signers' keys on every guix pull; substitutes are
accepted only from servers whose keys are in /etc/guix/acl. Rassvet's own channel has no
signed introduction, so it is trusted as GitHub serves it. The Russian material is checked
against published or pinned checksums.

## Network
The firewall is nftables, declared in system.scm: everything coming in is dropped unless it
answers something this laptop asked for (plus loopback, ICMP and mDNS); everything going out
is allowed. Nothing else listens on the network: the tutor (llama-server) and the dictionary
server (kiwix-serve) listen on 127.0.0.1, this computer only. openssh is installed, but no ssh
server runs.

    sudo nft list ruleset             the firewall as it is now
    ss -tlnp                          what is listening
    id                                your groups

References: man sudo ; man nft ; info "(guix) User Accounts" ; rassvet-learn wiki users

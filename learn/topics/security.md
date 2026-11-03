# Users, sudo and trust

You are in the wheel group, so sudo works with your password; the root account has the same
password, for recovery from a console. Other groups give you hardware without sudo: audio,
video, input, network, bluetooth, storage.

## Automatic login
If you chose it, ly (the login screen on tty1) logs you in at boot: auto_login_user and
auto_login_session in /etc/ly/config.ini. It does this once per boot; after logging out it asks.
The screen still locks with your password on sleep, lid close and Super+x (xss-lock + slock), so
a stolen sleeping laptop is locked, but a stolen powered-off one boots to your desktop. To turn
it off, set both keys back to null. Without disk encryption, anyone with the laptop
can read the disk anyway: Pustota does not encrypt it (yet).

## Software
Void's repositories are signed, and XBPS checks every package. Pustota's repository is signed
too, with a key that stays on the computer that builds Pustota; the installer trusted its
public half (ls /var/db/xbps/keys). Packages built from Pustota's templates download only
pinned sources with checksums, and the Russian material is checked the same way. Add
third-party repositories only if you trust them.

## Network
Nothing listens on the network by default except what you start; the tutor (Ollama) and the
dictionary server (kiwix-serve) listen on 127.0.0.1, this computer only. sshd is installed but
not enabled.

    ss -tlnp                          what is listening
    id                                your groups

References: man sudo ; man agetty ; /etc/ly/config.ini (every key explained) ; https://docs.voidlinux.org/config/users-and-groups.html

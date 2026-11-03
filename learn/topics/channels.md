# Channels: where Guix gets its packages

Guix has no package repository in the usual sense. A channel is a Git repository of package
definitions (Scheme); guix pull fetches the channels' newest commits and builds a new guix
command from them. Rassvet follows three, listed in system.scm and written to
/etc/guix/channels.scm:
    guix       https://codeberg.org/guix/guix.git           Guix itself: some 30,000 packages
    nonguix    https://gitlab.com/nonguix/nonguix           the full kernel, firmware, Firefox,
                                                            Steam, Intel's video driver
    rassvet    https://github.com/factionparadox/Pustota    Rassvet: (rassvet packages),
                                                            (rassvet system)

guix pull is per user: yours lands in ~/.config/guix/current, and rassvet-update hands that same
guix to sudo guix system reconfigure, so the system is built from exactly what you pulled.

## Trust
Guix and Nonguix are authenticated: each channel carries an introduction (a first commit and its
signer's OpenPGP fingerprint), and guix pull refuses any commit not signed by a key the channel
itself authorises. Rassvet's channel has no introduction, so its commits are fetched over HTTPS
from GitHub without that check.

Prebuilt packages (substitutes) come from bordeaux.guix.gnu.org and ci.guix.gnu.org for Guix,
and substitutes.nonguix.org for Nonguix. Each server signs what it sends; the keys this system
trusts are in /etc/guix/acl (system.scm adds Nonguix's to Guix's). A substitute has to match the
package definition's hash exactly, so it is the same thing you would have built yourself.

## Look
    guix describe                     the channels and commits your guix was pulled from
    cat /etc/guix/channels.scm
    guix pull --list-generations      every pull you can go back to (guix pull --roll-back)
    guix weather firefox              whether a substitute is ready

References: info "(guix) Channels" ; info "(guix) Substitutes" ; rassvet-learn wiki channels

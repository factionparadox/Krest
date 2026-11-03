# Guix: installing, updating and asking questions

Guix keeps every package in /gnu/store, each in its own read-only folder whose name begins with
a hash of everything that went into it. Nothing is installed "over" anything else, so two
versions can sit side by side, and an update never breaks what is running. A profile is a set
of packages linked together; each change makes a new generation of it, and the old one stays
until you delete it.

There are two kinds of profile:
- the system's (/run/current-system/profile): what system.scm lists, Rassvet's own packages
  included. It changes only through  sudo guix system reconfigure /etc/config.scm.
- yours (~/.guix-profile): what you install with guix install. No sudo needed; each user has
  their own.

## Ask (read-only)
    guix search mpv                 names and descriptions
    guix show mpv                   details: version, dependencies, licence, home page
    guix package -I                 what you installed yourself
    guix package -l                 your profile's generations
    guix size mpv                   how much disk it takes, with everything it needs
    ls /run/current-system/profile/bin    the system's commands

## Change
    rassvet-update                  update the whole system (guix pull, then reconfigure)
    guix install gimp               install for you, with its dependencies
    guix remove gimp                remove it from your profile
    guix upgrade                    update what you installed
    guix package --roll-back        undo your last install, remove or upgrade
    guix shell gimp -- gimp         try a program without installing it
    guix gc                         free the disk: delete store items no generation uses
Shortcuts in your shell: gs (search), gi (install), gr (remove), gu (rassvet-update).

There are no partial upgrades to avoid: every package is built against exact versions of its
dependencies. Prebuilt packages (substitutes) come from Guix's servers and Nonguix's; anything
not prebuilt yet is built on this laptop, which is slower but gives the same result.

References: info "(guix) Package Management" ; rassvet-learn wiki guix-packages

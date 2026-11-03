# Guix packages

Guix is a functional package manager: a package is the result of a build whose every input
(source, dependencies, build script, compiler) is fixed, and it lands in /gnu/store under a
name beginning with a hash of all of them. Change any input and the hash changes, so builds
never overwrite one another, and two versions of anything can coexist. The store is read-only;
only guix-daemon writes to it, which is why ordinary users can install packages safely.

## Profiles and generations
A profile is a folder of links joining a set of store items into one tree (bin/, share/ ...).
  /run/current-system/profile    the system's packages (system.scm's list)
  ~/.guix-profile                yours (a link to /var/guix/profiles/per-user/YOU/guix-profile)
  ~/.config/guix/current         the guix command you pulled (see: channels)
Every change to a profile makes a new generation; the old ones stay, so undoing is a matter of
pointing the link back. Your login shell reads ~/.guix-profile/etc/profile, which sets PATH,
MANPATH, INFOPATH and the rest: after your first guix install, log in again (or source it).

## Everyday use
  guix search word                     search names and descriptions (regular expressions)
  guix show foo                        details: version, inputs, licence, home page
  guix install foo bar                 install for you
  guix remove foo                      remove from your profile
  guix upgrade                         upgrade what you installed (after guix pull)
  guix upgrade foo                     just one
  guix package -I                      what is in your profile (-I regexp: matching ones)
  guix package -A word                 every available package matching, with versions
  guix install foo@1.2                 a specific version, if the channels have it
Add --dry-run (-n) to see what would be built or downloaded, without doing it.
The system's packages change only through reconfigure (see: system).

## Going back
  guix package -l                      your profile's generations and what each changed
  guix package --roll-back             to the previous one
  guix package -S 5                    to generation 5
  guix package -d 1m                   delete generations older than a month
The same for the system: guix system list-generations / roll-back / switch-generation /
delete-generations; and for guix itself: guix pull -l / --roll-back.

## Manifests: a profile as a file
  guix package --export-manifest > ~/manifest.scm    what you have, as Scheme
  guix package -m ~/manifest.scm                     make the profile exactly that
A manifest moves your programs to another machine, or keeps them under Git.

## The store and garbage collection
Nothing is deleted when you remove a package or a generation: the store items stay until the
garbage collector finds that no generation (of any profile, the system's included) needs them.
  guix gc                              delete everything unused
  guix gc -F 20G                       delete until 20 GB are free
  guix gc -d 2m                        delete your generations older than 2 months, then collect
  guix gc --list-roots                 what keeps things alive
  guix gc -R /gnu/store/...-foo        everything foo needs ; --referrers: what needs foo
  sudo guix gc --verify=contents       check the store's files against their hashes
  df -h / ; du -sh /gnu/store

## Substitutes and building
Guix downloads a prebuilt result (a substitute) when a trusted server has one with the same
hash, and builds from source when not; the result is the same either way. guix weather foo
says whether substitutes are available. After a large guix pull, some packages may not be
built on the servers yet: waiting a day, or building, are both fine.

## Grafts
A security fix to a library low in the graph (glibc, openssl) would rebuild thousands of
packages. Guix instead grafts: it rewrites the references in already built packages to point
at the fixed library, which takes minutes. Rassvet's installer works offline, so it installs
without grafts (--no-grafts); the first rassvet-update applies them.

## Errors you may meet
  "package not found"           guix pull first, or the name differs: guix search
  "collision encountered"       two packages in your profile have the same file; the first
                                wins. Harmless, or remove one
  a build fails                 the log's path is printed: less it. guix build --keep-failed
                                keeps the build folder for a look
  disk full                     guix gc, after deleting old generations

See also: guix-tools, guix-packaging, channels, system, from-arch ;
info "(guix) Package Management" ; info "(guix) Invoking guix package" ;
info "(guix) Invoking guix gc" ; https://packages.guix.gnu.org/

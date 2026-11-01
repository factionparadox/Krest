# The Void Handbook, offline

The Void Linux Handbook is Void's official documentation, written by its developers and kept
in step with the system: installation, configuration, XBPS, services. It is installed with
Pustota (package void-docs) in /usr/share/doc/void in four forms:

  markdown/     the source pages, plain text: read them in mc, less or acme
  html/         the website, offline, with its search box
  handbook.pdf  the whole Handbook as one book
  mandoc/       each page as a manual page (section 7)

## Reading it
  pustota-handbook          Midnight Commander with the Handbook on the left and this wiki on
                            the right (also: menu -> Learn -> Void Handbook)
                              arrows and Enter   move into folders
                              F3                 read the page (q, or F10, closes it)
                              /  in the viewer   search the page; n for the next match
                              Tab                the other side
                              Alt+?              find a file by name, or by text inside it
                              F10                quit
  pustota-handbook pdf      the book, in zathura (j/k scroll, / search, q quits)
  pustota-handbook web      the offline website, in Firefox
  void-docs xbps            Void's own reader: finds the pages matching a word and shows one
                            (it picks a viewer; -m for the Markdown, -r for the man page)
  man FILE.7                the mandoc form, as a manual page:
                            man /usr/share/doc/void/mandoc/config/services/index.7

## Where it fits
The Handbook says how Void is meant to be used; this wiki explains the same system at more
length, with Pustota's own choices; the lessons (pustota-learn learn) are the short tour. When
they disagree, the Handbook and the manual pages are right.

See also: index ; man void-docs ; https://docs.voidlinux.org ;
https://github.com/void-linux/void-docs (to suggest corrections)

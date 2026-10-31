# ratpoison: one window, the whole screen

ratpoison is a window manager without decorations, overlapping windows or mouse handling.
Every window fills its frame; at first there is one frame, the whole screen. You move between
windows with the keyboard, like tabs in a terminal multiplexer (screen, tmux).

## Windows and frames
- Super+Tab / Super+Shift+Tab: next / previous window. Super+`: the list. Super+0-9: by number.
- Super+s splits the frame side by side, Super+Shift+s top and bottom; Super+arrows move
  between frames; Super+Shift+arrows swap windows; Super+x removes a frame; Super+o goes back
  to one.
- Super+q closes a window.

## ratpoison's own keys
Everything Super does is also ratpoison's prefix key, Ctrl+t, followed by a letter:
Ctrl+t ? lists them all. Ctrl+t : lets you type any ratpoison command, for example
    :windows       :split      :only      :exec firefox      :source ~/.ratpoisonrc

## Settings
~/.ratpoisonrc sources /etc/pustota/ratpoisonrc, then your lines. Lines are ratpoison commands:
    definekey top s-g exec gimp      Super+g starts GIMP
    set border 0
Reload: Super+Shift+r. The command line tool talks to the running ratpoison:
    ratpoison -c windows ; ratpoison -c "echo hello"

Dialogs that would float elsewhere open centred in the frame. If one gets lost, Super+`.

References: man ratpoison ; https://www.nongnu.org/ratpoison/doc/

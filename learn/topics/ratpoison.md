# ratpoison: one window, the whole screen

ratpoison is a window manager without decorations, overlapping windows or mouse handling.
Every window fills its frame; at first there is one frame, the whole screen. You move between
windows with the keyboard, like tabs in a terminal multiplexer (screen, tmux).

## Workstations, windows and frames
- Super+1-9: workstation 1-9 (ratpoison calls them groups: :groups lists them). Super+Shift+1-9
  sends the window there. The bar shows which one you are on. Super+Tab: pick a window or a
  workstation from a list (krest-overview).
- Super+` / Super+Shift+Tab: next / previous window. Super+q closes one; Super+f makes it
  full size.
- Super+r: this window's width, 33% -> 50% -> 67% -> 100%, with the next window beside it
  (krest-width; like a scrolling layout's columns). It replaces any splits you made.
- Super+\ splits the frame side by side, Super+- top and bottom; Super+arrows move between
  frames; Super+Shift+arrows swap windows; Super+Backspace removes a frame; Super+o goes back
  to one.
- Programs are on Ctrl+Super chords: Ctrl+Super+w the web, t a terminal, e files ...
  (Super+? lists them; krest-open is the script behind them).
- No floating windows and no mouse dragging: every window has a frame.

## ratpoison's own keys
Most of what Super does is also ratpoison's prefix key, Ctrl+t, followed by a letter:
Ctrl+t ? lists them all. Ctrl+t : lets you type any ratpoison command, for example
    :windows       :split      :only      :exec firefox      :source ~/.ratpoisonrc

## Settings
~/.ratpoisonrc sources /etc/krest/ratpoisonrc, then your lines. Lines are ratpoison commands:
    definekey top C-s-i exec gimp    Ctrl+Super+i starts GIMP (once: sudo prt-get depinst gimp)
    set border 0
Reload: Super+Shift+r. The command line tool talks to the running ratpoison:
    ratpoison -c windows ; ratpoison -c "echo hello"

Dialogs that would float elsewhere open centred in the frame. If one gets lost, Super+Tab.

References: man ratpoison ; https://www.nongnu.org/ratpoison/doc/

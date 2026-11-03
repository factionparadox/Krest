# Rassvet ~/.bashrc
[ -z "$PS1" ] && return
PS1='\[\e[1;31m\]\u@\h\[\e[0m\] \w \$ '
alias ls='ls --color=auto' ll='ls -lh' la='ls -lAh'
alias pk='prt-get search' pi='sudo prt-get depinst' pr='sudo prt-get remove' pu='rassvet-update'
alias explain='rassvet-learn explain'

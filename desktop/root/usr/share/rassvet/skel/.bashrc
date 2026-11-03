# Rassvet ~/.bashrc
[ -z "$PS1" ] && return
PS1='\[\e[1;31m\]\u@\h\[\e[0m\] \w \$ '
alias ls='ls --color=auto' ll='ls -lh' la='ls -lAh'
alias gs='guix search' gi='guix install' gr='guix remove' gu='rassvet-update'
alias explain='rassvet-learn explain'

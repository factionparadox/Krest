# Pustota ~/.bashrc
[ -z "$PS1" ] && return
PS1='\[\e[1;31m\]\u@\h\[\e[0m\] \w \$ '
alias ls='ls --color=auto' ll='ls -lh' la='ls -lAh'
alias xi='sudo xbps-install' xq='xbps-query -Rs' xr='sudo xbps-remove -R' xu='sudo xbps-install -Su'
alias explain='pustota-learn explain'

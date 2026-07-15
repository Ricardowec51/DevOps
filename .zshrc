# Enable Powerlevel10k instant prompt. Debe ir al inicio del ~/.zshrc.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# ============================================
# Oh My Zsh
# ============================================
export ZSH="$HOME/.oh-my-zsh"

ZSH_THEME="powerlevel10k/powerlevel10k"

plugins=(
    git
    brew
    macos
    sudo
    extract
    copypath
    colored-man-pages
    history
    kubectl
    terraform
    docker
    docker-compose
    fzf-tab
    zsh-autosuggestions
    zsh-syntax-highlighting
    zsh-completions
    zsh-history-substring-search
)

# Completions (antes de source oh-my-zsh)
fpath+=${ZSH_CUSTOM:-${ZSH:-~/.oh-my-zsh}/custom}/plugins/zsh-completions/src

source $ZSH/oh-my-zsh.sh

# history-substring-search keybindings
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down
bindkey '^[OA' history-substring-search-up
bindkey '^[OB' history-substring-search-down

# ============================================
# Historial
# ============================================
HISTSIZE=50000
SAVEHIST=50000
setopt SHARE_HISTORY
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE

alias hist='history | fzf --tac --no-sort'

# ============================================
# PATH
# ============================================
# Homebrew (Apple Silicon)
if [[ $(uname -m) == 'arm64' ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

export PATH="$HOME/.local/bin:$HOME/bin:$PATH"

# LM Studio CLI
export PATH="/Users/rwagner/.cache/lm-studio/bin:$PATH"

# ============================================
# Herramientas modernas
# ============================================

# eza (reemplazo de ls)
alias ls='eza --icons'
alias ll='eza -alF --icons --git'
alias la='eza -a --icons'
alias tree='eza --tree --icons'

# bat (reemplazo de cat)
alias cat='bat --paging=never'

# fzf
eval "$(fzf --zsh)"

# ============================================
# kubectl — complementa el plugin omz
# ============================================

# Persistent Volumes (el plugin solo tiene PVC)
alias kgpv='kubectl get pv'
alias kdpv='kubectl describe pv'
alias kdelpv='kubectl delete pv'

# Storage Classes
alias kgsc='kubectl get storageclass'
alias kdsc='kubectl describe storageclass'

# Nodos
alias kgnow='kubectl get nodes -o wide'
alias kgnoww='kubectl get nodes -o wide --watch'
alias kcordon='kubectl cordon'
alias kuncordon='kubectl uncordon'
alias kdrain='kubectl drain --ignore-daemonsets --delete-emptydir-data'

# Top / recursos
alias ktopn='kubectl top nodes'
alias ktopp='kubectl top pods'
alias ktoppa='kubectl top pods --all-namespaces'

# Cambio rápido de namespace
kns() { kubectl config set-context --current --namespace="$1" }

# ============================================
# Prompt p10k
# ============================================
# Powerlevel10k desactivado; Starship es el prompt activo
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# ============================================
# zoxide (al final, como requiere)
# ============================================
eval "$(zoxide init zsh)"
alias cd='z'

# ============================================
# Credenciales de Facebook retiradas del .zshrc
eval "$(mise activate zsh)"

# ============================================
# Starship - Terminal Plus
# ============================================
# eval "$(starship init zsh)"
fastfetch

# bun completions
[ -s "/Users/rwagner/.oh-my-zsh/completions/_bun" ] && source "/Users/rwagner/.oh-my-zsh/completions/_bun"

# bun
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

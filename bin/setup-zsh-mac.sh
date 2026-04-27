#!/bin/bash
# =============================================================
# Setup: Zsh + Oh My Zsh + Powerlevel10k + Herramientas modernas
# macOS (Apple Silicon y Intel)
# =============================================================

set -e

# Colores
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[OK]${NC}  $1"; }
warn() { echo -e "${YELLOW}[>>]${NC}  $1"; }
err()  { echo -e "${RED}[ERR]${NC} $1"; exit 1; }
sep()  { echo -e "\n${GREEN}── $1 ──────────────────────────────${NC}"; }

# No correr como root
[[ $EUID -eq 0 ]] && err "No ejecutar como root."

sep "Homebrew"
if ! command -v brew &>/dev/null; then
    warn "Instalando Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Activar brew en la sesión actual
if [[ $(uname -m) == 'arm64' ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
else
    eval "$(/usr/local/bin/brew shellenv)"
fi
log "Homebrew $(brew --version | head -1)"

sep "Zsh"
if ! command -v zsh &>/dev/null; then
    brew install zsh
fi
ZSH_PATH="$(which zsh)"
if [[ "$SHELL" != "$ZSH_PATH" ]]; then
    warn "Cambiando shell por defecto a zsh..."
    grep -qF "$ZSH_PATH" /etc/shells || echo "$ZSH_PATH" | sudo tee -a /etc/shells
    chsh -s "$ZSH_PATH"
fi
log "zsh $(zsh --version | awk '{print $2}')"

sep "Oh My Zsh"
if [[ ! -d "$HOME/.oh-my-zsh" ]]; then
    warn "Instalando Oh My Zsh..."
    RUNZSH=no CHSH=no sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
else
    git -C "$HOME/.oh-my-zsh" pull --quiet
    log "Oh My Zsh actualizado"
fi

sep "Powerlevel10k"
P10K_DIR="$HOME/.oh-my-zsh/custom/themes/powerlevel10k"
if [[ ! -d "$P10K_DIR" ]]; then
    warn "Instalando Powerlevel10k..."
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$P10K_DIR"
else
    git -C "$P10K_DIR" pull --quiet
fi
log "Powerlevel10k listo"

sep "Plugins"
ZSH_CUSTOM="$HOME/.oh-my-zsh/custom"

plugin_install() {
    local name="$1" url="$2"
    local dest="$ZSH_CUSTOM/plugins/$name"
    if [[ ! -d "$dest" ]]; then
        warn "Instalando $name..."
        git clone --depth=1 "$url" "$dest"
    else
        git -C "$dest" pull --quiet
    fi
    log "$name listo"
}

plugin_install zsh-autosuggestions     https://github.com/zsh-users/zsh-autosuggestions
plugin_install zsh-syntax-highlighting https://github.com/zsh-users/zsh-syntax-highlighting
plugin_install zsh-completions         https://github.com/zsh-users/zsh-completions

sep "Herramientas modernas"
TOOLS=(eza bat fzf zoxide)
for tool in "${TOOLS[@]}"; do
    if brew list "$tool" &>/dev/null; then
        log "$tool ya instalado"
    else
        warn "Instalando $tool..."
        brew install "$tool"
    fi
done

sep "MesloLGS Nerd Font"
if ls "$HOME/Library/Fonts/MesloLGS"* &>/dev/null 2>&1; then
    log "MesloLGS Nerd Font ya instalada"
else
    warn "Instalando MesloLGS Nerd Font..."
    brew install --cask font-meslo-lg-nerd-font
fi

sep "Cache dirs"
mkdir -p "$HOME/.cache/zsh"
log "Directorios de cache listos"

sep "Escribiendo ~/.zshrc"
[[ -f "$HOME/.zshrc" ]] && cp "$HOME/.zshrc" "$HOME/.zshrc.bak.$(date +%Y%m%d_%H%M%S)" && warn "Backup creado"

# Detectar si es Apple Silicon para el brew path
if [[ $(uname -m) == 'arm64' ]]; then
    BREW_EVAL='eval "$(/opt/homebrew/bin/brew shellenv)"'
else
    BREW_EVAL='eval "$(/usr/local/bin/brew shellenv)"'
fi

cat > "$HOME/.zshrc" << ZSHRC_CONTENT
# Enable Powerlevel10k instant prompt. Debe ir al inicio de ~/.zshrc.
if [[ -r "\${XDG_CACHE_HOME:-\$HOME/.cache}/p10k-instant-prompt-\${(%):-%n}.zsh" ]]; then
  source "\${XDG_CACHE_HOME:-\$HOME/.cache}/p10k-instant-prompt-\${(%):-%n}.zsh"
fi

# ============================================
# Oh My Zsh
# ============================================
export ZSH="\$HOME/.oh-my-zsh"

ZSH_THEME="powerlevel10k/powerlevel10k"

plugins=(
    git
    zsh-autosuggestions
    zsh-syntax-highlighting
    zsh-completions
)

fpath+=\${ZSH_CUSTOM:-\${ZSH:-~/.oh-my-zsh}/custom}/plugins/zsh-completions/src

source \$ZSH/oh-my-zsh.sh

# ============================================
# Historial
# ============================================
HISTSIZE=50000
SAVEHIST=50000
setopt SHARE_HISTORY
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE

# ============================================
# PATH
# ============================================
${BREW_EVAL}
export PATH="\$HOME/.local/bin:\$PATH"

# ============================================
# Herramientas modernas
# ============================================
alias ls='eza --icons'
alias ll='eza -alF --icons --git'
alias la='eza -a --icons'
alias tree='eza --tree --icons'

alias cat='bat --paging=never'

eval "\$(fzf --zsh)"

# ============================================
# Prompt p10k
# ============================================
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# ============================================
# zoxide (al final)
# ============================================
eval "\$(zoxide init zsh)"
alias cd='z'
ZSHRC_CONTENT

log "~/.zshrc escrito"

# ============================================
echo ""
echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Instalación completada en macOS    ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
echo ""
echo "  Pasos finales:"
echo "  1. Abre una nueva terminal"
echo "  2. Cambia la fuente a: MesloLGS Nerd Font Regular"
echo "  3. Ejecuta: p10k configure"
echo ""

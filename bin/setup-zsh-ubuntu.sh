#!/bin/bash
# =============================================================
# Setup: Zsh + Oh My Zsh + Powerlevel10k + Herramientas modernas
# Ubuntu / Debian
# =============================================================

set -e

# Colores
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[OK]${NC}  $1"; }
warn() { echo -e "${YELLOW}[>>]${NC}  $1"; }
err()  { echo -e "${RED}[ERR]${NC} $1"; exit 1; }
sep()  { echo -e "\n${GREEN}── $1 ──────────────────────────────${NC}"; }

# No correr como root
[[ $EUID -eq 0 ]] && err "No ejecutar como root. Usa tu usuario normal con sudo disponible."

# Verificar Ubuntu/Debian
[[ -f /etc/debian_version ]] || err "Este script es para Ubuntu/Debian."

sep "Dependencias base"
sudo apt update -y
sudo apt install -y zsh git curl wget unzip fontconfig build-essential
log "Dependencias instaladas"

sep "Zsh como shell por defecto"
ZSH_PATH="$(which zsh)"
if [[ "$SHELL" != "$ZSH_PATH" ]]; then
    warn "Cambiando shell por defecto a zsh (necesita logout/login para aplicar)..."
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

sep "eza"
if command -v eza &>/dev/null; then
    log "eza ya instalado ($(eza --version | head -1))"
else
    warn "Instalando eza desde repositorio oficial..."
    sudo mkdir -p /etc/apt/keyrings
    wget -qO- https://raw.githubusercontent.com/eza-community/eza/main/deb.asc \
        | sudo gpg --dearmor -o /etc/apt/keyrings/gierens.gpg
    echo "deb [signed-by=/etc/apt/keyrings/gierens.gpg] http://deb.gierens.de stable main" \
        | sudo tee /etc/apt/sources.list.d/gierens.list > /dev/null
    sudo chmod 644 /etc/apt/keyrings/gierens.gpg /etc/apt/sources.list.d/gierens.list
    sudo apt update -y && sudo apt install -y eza
    log "eza instalado"
fi

sep "bat"
mkdir -p "$HOME/.local/bin"
if command -v bat &>/dev/null; then
    log "bat ya instalado"
elif command -v batcat &>/dev/null; then
    # Ubuntu/Debian instala como batcat, creamos symlink
    ln -sf "$(which batcat)" "$HOME/.local/bin/bat"
    log "bat (symlink a batcat) creado"
else
    warn "Instalando bat..."
    sudo apt install -y bat 2>/dev/null || true
    # Intentar con batcat si bat no está
    if command -v batcat &>/dev/null && ! command -v bat &>/dev/null; then
        ln -sf "$(which batcat)" "$HOME/.local/bin/bat"
    fi
    log "bat instalado"
fi

sep "fzf"
if command -v fzf &>/dev/null; then
    log "fzf ya instalado ($(fzf --version))"
else
    warn "Instalando fzf..."
    if [[ ! -d "$HOME/.fzf" ]]; then
        git clone --depth 1 https://github.com/junegunn/fzf.git "$HOME/.fzf"
    fi
    "$HOME/.fzf/install" --all --no-bash --no-fish --no-update-rc
    log "fzf instalado"
fi

sep "zoxide"
if command -v zoxide &>/dev/null; then
    log "zoxide ya instalado ($(zoxide --version))"
else
    warn "Instalando zoxide..."
    curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh
    log "zoxide instalado"
fi

sep "MesloLGS Nerd Font"
FONT_DIR="$HOME/.local/share/fonts/MesloLGS"
if ls "$FONT_DIR"/*.ttf &>/dev/null 2>&1; then
    log "MesloLGS Nerd Font ya instalada"
else
    warn "Descargando MesloLGS Nerd Font..."
    mkdir -p "$FONT_DIR"
    BASE="https://github.com/romkatv/powerlevel10k-media/raw/master"
    FONTS=(
        "MesloLGS NF Regular.ttf"
        "MesloLGS NF Bold.ttf"
        "MesloLGS NF Italic.ttf"
        "MesloLGS NF Bold Italic.ttf"
    )
    for font in "${FONTS[@]}"; do
        encoded="${font// /%20}"
        curl -fsSL -o "$FONT_DIR/$font" "$BASE/$encoded"
    done
    fc-cache -f "$FONT_DIR"
    log "MesloLGS Nerd Font instalada"
fi

sep "Cache dirs"
mkdir -p "$HOME/.cache/zsh"
log "Directorios de cache listos"

sep "Escribiendo ~/.zshrc"
[[ -f "$HOME/.zshrc" ]] && cp "$HOME/.zshrc" "$HOME/.zshrc.bak.$(date +%Y%m%d_%H%M%S)" && warn "Backup creado"

cat > "$HOME/.zshrc" << 'ZSHRC_CONTENT'
# Enable Powerlevel10k instant prompt. Debe ir al inicio de ~/.zshrc.
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
    zsh-autosuggestions
    zsh-syntax-highlighting
    zsh-completions
)

fpath+=${ZSH_CUSTOM:-${ZSH:-~/.oh-my-zsh}/custom}/plugins/zsh-completions/src

source $ZSH/oh-my-zsh.sh

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
export PATH="$HOME/.local/bin:$PATH"

# ============================================
# Herramientas modernas
# ============================================
alias ls='eza --icons'
alias ll='eza -alF --icons --git'
alias la='eza -a --icons'
alias tree='eza --tree --icons'

alias cat='bat --paging=never'

# fzf (instalado en ~/.fzf si fue por git)
[[ -f ~/.fzf.zsh ]] && source ~/.fzf.zsh || eval "$(fzf --zsh 2>/dev/null)"

# ============================================
# Prompt p10k
# ============================================
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# ============================================
# zoxide (al final)
# ============================================
eval "$(zoxide init zsh)"
alias cd='z'
ZSHRC_CONTENT

log "~/.zshrc escrito"

# ============================================
echo ""
echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Instalación completada en Ubuntu   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
echo ""
echo "  Pasos finales:"
echo "  1. Cierra la sesión y vuelve a entrar (para que zsh sea el shell por defecto)"
echo "     O ejecuta ahora mismo: exec zsh"
echo "  2. En tu emulador de terminal, cambia la fuente a: MesloLGS NF Regular"
echo "  3. Ejecuta: p10k configure"
echo ""

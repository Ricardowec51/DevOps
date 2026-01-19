#!/bin/bash
# ==============================================================================
# Script Post-Instalacion VMs - No Interactivo (Auto)
# Basado en init-script.sh de Ricardo
# Pasos: Expandir Disco, Actualizar, Utilitarios, Hora, Zsh+Aliases
# ==============================================================================

set -e
export DEBIAN_FRONTEND=noninteractive

LOG="/var/log/init-script-auto.log"
exec > >(tee -a "$LOG") 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') - Iniciando configuracion post-instalacion..."

# ------------------------------------------------------------------------------
# Paso 8: Expandir disco LVM (PRIMERO para tener espacio)
# ------------------------------------------------------------------------------
echo ">>> Paso 8: Expandiendo disco LVM..."
ROOT_PART=$(findmnt / -no SOURCE)
DISK=$(lsblk -no pkname $ROOT_PART | head -n 1)

if [[ $ROOT_PART == /dev/mapper/* ]]; then
    PV_DEVICE=$(pvs --noheadings -o pv_name | xargs)
    PART_NUM=$(echo $PV_DEVICE | grep -o '[0-9]*$')
    LV_PATH=$(lvs --noheadings -o lv_path | xargs)

    swapoff -a || true
    parted /dev/$DISK resizepart $PART_NUM 100% --script || true
    pvresize $PV_DEVICE || true
    lvextend -l +100%FREE $LV_PATH || true
    resize2fs $LV_PATH || true
    echo ">>> Disco expandido: $(df -h / | tail -1 | awk '{print $2}')"
else
    echo ">>> No se detecto LVM, omitiendo expansion."
fi

# ------------------------------------------------------------------------------
# Paso 3: Actualizar sistema
# ------------------------------------------------------------------------------
echo ">>> Paso 3: Actualizando sistema..."
apt-get update
apt-get upgrade -y
apt-get autoremove -y
echo ">>> Sistema actualizado."

# ------------------------------------------------------------------------------
# Paso 4: Instalar utilitarios
# ------------------------------------------------------------------------------
echo ">>> Paso 4: Instalando utilitarios..."
apt-get install -y neofetch glances net-tools htop curl git wget vim
echo ">>> Utilitarios instalados."

# ------------------------------------------------------------------------------
# Paso 5: Configurar hora (Ecuador)
# ------------------------------------------------------------------------------
echo ">>> Paso 5: Configurando zona horaria..."
timedatectl set-timezone America/Guayaquil
timedatectl set-ntp on
echo ">>> Zona horaria: $(timedatectl show --property=Timezone --value)"

# ------------------------------------------------------------------------------
# Paso 6: Instalar Zsh + Oh My Zsh + Honukai + Aliases
# ------------------------------------------------------------------------------
echo ">>> Paso 6: Instalando Zsh..."
apt-get install -y zsh git curl wget fonts-powerline locales-all

# Configurar para usuario rwagner
USER_HOME="/home/rwagner"
USER_NAME="rwagner"

if [ -d "$USER_HOME" ]; then
    echo ">>> Instalando Oh My Zsh para $USER_NAME..."

    # Instalar Oh My Zsh
    if [ ! -d "$USER_HOME/.oh-my-zsh" ]; then
        sudo -u $USER_NAME sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    fi

    ZSH_CUSTOM="$USER_HOME/.oh-my-zsh/custom"

    # Plugins
    sudo -u $USER_NAME mkdir -p "$ZSH_CUSTOM/plugins" "$ZSH_CUSTOM/themes"

    if [ ! -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]; then
        sudo -u $USER_NAME git clone https://github.com/zsh-users/zsh-autosuggestions.git "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
    fi

    if [ ! -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]; then
        sudo -u $USER_NAME git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"
    fi

    if [ ! -d "$ZSH_CUSTOM/plugins/zsh-completions" ]; then
        sudo -u $USER_NAME git clone https://github.com/zsh-users/zsh-completions.git "$ZSH_CUSTOM/plugins/zsh-completions"
    fi

    # Tema Honukai
    if [ ! -f "$ZSH_CUSTOM/themes/honukai.zsh-theme" ]; then
        sudo -u $USER_NAME curl -o "$ZSH_CUSTOM/themes/honukai.zsh-theme" https://raw.githubusercontent.com/oskarkrawczyk/honukai-iterm/master/honukai.zsh-theme
    fi

    # Crear .zshrc con aliases personalizados y neofetch al inicio
    cat > "$USER_HOME/.zshrc" << 'ZSHRC'
# Zsh + Oh My Zsh + Honukai
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="honukai"

plugins=(
    git
    zsh-autosuggestions
    zsh-syntax-highlighting
    zsh-completions
)

source $ZSH/oh-my-zsh.sh

# zsh-completions
fpath+=${ZSH_CUSTOM:-${ZSH:-~/.oh-my-zsh}/custom}/plugins/zsh-completions/src
autoload -Uz compinit
mkdir -p "${XDG_CACHE_HOME:-$HOME/.cache}/zsh"
compinit -d "${XDG_CACHE_HOME:-$HOME/.cache}/zsh/.zcompdump"

# Historial
HISTSIZE=50000
SAVEHIST=50000
setopt SHARE_HISTORY

# ============================================
# Aliases Personalizados
# ============================================
alias l='ls -lt'
alias ll='ls -alF'
alias la='ls -A'
alias k='kubectl'
alias kgp='kubectl get pods -A'
alias kgn='kubectl get nodes'
alias kga='kubectl get all -A'
alias myip='curl -s ifconfig.me'
alias update='sudo apt update && sudo apt upgrade -y'

# ============================================
# Ejecutar neofetch al iniciar
# ============================================
neofetch

ZSHRC

    chown $USER_NAME:$USER_NAME "$USER_HOME/.zshrc"
    chsh -s "$(which zsh)" $USER_NAME
    echo ">>> Zsh configurado para $USER_NAME."
fi

# ------------------------------------------------------------------------------
# Resumen
# ------------------------------------------------------------------------------
echo ""
echo "============================================"
echo "  CONFIGURACION COMPLETADA"
echo "============================================"
echo "Hostname:  $(hostname)"
echo "IP:        $(hostname -I | awk '{print $1}')"
echo "Disco:     $(df -h / | tail -1 | awk '{print $2" usado "$5}')"
echo "Hora:      $(date)"
echo "============================================"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Script finalizado."

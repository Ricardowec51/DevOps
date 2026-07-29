#!/bin/bash

# ==============================================================================
# Script Post-Instalación Ubuntu 24.04/22.04 - Optimizado por AntiGravity & Ricardo
# ==============================================================================

set -e  # Salir en caso de error

# Colores para mejor legibilidad
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Estado de los pasos (N = No ejecutado, S = Ejecutado)
step1_status="N"; step2_status="N"; step3_status="N"; step4_status="N"
step5_status="N"; step6_status="N"; step7_status="N"; step8_status="N"
step9_status="N"; step10_status="N"

# ------------------------------------------------------------------------------
# Funciones de Resumen
# ------------------------------------------------------------------------------

print_summary() {
    echo -e "\n${BLUE}┌──────────────────────────────────────────────────────────────┬──────────────┐${NC}"
    echo -e "${BLUE}│ Actividad                                                   │ Ejecutado    │${NC}"
    echo -e "${BLUE}├──────────────────────────────────────────────────────────────┼──────────────┤${NC}"
    printf "│ %-60s │ %-10s │\n" "Configurar sudo sin pedir contraseña" "$step1_status"
    printf "│ %-60s │ %-10s │\n" "Instalación de qemu-guest-agent" "$step2_status"
    printf "│ %-60s │ %-10s │\n" "Actualización del servidor" "$step3_status"
    printf "│ %-60s │ %-10s │\n" "Instalación de utilitarios modernos" "$step4_status"
    printf "│ %-60s │ %-10s │\n" "Sincronización de hora y NTP" "$step5_status"
    printf "│ %-60s │ %-10s │\n" "Instalación Pro de Zsh (Honukai)" "$step6_status"
    printf "│ %-60s │ %-10s │\n" "Añadir nuevo usuario sudo" "$step7_status"
    printf "│ %-60s │ %-10s │\n" "Expansión automática de disco LVM" "$step8_status"
    printf "│ %-60s │ %-10s │\n" "Instalación de Docker" "$step9_status"
    printf "│ %-60s │ %-10s │\n" "Instalación de Portainer CE" "$step10_status"
    echo -e "${BLUE}└──────────────────────────────────────────────────────────────┴──────────────┘${NC}"
}

print_system_info() {
    echo -e "\n${GREEN}===========================================${NC}"
    echo -e "${GREEN}       Resumen del Entorno de Trabajo      ${NC}"
    echo -e "${GREEN}===========================================${NC}"
    echo "Nombre del Servidor:    $(hostname)"
    echo "Nombre del Usuario:     $(logname 2>/dev/null || echo $USER)"
    
    OS_INFO=$(lsb_release -ds 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2)
    echo "Versión del S.O.:       $OS_INFO"
    echo "Versión del Kernel:    $(uname -r)"
    
    echo -e "\nEstatus del Disco (/):"
    df -h / | tail -1 | awk '{print "  Tamaño: "$2" | Usado: "$3" | Disponible: "$4" | Uso%: "$5}'
    
    echo -e "\nEstatus de Memoria:"
    free -h | awk '/^Mem:/ {print "  Total: "$2" | Usada: "$3" | Libre: "$4}'
    
    echo -e "\nDatos de Red:"
    echo "  IP Local:    $(hostname -I | awk '{print $1}')"
    echo "  IP Externa:  $(curl -s ifconfig.me || echo "Desconocida")"
    echo "==========================================="
}

# ------------------------------------------------------------------------------
# Pasos de Configuración
# ------------------------------------------------------------------------------

paso1() {
    echo -e "${BLUE}Paso 1: Configurar sudo sin contraseña.${NC}"
    if sudo -n true 2>/dev/null; then
        echo "Sudo ya está configurado sin contraseña."
    else
        echo "$(logname 2>/dev/null || echo $USER) ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/$(logname 2>/dev/null || echo $USER) > /dev/null
        sudo chmod 0440 /etc/sudoers.d/$(logname 2>/dev/null || echo $USER)
        echo -e "${GREEN}Configuración completada.${NC}"
    fi
    step1_status="S"
}

paso2() {
    echo -e "${BLUE}Paso 2: Instalación de qemu-guest-agent.${NC}"
    sudo apt update && sudo apt install -y qemu-guest-agent
    sudo systemctl enable --now qemu-guest-agent
    step2_status="S"
}

paso3() {
    echo -e "${BLUE}Paso 3: Actualización del servidor.${NC}"
    sudo apt update && sudo apt upgrade -y && sudo apt autoremove -y
    step3_status="S"
}

paso4() {
    echo -e "${BLUE}Paso 4: Instalación de utilitarios.${NC}"
    OS_VERSION=$(lsb_release -rs 2>/dev/null || echo "22.04")
    UTIL_FETCH="fastfetch"
    if [[ "$OS_VERSION" < "24.04" ]]; then UTIL_FETCH="neofetch"; fi
    
    sudo apt install -y $UTIL_FETCH speedtest-cli glances cockpit net-tools htop curl git
    step4_status="S"
}

paso5() {
    echo -e "${BLUE}Paso 5: Sincronización de hora (Ecuador).${NC}"
    sudo timedatectl set-timezone America/Guayaquil
    sudo timedatectl set-ntp on
    step5_status="S"
}

paso6() {
    echo -e "${BLUE}Paso 6: Instalación Pro de Zsh (Zsh + OMZ + Honukai).${NC}"
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SCRIPT_ZSH="$SCRIPT_DIR/my_zsh_install.sh"
    if [ -f "$SCRIPT_ZSH" ]; then
        bash "$SCRIPT_ZSH"
    else
        echo -e "${YELLOW}Script de Zsh no encontrado localmente. Intentando descarga...${NC}"
        curl -fsSL https://raw.githubusercontent.com/Ricardowec51/Initial/main/my_zsh_install.sh -o my_zsh_install.sh
        chmod +x my_zsh_install.sh
        ./my_zsh_install.sh
    fi
    step6_status="S"
}

paso7() {
    echo -e "${BLUE}Paso 7: Añadir nuevo usuario sudo.${NC}"
    read -p "Nombre del nuevo usuario: " newuser
    if id "$newuser" &>/dev/null; then echo "El usuario ya existe."; else
        sudo adduser --gecos "" --disabled-password "$newuser"
        echo "$newuser:$newuser" | sudo chpasswd
        sudo usermod -aG sudo "$newuser"
        echo -e "${GREEN}Usuario $newuser creado.${NC}"
    fi
    step7_status="S"
}

paso8() {
    echo -e "${BLUE}Paso 8: Expansión de disco LVM.${NC}"
    ROOT_PART=$(findmnt / -no SOURCE)
    DISK=$(lsblk -no pkname $ROOT_PART | head -n 1)
    if [[ $ROOT_PART == /dev/mapper/* ]]; then
        PV_DEVICE=$(sudo pvs --noheadings -o pv_name | xargs)
        PART_NUM=$(echo $PV_DEVICE | grep -o '[0-9]*$')
        LV_PATH=$(sudo lvs --noheadings -o lv_path | xargs)
        
        sudo swapoff -a || true
        sudo parted /dev/$DISK resizepart $PART_NUM 100%
        sudo pvresize $PV_DEVICE
        sudo lvextend -l +100%FREE $LV_PATH
        sudo resize2fs $LV_PATH
        echo -e "${GREEN}Disco expandido.${NC}"
    else
        echo -e "${RED}No se detectó LVM en la raíz.${NC}"
    fi
    step8_status="S"
}

paso9() {
    echo -e "${BLUE}Paso 9: Instalación de Docker.${NC}"
    sudo apt update
    sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io
    sudo usermod -aG docker $(logname 2>/dev/null || echo $USER)
    echo -e "${GREEN}Docker instalado.${NC}"
    step9_status="S"
}

paso10() {
    echo -e "${BLUE}Paso 10: Instalación de Portainer CE.${NC}"
    if command -v docker &>/dev/null; then
        sudo docker volume create portainer_data
        sudo docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always \
            -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data \
            portainer/portainer-ce:latest
        echo -e "${GREEN}Portainer en ejecución en puerto 9443.${NC}"
    else
        echo -e "${RED}Docker no está instalado. Ejecute el paso 9 primero.${NC}"
    fi
    step10_status="S"
}

# ------------------------------------------------------------------------------
# Menú Principal
# ------------------------------------------------------------------------------

clear
echo -e "${GREEN}======================================================${NC}"
echo -e "${GREEN}   SCRIPT POST-INSTALACIÓN INTEGRAL - RICARDO & AG    ${NC}"
echo -e "${GREEN}======================================================${NC}"
echo "1) Configurar Sudo (Sin Contraseña)"
echo "2) Instalar QEMU Guest Agent"
echo "3) Actualización de Sistema"
echo "4) Instalar Utilitarios (Fastfetch, Glances, etc.)"
echo "5) Ajustar Hora (Ecuador)"
echo "6) Instalar Zsh Pro (Oh My Zsh + Honukai)"
echo "7) Crear nuevo Usuario Sudo"
echo "8) Expandir Disco LVM (Automático)"
echo "9) Instalar Docker"
echo "10) Instalar Portainer CE"
echo "11) EJECUTAR TODOS LOS PASOS"
echo "0) Salir"
echo "------------------------------------------------------"
read -p "Selecciona una opción [0-11]: " opcion

case $opcion in
    1) paso1 ;;
    2) paso2 ;;
    3) paso3 ;;
    4) paso4 ;;
    5) paso5 ;;
    6) paso6 ;;
    7) paso7 ;;
    8) paso8 ;;
    9) paso9 ;;
    10) paso10 ;;
    11) 
        paso1; paso2; paso3; paso4; paso5; paso6; paso7; paso8; paso9; paso10 
        ;;
    0) exit 0 ;;
    *) echo "Opción no válida" ;;
esac

print_summary
print_system_info

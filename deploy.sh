#!/bin/bash
#===============================================================================
# deploy.sh - Sincroniza el proyecto a la VM Admin (k3s-admin)
#===============================================================================
# Uso: ./deploy.sh [opciones]
#
# Opciones:
#   --setup              Ejecuta setup_admin_vm.sh despues del sync
#   --run                Ejecuta main.py interactivo (requiere TTY)
#   --action <accion>    Ejecuta accion headless (sin menu)
#   --confirm            Confirma acciones destructivas
#
# Ejemplos:
#   ./deploy.sh                              # Solo sincronizar
#   ./deploy.sh --setup                      # Sync + instalar dependencias
#   ./deploy.sh --action list-actions        # Ver acciones disponibles
#   ./deploy.sh --action check-vms           # Verificar VMs
#   ./deploy.sh --action dry-run             # Simular creacion de VMs
#   ./deploy.sh --action create-vms --confirm # Crear VMs
#===============================================================================

set -e

# ============================================================================
# PARSEAR ARGUMENTOS PRIMERO (antes de cualquier otra operacion)
# ============================================================================
DO_SETUP=false
DO_RUN=false
ACTION=""
DO_CONFIRM=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --setup)
            DO_SETUP=true
            shift
            ;;
        --run)
            DO_RUN=true
            shift
            ;;
        --action)
            ACTION="$2"
            shift 2
            ;;
        --confirm|-y)
            DO_CONFIRM=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# ============================================================================
# CONFIGURACION
# ============================================================================
ADMIN_IP="192.168.1.20"
ADMIN_USER="rwagner"
ADMIN_VM_ID="1102"
ADMIN_VM_NAME="k3s-admin"
REMOTE_DIR="/home/${ADMIN_USER}/proxmox-vm-creator"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Archivos/Directorios a excluir del sync
EXCLUDES=(
    "venv/"
    "__pycache__/"
    "*.pyc"
    ".git/"
    "logs/"
    "*.log"
    ".DS_Store"
    "k3s-backup-*/"
    "*.backup.*"
    "k3sup-darwin-*"
)

# Construir argumentos de exclusion para rsync
EXCLUDE_ARGS=""
for excl in "${EXCLUDES[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude=$excl"
done

# ============================================================================
# BANNER
# ============================================================================
echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║       PROXMOX VM CREATOR - Deploy to Admin VM                 ║"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo "║  Target: ${ADMIN_USER}@${ADMIN_IP} (${ADMIN_VM_NAME})                       ║"
echo "║  Remote: ${REMOTE_DIR}                    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================================
# SYNC
# ============================================================================

# Verificar conectividad SSH
echo -e "${YELLOW}[1/4] Verificando conectividad SSH...${NC}"
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes ${ADMIN_USER}@${ADMIN_IP} "echo 'OK'" &>/dev/null; then
    echo -e "${RED}ERROR: No se puede conectar a ${ADMIN_USER}@${ADMIN_IP}${NC}"
    echo "Verifica que:"
    echo "  1. La VM Admin (${ADMIN_VM_NAME}) este encendida"
    echo "  2. Tu clave SSH este configurada"
    echo "  3. El usuario ${ADMIN_USER} exista en la VM"
    exit 1
fi
echo -e "${GREEN}   -> Conexion OK${NC}"

# Crear directorio remoto si no existe
echo -e "${YELLOW}[2/4] Preparando directorio remoto...${NC}"
ssh ${ADMIN_USER}@${ADMIN_IP} "mkdir -p ${REMOTE_DIR}"
echo -e "${GREEN}   -> Directorio listo${NC}"

# Sincronizar con rsync
echo -e "${YELLOW}[3/4] Sincronizando archivos con rsync...${NC}"
rsync -avz --progress --delete \
    $EXCLUDE_ARGS \
    ./ ${ADMIN_USER}@${ADMIN_IP}:${REMOTE_DIR}/

echo -e "${GREEN}   -> Sincronizacion completada${NC}"

# Ajustar permisos
echo -e "${YELLOW}[4/4] Ajustando permisos en destino...${NC}"
ssh ${ADMIN_USER}@${ADMIN_IP} "cd ${REMOTE_DIR} && chmod +x *.sh *.py 2>/dev/null || true"
echo -e "${GREEN}   -> Permisos ajustados${NC}"

# ============================================================================
# EJECUTAR ACCIONES POST-SYNC
# ============================================================================

# Ejecutar setup si se solicito
if $DO_SETUP; then
    echo ""
    echo -e "${CYAN}[Extra] Ejecutando setup_admin_vm.sh en destino...${NC}"
    ssh -t ${ADMIN_USER}@${ADMIN_IP} "cd ${REMOTE_DIR} && ./setup_admin_vm.sh"
fi

# Ejecutar accion headless si se especifico
if [[ -n "$ACTION" ]]; then
    echo ""
    echo -e "${CYAN}[Extra] Ejecutando accion headless: ${ACTION}${NC}"
    CONFIRM_FLAG=""
    if $DO_CONFIRM; then
        CONFIRM_FLAG="--confirm"
    fi
    ssh ${ADMIN_USER}@${ADMIN_IP} "cd ${REMOTE_DIR} && source venv/bin/activate && python3 main.py --action ${ACTION} ${CONFIRM_FLAG}"
    exit $?
fi

# Ejecutar menu interactivo si se solicito (requiere TTY)
if $DO_RUN; then
    echo ""
    echo -e "${CYAN}[Extra] Ejecutando main.py interactivo en destino...${NC}"
    ssh -t ${ADMIN_USER}@${ADMIN_IP} "cd ${REMOTE_DIR} && source venv/bin/activate && python3 main.py"
    exit $?
fi

# ============================================================================
# RESUMEN FINAL (solo si no se ejecuto nada)
# ============================================================================
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    DEPLOY COMPLETADO                          ║${NC}"
echo -e "${GREEN}╠═══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  Modo headless (desde aqui):                                  ║${NC}"
echo -e "${GREEN}║    ./deploy.sh --action list-actions                          ║${NC}"
echo -e "${GREEN}║    ./deploy.sh --action check-vms                             ║${NC}"
echo -e "${GREEN}║    ./deploy.sh --action dry-run                               ║${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}║  Menu interactivo (via SSH):                                  ║${NC}"
echo -e "${GREEN}║    ssh ${ADMIN_USER}@${ADMIN_IP}                                       ║${NC}"
echo -e "${GREEN}║    cd ~/proxmox-vm-creator && ./launch.sh                     ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"

#!/bin/bash
#
# Script para actualizar config.yaml para usar imágenes desde NFS_SERVER
#

set -e

CONFIG_FILE="config.yaml"

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Actualizando config.yaml para usar NFS_SERVER               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Backup del config actual
echo -e "${YELLOW}📋 Creando backup de config.yaml...${NC}"
cp "$CONFIG_FILE" "${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${GREEN}✅ Backup creado${NC}"
echo ""

# Actualizar las rutas de imágenes
echo -e "${BLUE}🔧 Actualizando rutas de cloud images...${NC}"

# Usar sed para actualizar las rutas (compatible con macOS)
sed -i '' \
    -e 's|ubuntu22:.*|ubuntu22: "NFS_SERVER:iso/jammy-server-cloudimg-amd64.img"|' \
    -e 's|ubuntu24:.*|ubuntu24: "NFS_SERVER:iso/noble-server-cloudimg-amd64.img"|' \
    -e 's|debian12:.*|debian12: "NFS_SERVER:iso/debian-12-generic-amd64.qcow2"|' \
    -e 's|debian13:.*|debian13: "NFS_SERVER:iso/debian-13-generic-amd64.qcow2"|' \
    "$CONFIG_FILE"

echo -e "${GREEN}✅ config.yaml actualizado${NC}"
echo ""

echo -e "${BLUE}📝 Nuevas configuraciones:${NC}"
grep -A4 "images:" "$CONFIG_FILE"

echo ""
echo -e "${GREEN}🎉 ¡Configuración actualizada exitosamente!${NC}"
echo ""
echo -e "${YELLOW}📝 Ahora puedes crear las VMs con:${NC}"
echo "   ./create_vm.py"
echo ""

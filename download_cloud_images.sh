#!/bin/bash
#
# Script para descargar cloud images a NFS_SERVER en Proxmox
# Uso: ./download_cloud_images.sh <usuario@host-proxmox>
# Ejemplo: ./download_cloud_images.sh root@192.168.1.143
#

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Debes especificar el host de Proxmox${NC}"
    echo "Uso: $0 <usuario@host-proxmox>"
    echo "Ejemplo: $0 root@192.168.1.143"
    exit 1
fi

PROXMOX_HOST="$1"
NFS_PATH="/mnt/pve/NFS_SERVER/template/iso"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Descargando Cloud Images a NFS_SERVER                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📡 Host Proxmox: ${PROXMOX_HOST}${NC}"
echo -e "${YELLOW}📁 Ruta NFS: ${NFS_PATH}${NC}"
echo ""

# Verificar conectividad SSH
echo -e "${BLUE}🔍 Verificando conectividad SSH...${NC}"
if ! ssh -o ConnectTimeout=5 "$PROXMOX_HOST" "exit" 2>/dev/null; then
    echo -e "${RED}❌ Error: No se puede conectar a ${PROXMOX_HOST}${NC}"
    echo "Verifica que:"
    echo "  - El host es correcto"
    echo "  - Tienes acceso SSH configurado"
    echo "  - Las credenciales son correctas"
    exit 1
fi
echo -e "${GREEN}✅ Conexión SSH exitosa${NC}"
echo ""

# Verificar que el directorio NFS existe
echo -e "${BLUE}🔍 Verificando directorio NFS_SERVER...${NC}"
if ! ssh "$PROXMOX_HOST" "test -d ${NFS_PATH}"; then
    echo -e "${RED}❌ Error: Directorio ${NFS_PATH} no existe${NC}"
    echo "Intentando rutas alternativas..."

    # Buscar ruta alternativa
    ALT_PATH=$(ssh "$PROXMOX_HOST" "find /mnt -type d -name 'NFS_SERVER' 2>/dev/null | head -1")
    if [ -n "$ALT_PATH" ]; then
        NFS_PATH="${ALT_PATH}/template/iso"
        echo -e "${YELLOW}⚠️  Usando ruta alternativa: ${NFS_PATH}${NC}"
    else
        echo -e "${RED}❌ No se pudo encontrar el storage NFS_SERVER${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✅ Directorio NFS_SERVER encontrado${NC}"
echo ""

# Crear script de descarga en el servidor
echo -e "${BLUE}📝 Creando script de descarga en Proxmox...${NC}"

ssh "$PROXMOX_HOST" "bash -s" << 'ENDSSH'
#!/bin/bash

# Colores para SSH
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NFS_PATH="/mnt/pve/NFS_SERVER/template/iso"

# Verificar si existe, sino buscar ruta alternativa
if [ ! -d "$NFS_PATH" ]; then
    NFS_PATH=$(find /mnt -type d -name 'NFS_SERVER' 2>/dev/null | head -1)
    NFS_PATH="${NFS_PATH}/template/iso"
fi

cd "$NFS_PATH" || exit 1

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Descargando Cloud Images                                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📁 Directorio de trabajo: $(pwd)${NC}"
echo ""

# Función para descargar imagen
download_image() {
    local name="$1"
    local url="$2"
    local filename="$3"

    echo -e "${BLUE}📥 Descargando ${name}...${NC}"

    if [ -f "$filename" ]; then
        echo -e "${YELLOW}⚠️  Archivo ya existe: ${filename}${NC}"
        read -p "¿Sobrescribir? (s/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            echo -e "${YELLOW}⏭️  Omitiendo ${name}${NC}"
            return 0
        fi
        rm -f "$filename"
    fi

    if wget --progress=bar:force "$url" -O "${filename}.tmp" 2>&1; then
        mv "${filename}.tmp" "$filename"
        local size=$(du -h "$filename" | cut -f1)
        echo -e "${GREEN}✅ ${name} descargada (${size})${NC}"
        return 0
    else
        echo -e "${RED}❌ Error descargando ${name}${NC}"
        rm -f "${filename}.tmp"
        return 1
    fi
}

# Descargar imágenes
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

download_image \
    "Ubuntu 22.04 LTS (Jammy)" \
    "https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img" \
    "jammy-server-cloudimg-amd64.img"

echo ""
download_image \
    "Ubuntu 24.04 LTS (Noble)" \
    "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img" \
    "noble-server-cloudimg-amd64.img"

echo ""
download_image \
    "Debian 12 (Bookworm)" \
    "https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.qcow2" \
    "debian-12-generic-amd64.qcow2"

echo ""
download_image \
    "Debian 13 (Trixie)" \
    "https://cloud.debian.org/images/cloud/trixie/latest/debian-13-generic-amd64.qcow2" \
    "debian-13-generic-amd64.qcow2"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}📋 Resumen de archivos descargados:${NC}"
echo ""
ls -lh jammy-server-cloudimg-amd64.img 2>/dev/null && echo -e "${GREEN}✅ Ubuntu 22.04${NC}" || echo -e "${RED}❌ Ubuntu 22.04${NC}"
ls -lh noble-server-cloudimg-amd64.img 2>/dev/null && echo -e "${GREEN}✅ Ubuntu 24.04${NC}" || echo -e "${RED}❌ Ubuntu 24.04${NC}"
ls -lh debian-12-generic-amd64.qcow2 2>/dev/null && echo -e "${GREEN}✅ Debian 12${NC}" || echo -e "${RED}❌ Debian 12${NC}"
ls -lh debian-13-generic-amd64.qcow2 2>/dev/null && echo -e "${GREEN}✅ Debian 13${NC}" || echo -e "${RED}❌ Debian 13${NC}"

echo ""
echo -e "${GREEN}🎉 Proceso completado${NC}"

ENDSSH

echo ""
echo -e "${GREEN}✅ Script ejecutado en Proxmox${NC}"
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Verificando imágenes en NFS_SERVER                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar que las imágenes existen
ssh "$PROXMOX_HOST" "ls -lh ${NFS_PATH}/*.{img,qcow2} 2>/dev/null | grep -E 'jammy|noble|debian-1[23]' || echo 'No se encontraron imágenes'"

echo ""
echo -e "${GREEN}🎉 ¡Proceso completado!${NC}"
echo ""
echo -e "${YELLOW}📝 Siguiente paso:${NC}"
echo "Actualiza el archivo config.yaml con las nuevas rutas:"
echo ""
echo "  images:"
echo "    ubuntu22: \"NFS_SERVER:iso/jammy-server-cloudimg-amd64.img\""
echo "    ubuntu24: \"NFS_SERVER:iso/noble-server-cloudimg-amd64.img\""
echo "    debian12: \"NFS_SERVER:iso/debian-12-generic-amd64.qcow2\""
echo "    debian13: \"NFS_SERVER:iso/debian-13-generic-amd64.qcow2\""
echo ""

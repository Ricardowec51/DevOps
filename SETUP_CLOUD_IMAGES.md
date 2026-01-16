# Setup Cloud Images en NFS_SERVER

Guía para descargar y configurar cloud images en el storage compartido NFS_SERVER.

## 📋 Requisitos

- Acceso SSH a uno de los nodos de Proxmox
- Storage NFS_SERVER configurado y accesible
- Conexión a Internet en el nodo de Proxmox

## 🚀 Proceso de Setup

### Paso 1: Descargar Cloud Images a NFS_SERVER

Ejecuta el script de descarga desde tu máquina local:

```bash
cd /Users/rwagner/proxmox-vm-creator
./download_cloud_images.sh root@192.168.1.143
```

**Nota:** Reemplaza `root@192.168.1.143` con el usuario y IP de tu servidor Proxmox.

Este script descargará:
- ✅ Ubuntu 22.04 LTS (Jammy) - ~660 MB
- ✅ Ubuntu 24.04 LTS (Noble) - ~600 MB
- ✅ Debian 12 (Bookworm) - ~500 MB
- ✅ Debian 13 (Trixie) - ~500 MB

**Tiempo estimado:** 5-10 minutos dependiendo de tu conexión.

### Paso 2: Actualizar config.yaml

Ejecuta el script para actualizar automáticamente las rutas:

```bash
./update_config_for_nfs.sh
```

O actualiza manualmente `config.yaml`:

```yaml
defaults:
  images:
    ubuntu22: "NFS_SERVER:iso/jammy-server-cloudimg-amd64.img"
    ubuntu24: "NFS_SERVER:iso/noble-server-cloudimg-amd64.img"
    debian12: "NFS_SERVER:iso/debian-12-generic-amd64.qcow2"
    debian13: "NFS_SERVER:iso/debian-13-generic-amd64.qcow2"
```

### Paso 3: Verificar las Imágenes

Verifica que las imágenes están disponibles:

```bash
./venv/bin/python check_images.py
```

Deberías ver las 4 cloud images listadas en NFS_SERVER.

### Paso 4: Crear las VMs Faltantes

Ahora puedes crear las VMs que fallaron anteriormente:

```bash
# Dry-run para verificar
./venv/bin/python create_vm.py --dry-run

# Crear VMs reales
./venv/bin/python create_vm.py
```

## 🔍 Verificación Manual (Opcional)

Si prefieres verificar manualmente vía SSH:

```bash
# Conectarse al nodo Proxmox
ssh root@192.168.1.143

# Ir al directorio de ISOs en NFS_SERVER
cd /mnt/pve/NFS_SERVER/template/iso/

# Listar cloud images
ls -lh *.img *.qcow2 | grep -E "jammy|noble|debian"

# Verificar tamaños
du -h jammy-server-cloudimg-amd64.img
du -h noble-server-cloudimg-amd64.img
du -h debian-12-generic-amd64.qcow2
du -h debian-13-generic-amd64.qcow2
```

## ⚠️ Troubleshooting

### Error: No se puede conectar vía SSH

```bash
# Verificar conectividad
ping 192.168.1.143

# Verificar acceso SSH
ssh -v root@192.168.1.143
```

### Error: Directorio NFS_SERVER no existe

El script intenta encontrarlo automáticamente. Si falla:

```bash
# En el servidor Proxmox
find /mnt -name "NFS_SERVER" -type d

# Actualizar NFS_PATH en el script si es necesario
```

### Error: Descarga interrumpida

Las descargas pueden reanudarse. Ejecuta el script de nuevo y selecciona sobrescribir (s) cuando pregunte.

### Cloud images ya existen

El script te preguntará si quieres sobrescribir. Responde:
- `s` - Para sobrescribir
- `n` - Para omitir

## 📊 Estado Actual de las VMs

**VMs creadas exitosamente:**
- ✅ VM 2004 - legacy-server (msa)
- ✅ VM 2012 - k8s-worker-02 (msa)

**VMs que faltan por crear:**
- ❌ VM 2001 - web-prod-01 (Nnuc13)
- ❌ VM 2002 - db-prod-01 (DELL)
- ❌ VM 2005 - vpn-server (msn2)
- ❌ VM 2010 - k8s-master-01 (BOSC)
- ❌ VM 2011 - k8s-worker-01 (DELL)

Después de completar el setup, estas 5 VMs se crearán correctamente.

## 🎯 Beneficios de usar NFS_SERVER

✅ **Storage compartido** - Todas las imágenes disponibles en todos los nodos
✅ **Ahorro de espacio** - Una sola copia para todo el cluster
✅ **Fácil mantenimiento** - Actualizar imágenes en un solo lugar
✅ **Respaldo automático** - Si NFS_SERVER tiene backup configurado

## 📚 Referencias

- [Ubuntu Cloud Images](https://cloud-images.ubuntu.com/)
- [Debian Cloud Images](https://cloud.debian.org/images/cloud/)
- [Proxmox Cloud-Init](https://pve.proxmox.com/wiki/Cloud-Init_Support)

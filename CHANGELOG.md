# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [3.1.0] - 2026-01-15

### Agregado
- **SSH keys URL encoding** - Fix crítico para soporte completo de múltiples llaves SSH
- Scripts automatizados para descarga de cloud images a NFS_SERVER
- `download_cloud_images.sh` - Descarga Ubuntu 22.04, 24.04, Debian 12, 13 a NFS compartido
- `update_config_for_nfs.sh` - Actualiza config.yaml para usar NFS_SERVER
- `SETUP_CLOUD_IMAGES.md` - Documentación completa del proceso de setup
- Helpers útiles: `list_vms.py`, `list_nodes.py`, `check_vms.py`, `check_images.py`, `delete_vm.py`
- Conversión automática de rutas NFS_SERVER:iso/ a paths absolutos

### Corregido
- **CRÍTICO:** SSH keys ahora se codifican en URL usando `urllib.parse.quote()`
  - Error anterior: `'invalid urlencoded string'`
  - Solución: Múltiples keys separadas por `%0A` (newline URL-encoded)
- Nombres de nodos corregidos:
  - `Nuc13` → `Nnuc13`
  - `msa2` → `msn2`
  - Agregado: `nuc10`
- Conversión de image paths para `import-from`:
  - `NFS_SERVER:iso/file.img` (fallaba con error "wrong type 'iso'")
  - → `/mnt/pve/NFS_SERVER/template/iso/file.img` (funciona correctamente)

### Cambiado
- Cloud images ahora en NFS_SERVER (storage compartido entre todos los nodos)
- Storage por defecto: `local-lvm` → `NFS_SERVER`
- Rutas de imágenes actualizadas de `/var/lib/vz/` a `NFS_SERVER:iso/`

### Detalles Técnicos
- Python 3.14 compatible
- proxmoxer 2.0.1
- PyYAML 6.0.1
- urllib.parse.quote() para encoding de SSH keys
- Total cloud images: ~2.1 GB en NFS_SERVER

### Deployment Exitoso
- ✅ 7 VMs creadas en cluster Proxmox
- Distribución: BOSC (1), DELL (2), Nnuc13 (1), msa (2), msn2 (1)
- Todas con SSH keys configuradas, QEMU Agent, y cloud-init

## [3.0.0] - 2026-01-10

### Agregado
- Soporte completo para cloud images (Ubuntu, Debian, Rocky Linux)
- Configuración mediante cloud-init
- QEMU Guest Agent habilitado automáticamente
- Templates reutilizables para tipos comunes de servidores
- Modo `--dry-run` para simulación sin crear VMs
- Logging detallado con archivos de log
- Soporte para vendor snippets personalizados
- Configuración de red estática o DHCP
- Claves SSH configurables
- Tags para organización de VMs
- Auto-start de VMs opcional

### Cambiado
- Migración de imágenes ISO a cloud images
- Simplificación de configuración YAML
- Mejora en manejo de errores y validaciones

### Corregido
- Validación de credenciales Proxmox
- Manejo de excepciones en creación de VMs

## [2.0.0] - 2026-01-09

### Agregado
- Uso de biblioteca `proxmoxer` para API de Proxmox
- Creación básica de VMs
- Configuración mediante archivos YAML
- Logs básicos

### Cambiado
- Refactorización completa del código
- Separación de configuración en archivos YAML

## [1.0.0] - Fecha anterior

### Agregado
- Primera versión funcional
- Script básico con `paramiko` y `requests`
- Creación manual de VMs

# Guía Rápida - Proxmox VM Creator v3.1.0

Guía completa para crear, gestionar y eliminar VMs en Proxmox usando cloud images.

## 📋 Índice

1. [Procedimiento para Crear e Iniciar VMs](#procedimiento-para-crear-e-iniciar-vms)
2. [Procedimiento para Eliminar VMs](#procedimiento-para-eliminar-vms)
3. [Scripts Disponibles](#scripts-disponibles)
4. [Troubleshooting](#troubleshooting)

---

## 🚀 Procedimiento para Crear e Iniciar VMs

### Paso 1: Configurar VMs a Crear

Edita el archivo `vms.yaml` con las especificaciones de tus VMs:

```yaml
vms:
  - vmid: 2001
    name: "mi-servidor"
    node: "Nnuc13"              # Nodo donde se creará
    memory: 4096                # RAM en MB
    cores: 4                    # Número de CPUs
    disk_size: "50G"            # Tamaño del disco
    network_type: "static"      # "static" o "dhcp"
    ip: "192.168.1.100"         # IP (si es static)
    tags: "web,production"      # Tags opcionales
    start: true                 # Iniciar automáticamente tras crear
```

### Paso 2: Verificar Configuración (Dry-Run)

**Siempre** haz un dry-run primero para verificar que todo esté bien:

```bash
cd /Users/rwagner/proxmox-vm-creator
./venv/bin/python create_vm.py --dry-run
```

Esto te mostrará:
- Cuántas VMs se crearán
- Configuración de cada una
- Sin crear nada realmente

### Paso 3: Crear las VMs

Una vez verificado, crea las VMs realmente:

```bash
./venv/bin/python create_vm.py
```

**Nota:** Las VMs se crean pero quedan en estado "stopped" (apagadas).

**Salida esperada:**
```
🚀 Creando VM 2001 (mi-servidor) en Nnuc13...
  🔑 Configuradas 2 SSH key(s)
  ✅ VM 2001 creada
     Imagen: ubuntu22
     RAM: 4096MB
     CPU: 4 cores
     QEMU Agent: Habilitado
     Cloud-init: Configurado

✅ Exitosas: 1
❌ Fallidas: 0
```

### Paso 4: Iniciar las VMs

Hay **3 formas** de iniciar las VMs:

#### Opción A: Iniciar todas automáticamente (Recomendado)

```bash
./venv/bin/python start_vms.py
```

Este script:
- Inicia todas las VMs definidas en el código
- Muestra el progreso
- Verifica que se iniciaron correctamente

#### Opción B: Configurar auto-start en vms.yaml

Agrega `start: true` en el YAML:

```yaml
vms:
  - vmid: 2001
    name: "mi-servidor"
    node: "Nnuc13"
    start: true    # ← Esto inicia la VM automáticamente tras crearla
```

#### Opción C: Iniciar manualmente vía SSH

```bash
ssh root@192.168.1.143 "qm start 2001"
```

### Paso 5: Verificar Estado de las VMs

Verifica que todo esté corriendo:

```bash
./venv/bin/python check_vms.py
```

**Salida esperada:**
```
🔍 Verificando VMs creadas:
🟢 VM 2001: mi-servidor (running) - Nodo: Nnuc13
```

### Paso 6: Conectar a las VMs vía SSH

Espera ~30-60 segundos para que cloud-init complete la configuración inicial, luego:

```bash
ssh rwagner@192.168.1.100
```

**Nota:** Usa el usuario configurado en `.env` (variable `VM_DEFAULT_USER`).

---

## 🗑️ Procedimiento para Eliminar VMs

### Opción 1: Script Automático (Recomendado)

**SÍ existe un script** para eliminar VMs de forma segura:

```bash
./venv/bin/python delete_vm.py <NODO> <VMID>
```

**Ejemplos:**

```bash
# Eliminar VM 2001 del nodo Nnuc13
./venv/bin/python delete_vm.py Nnuc13 2001

# Eliminar VM 2002 del nodo DELL
./venv/bin/python delete_vm.py DELL 2002
```

**¿Qué hace el script?**
1. Verifica si la VM está corriendo
2. Si está corriendo, la detiene primero
3. Espera 3 segundos
4. Elimina la VM completamente
5. Confirma que se eliminó

**Salida esperada:**
```
🗑️  Eliminando VM 2001 del nodo Nnuc13...
  ⏸️  Deteniendo VM...
  ✅ VM 2001 eliminada exitosamente
```

### Opción 2: Eliminar Múltiples VMs

Para eliminar varias VMs a la vez:

```bash
# Método 1: Comando encadenado
./venv/bin/python delete_vm.py Nnuc13 2001 && \
./venv/bin/python delete_vm.py DELL 2002 && \
./venv/bin/python delete_vm.py msa 2004

# Método 2: Loop en bash
for vm in 2001 2002 2004; do
    ./venv/bin/python delete_vm.py <NODO> $vm
done
```

### Opción 3: Manual vía SSH

```bash
# Detener VM
ssh root@192.168.1.143 "qm stop 2001"

# Eliminar VM
ssh root@192.168.1.143 "qm destroy 2001"
```

**⚠️ ADVERTENCIA:** La eliminación es **PERMANENTE**. No hay forma de recuperar la VM después.

---

## 🛠️ Scripts Disponibles

### Scripts Principales

| Script | Descripción | Uso |
|--------|-------------|-----|
| `create_vm.py` | Crea VMs según vms.yaml | `./venv/bin/python create_vm.py` |
| `start_vms.py` | Inicia todas las VMs | `./venv/bin/python start_vms.py` |
| `delete_vm.py` | Elimina una VM específica | `./venv/bin/python delete_vm.py <nodo> <vmid>` |
| `check_vms.py` | Verifica estado de VMs | `./venv/bin/python check_vms.py` |
| `list_vms.py` | Lista todas las VMs del cluster | `./venv/bin/python list_vms.py` |
| `list_nodes.py` | Lista nodos del cluster | `./venv/bin/python list_nodes.py` |

### Scripts de Utilidades

| Script | Descripción | Uso |
|--------|-------------|-----|
| `check_images.py` | Verifica cloud images disponibles | `./venv/bin/python check_images.py` |
| `check_nfs_storage.py` | Inspecciona NFS_SERVER | `./venv/bin/python check_nfs_storage.py` |
| `check_vm_status.py` | Estado detallado de VMs | `./venv/bin/python check_vm_status.py` |

### Scripts de Setup

| Script | Descripción | Uso |
|--------|-------------|-----|
| `download_cloud_images.sh` | Descarga cloud images a NFS | `./download_cloud_images.sh root@IP` |
| `update_config_for_nfs.sh` | Actualiza config.yaml | `./update_config_for_nfs.sh` |

---

## 🔧 Troubleshooting

### Problema: VM no inicia

**Síntoma:**
```
⏳ VM 2001 (mi-servidor) - Iniciando... ⚠️  Estado: stopped
```

**Solución:**
1. Verificar logs:
   ```bash
   ./venv/bin/python check_vm_status.py
   ```

2. Si hay "lock timeout":
   ```bash
   # Esperar 30 segundos y reintentar
   sleep 30
   ./venv/bin/python start_vms.py
   ```

### Problema: Error al crear VM

**Síntoma:**
```
❌ Error: unable to create VM 2001 - VM 2001 already exists
```

**Solución:**
```bash
# Eliminar la VM existente primero
./venv/bin/python delete_vm.py <nodo> 2001

# Reintentar creación
./venv/bin/python create_vm.py
```

### Problema: No puedo conectar vía SSH

**Síntoma:**
```
ssh rwagner@192.168.1.100
Connection refused
```

**Solución:**
1. Verificar que la VM esté corriendo:
   ```bash
   ./venv/bin/python check_vms.py
   ```

2. Esperar que cloud-init complete (puede tomar 1-2 minutos):
   ```bash
   # Desde la consola de Proxmox
   ssh root@192.168.1.143
   qm terminal 2001
   # Luego ver:
   cloud-init status
   ```

3. Verificar IP configurada:
   ```bash
   # En la consola de la VM
   ip addr show
   ```

### Problema: SSH keys no funcionan

**Síntoma:**
```
ssh rwagner@192.168.1.100
Permission denied (publickey)
```

**Solución:**
1. Verificar que las keys están en `.env`:
   ```bash
   cat .env | grep VM_SSH_KEYS
   ```

2. Usar password temporalmente:
   ```bash
   ssh rwagner@192.168.1.100
   # Password: el configurado en VM_DEFAULT_PASSWORD
   ```

3. Revisar logs de cloud-init en la VM:
   ```bash
   cat /var/log/cloud-init.log | grep ssh
   ```

---

## 📚 Flujo Completo Recomendado

### Crear un Nuevo Servidor

```bash
# 1. Editar vms.yaml con la nueva VM
nano vms.yaml

# 2. Verificar con dry-run
./venv/bin/python create_vm.py --dry-run

# 3. Crear la VM
./venv/bin/python create_vm.py

# 4. Iniciar la VM
./venv/bin/python start_vms.py

# 5. Esperar 1 minuto para cloud-init
sleep 60

# 6. Conectar vía SSH
ssh rwagner@<IP_DE_LA_VM>

# 7. Verificar cloud-init completado
cloud-init status
```

### Eliminar un Servidor

```bash
# 1. Listar VMs para encontrar la correcta
./venv/bin/python list_vms.py

# 2. Eliminar la VM
./venv/bin/python delete_vm.py <NODO> <VMID>

# 3. Verificar que se eliminó
./venv/bin/python list_vms.py
```

### Recrear una VM

```bash
# 1. Eliminar VM existente
./venv/bin/python delete_vm.py <NODO> <VMID>

# 2. Esperar 10 segundos
sleep 10

# 3. Verificar que vms.yaml tiene la configuración correcta
nano vms.yaml

# 4. Crear la VM nuevamente
./venv/bin/python create_vm.py

# 5. Iniciar la VM
./venv/bin/python start_vms.py
```

---

## 📖 Documentación Adicional

- **README.md** - Overview completo del proyecto
- **SETUP_CLOUD_IMAGES.md** - Setup inicial de cloud images en NFS
- **CHANGELOG.md** - Historial de cambios y versiones
- **SESSION_SUMMARY.md** - Resumen de la última sesión
- **GUIA_RAPIDA.md** - Este documento

## 🆘 Ayuda

Si tienes problemas:

1. Revisa los logs:
   ```bash
   tail -100 vm_creation.log
   ```

2. Verifica estado del cluster:
   ```bash
   ./venv/bin/python list_nodes.py
   ./venv/bin/python list_vms.py
   ```

3. Consulta la documentación completa en `README.md`

---

**Versión:** 3.1.0
**Última actualización:** 2026-01-15
**Autor:** Ricardo Wagner

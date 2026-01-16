# Primeros Pasos - Guía para Nuevos Usuarios

Esta guía te llevará paso a paso desde cero hasta crear tu primera VM. Tiempo estimado: **20 minutos**.

## ✅ Pre-requisitos

Antes de empezar, necesitas:
- ✅ Acceso a un servidor Proxmox VE (IP, usuario, contraseña)
- ✅ Python 3.8+ instalado en tu máquina
- ✅ Este proyecto clonado en tu máquina

## 📝 Paso 1: Configurar Credenciales (5 minutos)

### 1.1 Copiar archivo de ejemplo

```bash
cd /Users/rwagner/proxmox-vm-creator
cp .env.example .env
```

### 1.2 Editar credenciales

```bash
nano .env
```

Edita estos valores con tus datos de Proxmox:

```bash
# Conexión a Proxmox
PROXMOX_HOST="192.168.1.143"        # ← Tu IP de Proxmox
PROXMOX_USER="root@pam"             # ← Tu usuario
PROXMOX_PASSWORD="tu_password_aqui" # ← Tu contraseña
PROXMOX_VERIFY_SSL="false"

# Usuario por defecto en las VMs (cloud-init)
VM_DEFAULT_USER="rwagner"           # ← Tu usuario preferido
VM_DEFAULT_PASSWORD="temporal123"   # ← Contraseña temporal

# SSH Keys (opcional pero recomendado)
VM_SSH_KEYS="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDe..."
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

### 1.3 Proteger el archivo

```bash
chmod 600 .env
```

## 🖼️ Paso 2: Verificar Cloud Images (5 minutos)

Las cloud images son imágenes pre-construidas de sistemas operativos (Ubuntu, Debian) optimizadas para virtualización.

### 2.1 Verificar si ya están descargadas

```bash
./venv/bin/python check_images.py
```

### 2.2 Si NO están descargadas, ejecutar:

```bash
# Ver guía detallada
cat SETUP_CLOUD_IMAGES.md

# O usar el script automático
./download_cloud_images.sh root@192.168.1.143
```

Esto descargará ~2.1 GB de imágenes (Ubuntu 22.04, 24.04, Debian 12, 13) al storage compartido.

**Importante:** Este paso se hace **SOLO UNA VEZ**. Las imágenes quedan disponibles para siempre.

## 📋 Paso 3: Definir tu Primera VM (3 minutos)

### 3.1 Copiar archivo de ejemplo

```bash
cp vms.yaml.example vms.yaml
```

### 3.2 Editar con tu VM

```bash
nano vms.yaml
```

**Ejemplo simple (borra todo y copia esto):**

```yaml
vms:
  - vmid: 2100                    # ID único (elige uno libre)
    name: "mi-primera-vm"         # Nombre descriptivo
    node: "Nnuc13"                # Nodo donde crearla
    template: "small"             # 2GB RAM, 2 cores, 50G disk
    network_type: "static"        # Usar IP fija
    ip: "192.168.1.150"           # IP fija (elige una libre en tu red)
    start: true                   # Iniciar automáticamente
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

### 3.3 Verificar nodos disponibles

Si no estás seguro de qué nodo usar:

```bash
./venv/bin/python list_nodes.py
```

Verás algo como:
```
📊 Nodos Proxmox:
  🟢 Nnuc13 (online)
  🟢 DELL (online)
  🟢 BOSC (online)
```

## 🧪 Paso 4: Probar con Dry-Run (2 minutos)

Antes de crear nada, verifica que todo esté bien configurado:

```bash
./venv/bin/python create_vm.py --dry-run
```

**Salida esperada:**
```
================================================================================
📋 PARÁMETROS DE EJECUCIÓN
================================================================================
Archivo de VMs: vms.yaml
Modo: DRY-RUN (Simulación)
================================================================================

🔍 Simulando creación de VM 2100 (mi-primera-vm) en Nnuc13...
  ✓ Configuración válida
  ✓ Nodo Nnuc13 disponible
  ✓ VMID 2100 libre

✅ Todo está correcto para crear 1 VM
```

Si ves errores, corrígelos antes de continuar.

## 🚀 Paso 5: Crear la VM (2 minutos)

Una vez que el dry-run pase sin errores:

```bash
./venv/bin/python create_vm.py
```

**Salida esperada:**
```
🚀 Creando VM 2100 (mi-primera-vm) en Nnuc13...
  🔑 Configuradas 1 SSH key(s)
  ✅ VM 2100 creada exitosamente en 3.45s
     └─ Imagen: ubuntu22
     └─ RAM: 2048MB
     └─ CPU: 2 cores
     └─ QEMU Agent: Habilitado
     └─ Cloud-init: Configurado

✅ Exitosas: 1
❌ Fallidas: 0
⏱️  Tiempo total: 3.45s
```

**Nota:** Como pusiste `start: true`, la VM se iniciará automáticamente.

## ✅ Paso 6: Verificar Estado (1 minuto)

```bash
./venv/bin/python check_vms.py
```

**Salida esperada:**
```
🔍 Verificando VMs creadas:
🟢 VM 2100: mi-primera-vm (running) - Nodo: Nnuc13
```

## 🔌 Paso 7: Conectar a la VM (2 minutos)

### 7.1 Esperar que cloud-init complete

Cloud-init configura el sistema operativo al primer arranque. Espera ~60 segundos:

```bash
sleep 60
```

### 7.2 Conectar vía SSH

```bash
ssh rwagner@192.168.1.150
```

Si configuraste SSH keys en `.env`, no pedirá contraseña. Si no, usa la contraseña que pusiste en `VM_DEFAULT_PASSWORD`.

### 7.3 Verificar que todo funciona

Una vez dentro de la VM:

```bash
# Verificar cloud-init completó
cloud-init status

# Debe mostrar: status: done

# Ver información del sistema
uname -a
cat /etc/os-release
```

## 🎉 ¡Felicidades!

Has creado tu primera VM usando Proxmox VM Creator. La VM:
- ✅ Está creada en Proxmox
- ✅ Está corriendo
- ✅ Tiene Ubuntu 22.04 instalado
- ✅ Tiene tu usuario configurado
- ✅ Acepta conexiones SSH

## 📚 Siguientes Pasos

Ahora que sabes lo básico:

1. **Crear múltiples VMs:** Edita `vms.yaml` y agrega más VMs
2. **Usar diferentes templates:** Prueba `medium`, `large`, `web-server`, `db-server`
3. **Ver logs detallados:** `cat logs/vm_creation_*.log`
4. **Explorar comandos:** Lee `GUIA_RAPIDA.md`

## 🆘 Troubleshooting

### Problema: "Error connecting to Proxmox"

**Solución:** Verifica credenciales en `.env`
```bash
cat .env | grep PROXMOX_HOST
cat .env | grep PROXMOX_USER
```

### Problema: "VM 2100 already exists"

**Solución:** Ese VMID ya está en uso. Cámbialo en `vms.yaml`:
```yaml
vmid: 2101  # ← Cambiar a otro número
```

O elimina la VM existente:
```bash
./venv/bin/python delete_vm.py Nnuc13 2100
```

### Problema: "Image ubuntu22 not found"

**Solución:** Las cloud images no están descargadas. Ejecuta:
```bash
./download_cloud_images.sh root@192.168.1.143
```

### Problema: "Cannot connect via SSH"

**Solución:**
1. Espera más tiempo (cloud-init puede tardar 1-2 minutos)
2. Verifica la VM está corriendo: `./venv/bin/python check_vms.py`
3. Verifica la IP es correcta y no está en uso por otra máquina

## 📖 Documentación Adicional

- **[README.md](README.md)** - Guía completa del proyecto
- **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** - Todos los comandos disponibles
- **[LOGGING.md](LOGGING.md)** - Sistema de logs
- **[SETUP_CLOUD_IMAGES.md](SETUP_CLOUD_IMAGES.md)** - Detalles de cloud images

---

**¿Preguntas?** Revisa el README.md o GUIA_RAPIDA.md para más detalles.

**Versión:** 3.1.0
**Última actualización:** 2026-01-15

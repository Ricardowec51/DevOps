# Proxmox VM Creator v3.2.0

Herramienta automatizada para crear y configurar máquinas virtuales en Proxmox VE usando **cloud images** y **cloud-init**. Simplifica el despliegue de infraestructura mediante archivos YAML declarativos.

## 🚀 Inicio Rápido para Nuevos Usuarios

**¿Primera vez aquí? Lee esto primero:** **[PRIMEROS_PASOS.md](PRIMEROS_PASOS.md)** - Guía paso a paso de 20 minutos que te lleva desde cero hasta tu primera VM funcionando.

### Resumen Rápido

Si ya sabes lo básico, aquí está el flujo completo:

### 1️⃣ Instalación y Configuración Inicial (5 minutos)

```bash
# 1. Ir al directorio del proyecto
cd /Users/rwagner/proxmox-vm-creator

# 2. El entorno virtual ya está creado, solo instala dependencias
./venv/bin/pip install -r requirements.txt

# 3. Configurar credenciales
cp .env.example .env
nano .env  # Editar con tus credenciales de Proxmox

# 4. Verificar que config.yaml existe
cat config.yaml  # Debe mostrar la configuración
```

### 2️⃣ Preparar Cloud Images (SOLO UNA VEZ)

Las cloud images deben estar en el storage compartido `NFS_SERVER`:

```bash
# Ver guía detallada
cat SETUP_CLOUD_IMAGES.md

# O usar el script automático
./download_cloud_images.sh root@192.168.1.143
```

### 3️⃣ Crear Tu Primera VM (2 minutos)

```bash
# 1. Editar vms.yaml con tu VM
nano vms.yaml

# 2. Verificar con dry-run (NO crea nada, solo simula)
./venv/bin/python create_vm.py --dry-run

# 3. Crear la VM de verdad
./venv/bin/python create_vm.py

# 4. Iniciar la VM
./venv/bin/python start_vms.py

# 5. Verificar que está corriendo
# 5. Verificar estado de ejecución
./venv/bin/python check_vms.py
```

### 4️⃣ Conectar y Verificar

```bash
# 1. Esperar 2-3 minutos para que cloud-init complete (IMPORTANTE)
sleep 180

# 2. Inyección manual de claves (si es necesario)
./force_copy_keys.sh

# 3. Verificar conectividad SSH masiva
./verify_ssh.sh

# 4. Conectar individualmente
ssh rwagner@<IP_DE_TU_VM>
```

## 📚 Documentación Completa

- **[PRIMEROS_PASOS.md](PRIMEROS_PASOS.md)** - ⭐⭐⭐ Guía paso a paso para nuevos usuarios (20 min)
- **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** - ⭐ Procedimientos detallados para crear, iniciar y eliminar VMs
- **[SETUP_CLOUD_IMAGES.md](SETUP_CLOUD_IMAGES.md)** - Setup inicial de cloud images en NFS_SERVER
- **[LOGGING.md](LOGGING.md)** - Sistema de logging y auditoría
- **[INDICE.md](INDICE.md)** - Índice de toda la documentación
- **[CHANGELOG.md](CHANGELOG.md)** - Historial de cambios y versiones

## Características

- Creación automática de VMs usando imágenes cloud (Ubuntu, Debian, Rocky Linux)
- Configuración mediante cloud-init con soporte para:
  - Usuarios y contraseñas personalizados
  - Claves SSH
  - Configuración de red estática o DHCP
  - Scripts personalizados post-instalación (vendor snippets)
- Templates reutilizables para diferentes tipos de servidores
- QEMU Guest Agent habilitado automáticamente
- Modo `--dry-run` para simular creación sin cambios reales
- Logging detallado de todas las operaciones

## Requisitos

### Servidor Proxmox
- Proxmox VE 7.x o superior
- Acceso API (usuario/password)
- Imágenes cloud descargadas en el storage

### Sistema Local
- Python 3.8+
- Dependencias Python (ver `requirements.txt`)

## Instalación

1. Clonar el repositorio:
```bash
git clone <repo-url>
cd proxmox-vm-creator
```

2. Crear entorno virtual e instalar dependencias:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configurar credenciales (IMPORTANTE):
```bash
# Copiar archivo de ejemplo de variables de entorno
cp .env.example .env

# Editar con tus credenciales
nano .env

# Restringir permisos (seguridad)
chmod 600 .env

# Opcional: crear config.yaml para valores no sensibles
cp config.yaml.example config.yaml
```

**IMPORTANTE:** Todas las credenciales sensibles deben ir en `.env`, NO en `config.yaml`. Ver [docs/SECURITY.md](docs/SECURITY.md) para más detalles.

## 📂 Archivos Importantes (¿Qué hace cada archivo?)

### 🔧 Archivos de Configuración

| Archivo | ¿Para qué sirve? | ¿Debo editarlo? |
|---------|------------------|-----------------|
| **`.env`** | Credenciales de Proxmox (user, password, SSH keys) | ✅ SÍ - Copia de `.env.example` y edita con tus datos |
| **`config.yaml`** | Configuración general (red, storage, nodos) | ⚠️ Ya está configurado, revisar si necesitas cambios |
| **`vms.yaml`** | Lista de VMs a crear | ✅ SÍ - Copia de `vms.yaml.example` y define tus VMs |
| **`templates.yaml`** | Plantillas reutilizables (small, medium, large, etc.) | ❌ NO - Ya está listo para usar |

### 🐍 Scripts Python

| Script | ¿Qué hace? | Ejemplo de uso |
|--------|-----------|----------------|
| **`create_vm.py`** | Crea VMs según `vms.yaml` | `./venv/bin/python create_vm.py` |
| **`start_vms.py`** | Inicia todas las VMs | `./venv/bin/python start_vms.py` |
| **`delete_vm.py`** | Elimina una VM específica | `./venv/bin/python delete_vm.py Nnuc13 2001` |
| **`check_vms.py`** | Verifica estado de VMs | `./venv/bin/python check_vms.py` |
| **`list_vms.py`** | Lista todas las VMs del cluster | `./venv/bin/python list_vms.py` |
| **`list_nodes.py`** | Lista nodos disponibles | `./venv/bin/python list_nodes.py` |
| **`delete_all_vms.py`** | **Elimina VMs en lote** (limpieza masiva) | `./venv/bin/python delete_all_vms.py` |

### 📚 Documentación

| Archivo | ¿Qué contiene? |
|---------|----------------|
| **`README.md`** | Este archivo - Guía de inicio |
| **`INDICE.md`** | Índice de toda la documentación |
| **`GUIA_RAPIDA.md`** | Comandos para crear/iniciar/eliminar VMs |
| **`SETUP_CLOUD_IMAGES.md`** | Cómo descargar cloud images (setup inicial) |
| **`LOGGING.md`** | Sistema de logs y auditoría |
| **`CHANGELOG.md`** | Historial de cambios |

### 📁 Directorios

| Directorio | Contenido |
|------------|-----------|
| **`venv/`** | Entorno virtual Python (NO editar) |
| **`logs/`** | Logs de ejecución con timestamp |
| **`examples/`** | Ejemplos de configuración |
| **`docs/`** | Documentación adicional |

## Estructura del Proyecto

```
proxmox-vm-creator/
├── create_vm.py              # ⭐ Script principal para crear VMs
├── start_vms.py              # Iniciar VMs
├── delete_vm.py              # Eliminar VMs
├── check_vms.py              # Verificar estado
│
├── .env                      # 🔐 Credenciales (editar ESTE)
├── .env.example              # Plantilla de credenciales
├── config.yaml               # ⚙️ Configuración general
├── config.yaml.example       # Plantilla de configuración
├── vms.yaml                  # 📝 VMs a crear (editar ESTE)
├── vms.yaml.example          # Plantilla de VMs
├── templates.yaml            # Plantillas predefinidas
│
├── README.md                 # 📖 Esta guía
├── GUIA_RAPIDA.md            # Comandos rápidos
├── INDICE.md                 # Índice de documentación
├── LOGGING.md                # Sistema de logs
│
├── venv/                     # Entorno virtual Python
├── logs/                     # Logs de ejecución
├── examples/                 # Ejemplos
└── docs/                     # Documentación adicional
```

## Configuración

### 1. config.yaml

Archivo principal con credenciales Proxmox, configuración de red, y rutas a imágenes cloud:

```yaml
proxmox:
  host: "192.168.1.143"
  user: "root@pam"
  password: "tu_password"

network:
  bridge: "vmbr0"
  gateway: "192.168.1.1"
  netmask: "24"
  nameserver: "8.8.8.8"

defaults:
  storage: "local-lvm"
  memory: 2048
  cores: 2
  images:
    ubuntu22: "/path/to/jammy-server-cloudimg-amd64.img"
    ubuntu24: "/path/to/noble-server-cloudimg-amd64.img"
```

### 2. vms.yaml - Define QUÉ VMs crear

Este archivo lista las VMs que quieres crear. Puedes usar templates o especificar todo manualmente:

**Ejemplo Simple (con DHCP):**
```yaml
vms:
  - vmid: 2001                    # ID único de la VM (100-999999)
    name: "mi-servidor"           # Nombre descriptivo
    node: "Nnuc13"                # Nodo donde crearla (Nnuc13, DELL, BOSC, msa, msn2)
    template: "web-server"        # Usar template predefinido
```

**Ejemplo Completo (con IP estática):**
```yaml
vms:
  - vmid: 2002
    name: "db-server-01"
    node: "DELL"
    memory: 8192                  # RAM en MB
    cores: 4                      # Número de CPUs
    disk_size: "100G"             # Tamaño del disco
    network_type: "static"        # "static" o "dhcp"
    ip: "192.168.1.100"           # IP fija (solo si es static)
    tags: "database,production"   # Tags opcionales
    start: true                   # Iniciar automáticamente tras crear
```

**Nodos disponibles:**
- `Nnuc13` - Intel NUC
- `DELL` - Servidor Dell
- `BOSC` - Servidor Bosch
- `msa` - Servidor MSA
- `msn2` - Servidor MSN2

### 3. templates.yaml - Define PLANTILLAS reutilizables

Este archivo tiene configuraciones predefinidas que puedes reutilizar. **Ya viene configurado** con estos templates:

```yaml
templates:
  small:                    # VM pequeña
    memory: 2048
    cores: 2
    disk_size: "50G"

  medium:                   # VM mediana
    memory: 4096
    cores: 4
    disk_size: "100G"

  large:                    # VM grande
    memory: 8192
    cores: 8
    disk_size: "200G"

  web-server:               # Servidor web
    memory: 4096
    cores: 4
    disk_size: "50G"

  db-server:                # Base de datos
    memory: 8192
    cores: 6
    disk_size: "200G"

  docker-host:              # Host para Docker
    memory: 8192
    cores: 8
    disk_size: "100G"
```

**Cómo usar templates en vms.yaml:**
```yaml
vms:
  - vmid: 2003
    name: "web-prod-01"
    node: "BOSC"
    template: "web-server"    # ← Usa el template predefinido
    ip: "192.168.1.50"        # Puedes sobrescribir valores
```

## 🛠️ Scripts Disponibles

Este proyecto incluye varios scripts útiles:

### Scripts Principales

| Script | Descripción | Ejemplo de Uso |
|--------|-------------|----------------|
| `create_vm.py` | **Crear VMs** según vms.yaml | `./venv/bin/python create_vm.py` |
| `start_vms.py` | **Iniciar todas las VMs** | `./venv/bin/python start_vms.py` |
| `delete_vm.py` | **Eliminar una VM** específica | `./venv/bin/python delete_vm.py Nnuc13 2001` |
| `check_vms.py` | **Verificar estado** de VMs creadas | `./venv/bin/python check_vms.py` |
| `list_vms.py` | **Listar todas las VMs** del cluster | `./venv/bin/python list_vms.py` |
| `list_nodes.py` | **Listar nodos** con estado | `./venv/bin/python list_nodes.py` |

### Scripts de Utilidades

| Script | Descripción |
|--------|-------------|
| `check_images.py` | Verifica cloud images disponibles |
| `check_nfs_storage.py` | Inspecciona contenido de NFS_SERVER |
| `check_vm_status.py` | Estado detallado de VMs específicas |
| `download_cloud_images.sh` | Descarga cloud images a NFS_SERVER |
| `update_config_for_nfs.sh` | Actualiza config.yaml para NFS |
| `verify_ssh.sh` | **Verifica acceso SSH** a rango de IPs 21-28 |
| `force_copy_keys.sh` | **Fuerza inyección SSH** usando `ssh-copy-id` |

**Ver [GUIA_RAPIDA.md](GUIA_RAPIDA.md) para ejemplos detallados de uso.**

## Uso

### Modo Dry-Run (Simulación)

Verifica la configuración sin crear VMs reales:

```bash
./create_vm.py --dry-run
```

### Crear VMs

Crea todas las VMs definidas en `vms.yaml`:

```bash
./create_vm.py
```

### Opciones Adicionales

```bash
# Usar archivos de configuración personalizados
./create_vm.py --config mi-config.yaml --vms mis-vms.yaml

# Ver ayuda
./create_vm.py --help
```

## Preparación de Imágenes Cloud en Proxmox

Descarga imágenes cloud directamente en tu servidor Proxmox:

```bash
# Ubuntu 24.04 LTS (Noble)
cd /var/lib/vz/template/iso
wget https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img

# Ubuntu 22.04 LTS (Jammy)
wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img

# Debian 12
wget https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.qcow2
```

## Ejemplos

### VM Simple con DHCP

```yaml
vms:
  - vmid: 100
    name: "test-vm"
    node: "pve"
```

### VM con IP Estática y SSH Keys

```yaml
vms:
  - vmid: 101
    name: "prod-server"
    node: "pve"
    memory: 8192
    cores: 4
    disk_size: "100G"
    network_type: "static"
    ip: "192.168.1.50"
    credentials:
      user: "admin"
      password: "secure_password"
      ssh_keys:
        - "ssh-rsa AAAAB3NzaC1yc2..."
    start: true
```

### Cluster Kubernetes

```yaml
vms:
  - vmid: 201
    name: "k8s-master"
    node: "pve1"
    template: "large"
    ip: "192.168.1.101"

  - vmid: 202
    name: "k8s-worker-01"
    node: "pve2"
    template: "large"
    ip: "192.168.1.102"

  - vmid: 203
    name: "k8s-worker-02"
    node: "pve3"
    template: "large"
    ip: "192.168.1.103"
```

## Cloud-init Vendor Snippets

Puedes ejecutar scripts personalizados durante el aprovisionamiento:

1. Crear snippet en Proxmox:
```bash
cat > /var/lib/vz/snippets/install-docker.yaml << 'EOF'
#cloud-config
runcmd:
  - curl -fsSL https://get.docker.com | sh
  - systemctl enable docker
  - systemctl start docker
EOF
```

2. Configurar en `config.yaml`:
```yaml
defaults:
  snippet: "local:snippets/install-docker.yaml"
```

## Troubleshooting

### Error de Autenticación

```
❌ Error: Couldn't authenticate user: root@pam
```

**Solución:** Verifica credenciales en `config.yaml` y permisos del usuario en Proxmox.

### Imagen Cloud No Encontrada

```
❌ Imagen 'ubuntu22' no encontrada en config.yaml
```

**Solución:** Verifica que la ruta en `config.yaml` bajo `defaults.images` apunte a un archivo existente en Proxmox.

### VM No Inicia

**Solución:**
1. Verifica que QEMU Guest Agent esté instalado en la imagen cloud
2. Revisa logs en Proxmox: `journalctl -u pve-cluster -f`
3. Verifica configuración de red en cloud-init

## Logs

Todos los logs se guardan en `vm_creation.log`:

```bash
# Ver logs en tiempo real
tail -f vm_creation.log

# Filtrar solo errores
grep "ERROR" vm_creation.log
```

## Seguridad

- **NUNCA** commits `.env` o `config.yaml` con credenciales (ya están en .gitignore)
- **Usa .env para TODAS las credenciales sensibles** (ver [docs/SECURITY.md](docs/SECURITY.md))
- Restringir permisos: `chmod 600 .env`
- Cambia las contraseñas por defecto de cloud-init
- Configura claves SSH en lugar de passwords
- Rota credenciales regularmente (cada 90 días recomendado)

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit tus cambios: `git commit -m 'Añadir nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

## Licencia

MIT License - Ver archivo LICENSE para más detalles

## Autor

Ricardo Wagner

## Changelog

### v3.2.0 (2026-01-16)
- **Corrección SSH Crítica**: Solucionado el problema de doble codificación URL en claves SSH.
- **Nuevos Scripts**: `delete_all_vms.py` para limpieza masiva y `verify_ssh.sh` para validación.
- **Utilidad**: `force_copy_keys.sh` como fallback para inyección manual de claves.
- Mejoras en robustez de borrado de VMs (espera activa de tareas).

### v3.0 (2026-01-10)
- Soporte completo para cloud images
- Configuración cloud-init mejorada
- Templates reutilizables
- QEMU Guest Agent automático
- Modo dry-run

### v2.0 (Anterior)
- Primera versión funcional con proxmoxer

## Referencias

- [Proxmox VE Documentation](https://pve.proxmox.com/pve-docs/)
- [Cloud-init Documentation](https://cloudinit.readthedocs.io/)
- [Proxmoxer Python Library](https://pypi.org/project/proxmoxer/)
- [Ubuntu Cloud Images](https://cloud-images.ubuntu.com/)

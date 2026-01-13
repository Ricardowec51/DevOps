# Guía de Inicio Rápido

## Instalación en 5 Minutos

### 1. Preparar el Entorno

```bash
# Clonar repositorio
git clone <repo-url>
cd proxmox-vm-creator

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Credenciales

```bash
# Copiar archivo de variables de entorno
cp .env.example .env

# Editar con tus credenciales
nano .env

# Restringir permisos
chmod 600 .env
```

Configuración mínima en `.env`:
```bash
# Proxmox
PROXMOX_HOST=192.168.1.100
PROXMOX_USER=root@pam
PROXMOX_PASSWORD=tu_password_aqui

# VMs
VM_DEFAULT_USER=rwagner
VM_DEFAULT_PASSWORD=password_vms

# Defaults
DEFAULT_STORAGE=local-lvm

# Imagen Cloud
IMAGE_UBUNTU24=/var/lib/vz/template/iso/noble-server-cloudimg-amd64.img
```

**IMPORTANTE:** NO pongas credenciales en `config.yaml`, usa `.env` siempre.

### 3. Descargar Imagen Cloud en Proxmox

Conecta a tu servidor Proxmox:

```bash
ssh root@192.168.1.100

# Descargar Ubuntu 24.04 LTS
cd /var/lib/vz/template/iso
wget https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img

# Verificar descarga
ls -lh noble-server-cloudimg-amd64.img
```

### 4. Crear tu Primera VM

Edita `vms.yaml`:

```yaml
vms:
  - vmid: 100
    name: "mi-primera-vm"
    node: "pve"
```

### 5. Ejecutar

```bash
# Primero, verificar sin crear (dry-run)
./create_vm.py --dry-run

# Si todo está OK, crear la VM
./create_vm.py
```

### 6. Verificar en Proxmox

Abre tu interfaz web de Proxmox y verás la VM creada. Iníciala desde la interfaz o configura `start: true` en el YAML.

## Próximos Pasos

- Lee el [README.md](../README.md) completo
- Explora [ejemplos](../examples/) para casos de uso más complejos
- Aprende sobre [cloud-init snippets](CLOUD_INIT.md) para personalización avanzada

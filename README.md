# Proxmox VM Creator v3.0

Herramienta automatizada para crear y configurar máquinas virtuales en Proxmox VE usando **cloud images** y **cloud-init**. Simplifica el despliegue de infraestructura mediante archivos YAML declarativos.

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

## Estructura del Proyecto

```
proxmox-vm-creator/
├── create_vm.py           # Script principal
├── config.yaml.example    # Plantilla de configuración
├── config.yaml           # Configuración (NO en Git)
├── vms.yaml              # Definición de VMs a crear
├── templetes.yaml        # Templates reutilizables
├── requirements.txt      # Dependencias Python
├── README.md            # Este archivo
├── .gitignore           # Archivos ignorados por Git
└── examples/            # Ejemplos de configuración
    ├── vms/             # Ejemplos de VMs
    └── snippets/        # Snippets cloud-init
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

### 2. vms.yaml

Define las VMs a crear. Puedes usar templates o especificar todo manualmente:

```yaml
vms:
  # VM simple con DHCP
  - vmid: 2001
    name: "web-server-01"
    node: "pve"
    template: "web-server"

  # VM con IP estática
  - vmid: 2002
    name: "db-server-01"
    node: "pve"
    memory: 8192
    cores: 4
    disk_size: "100G"
    network_type: "static"
    ip: "192.168.1.100"
    start: true
```

### 3. templetes.yaml

Templates reutilizables para diferentes tipos de servidores:

```yaml
templates:
  web-server:
    memory: 4096
    cores: 4
    disk_size: "50G"

  db-server:
    memory: 8192
    cores: 6
    disk_size: "200G"
```

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

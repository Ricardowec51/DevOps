# Guía de Seguridad y Manejo de Credenciales

## Filosofía de Seguridad

Este proyecto usa el patrón de **variables de entorno** para manejar credenciales sensibles, siguiendo las mejores prácticas de seguridad modernas.

## Sistema de Prioridades

Las credenciales se leen en el siguiente orden de prioridad:

```
1. Archivo .env (MÁS ALTA PRIORIDAD)
2. Variables de entorno del sistema
3. Archivo config.yaml (si existe)
4. Valores por defecto en el código (ÚLTIMA OPCIÓN)
```

## Configuración Inicial

### 1. Crear archivo .env

```bash
cd /Users/rwagner/proxmox-vm-creator
cp .env.example .env
chmod 600 .env  # Restringir permisos
```

### 2. Editar .env con tus credenciales

```bash
nano .env
```

Ejemplo de `.env` configurado:

```bash
# Credenciales de Proxmox
PROXMOX_HOST=192.168.1.143
PROXMOX_USER=root@pam
PROXMOX_PASSWORD=MiPasswordSeguro123!
PROXMOX_VERIFY_SSL=false

# Configuración de Red
NETWORK_BRIDGE=vmbr0
NETWORK_GATEWAY=192.168.1.1
NETWORK_NETMASK=24
NETWORK_NAMESERVER=8.8.8.8

# Credenciales Cloud-Init (VMs)
VM_DEFAULT_USER=rwagner
VM_DEFAULT_PASSWORD=PasswordVMs456!

# SSH Keys (opcional)
VM_SSH_KEYS=ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ... rwagner@laptop

# Storage y Defaults
DEFAULT_STORAGE=NFS_SERVER
DEFAULT_MEMORY=2048
DEFAULT_CORES=2
DEFAULT_DISK_SIZE=20G

# Rutas a Imágenes Cloud
IMAGE_UBUNTU22=/var/lib/vz/template/iso/jammy-server-cloudimg-amd64.img
IMAGE_UBUNTU24=/var/lib/vz/template/iso/noble-server-cloudimg-amd64.img
```

### 3. Verificar permisos

```bash
ls -la .env
# Debe mostrar: -rw------- (solo lectura/escritura para el propietario)
```

## Archivo config.yaml (Opcional)

Puedes crear un `config.yaml` para valores NO sensibles:

```bash
cp config.yaml.example config.yaml
```

**IMPORTANTE:** Si defines credenciales en `config.yaml`, el archivo `.env` tiene prioridad.

## Mejores Prácticas

### ✅ HACER

1. **Siempre usa .env para credenciales**
   ```bash
   PROXMOX_PASSWORD=mi_password_real
   ```

2. **Restringir permisos del archivo**
   ```bash
   chmod 600 .env
   ```

3. **Diferentes .env por entorno**
   ```
   .env.development
   .env.production
   .env.testing
   ```

4. **Rotar passwords regularmente**
   - Cambiar credenciales cada 90 días
   - Usar passwords fuertes (min 16 caracteres)

5. **Usar SSH keys en lugar de passwords**
   ```bash
   VM_SSH_KEYS=ssh-rsa AAAAB3...
   # No necesitas VM_DEFAULT_PASSWORD si usas keys
   ```

### ❌ NO HACER

1. **NUNCA commits .env al repositorio**
   ```bash
   # .env está en .gitignore - verificar:
   git status  # NO debe aparecer .env
   ```

2. **NUNCA pongas credenciales en config.yaml**
   - Solo usa config.yaml para valores no sensibles

3. **NUNCA compartas tu .env**
   - Cada usuario debe tener su propio .env

4. **NUNCA uses passwords débiles**
   ```bash
   # ❌ MAL
   PROXMOX_PASSWORD=123456

   # ✅ BIEN
   PROXMOX_PASSWORD=Pr0xm0x!S3cur3P@ssw0rd2024
   ```

## Variables de Entorno Disponibles

### Proxmox
```bash
PROXMOX_HOST          # IP del servidor Proxmox
PROXMOX_USER          # Usuario (ej: root@pam)
PROXMOX_PASSWORD      # Password del usuario
PROXMOX_VERIFY_SSL    # true/false
```

### Red
```bash
NETWORK_BRIDGE        # Bridge de red (ej: vmbr0)
NETWORK_GATEWAY       # Gateway por defecto
NETWORK_NETMASK       # Máscara de red (ej: 24)
NETWORK_NAMESERVER    # DNS (ej: 8.8.8.8)
```

### Credenciales de VMs
```bash
VM_DEFAULT_USER       # Usuario por defecto en VMs
VM_DEFAULT_PASSWORD   # Password por defecto en VMs
VM_SSH_KEYS           # Claves SSH (separadas por coma)
```

### Defaults
```bash
DEFAULT_STORAGE       # Storage por defecto
DEFAULT_MEMORY        # RAM en MB
DEFAULT_CORES         # Número de cores
DEFAULT_DISK_SIZE     # Tamaño de disco (ej: 20G)
```

### Imágenes Cloud
```bash
IMAGE_UBUNTU22        # Ruta a imagen Ubuntu 22.04
IMAGE_UBUNTU24        # Ruta a imagen Ubuntu 24.04
IMAGE_DEBIAN12        # Ruta a imagen Debian 12
IMAGE_ROCKY9          # Ruta a imagen Rocky 9
```

## Verificar Configuración

```bash
# Test sin crear VMs reales
./create_vm.py --dry-run

# El script mostrará de dónde lee las credenciales
```

## Múltiples Entornos

### Desarrollo
```bash
cp .env.example .env.development
# Editar con credenciales de desarrollo
```

### Producción
```bash
cp .env.example .env.production
# Editar con credenciales de producción
```

### Uso
```bash
# Desarrollo
ln -sf .env.development .env
./create_vm.py --dry-run

# Producción
ln -sf .env.production .env
./create_vm.py
```

## Troubleshooting

### Error: Faltan credenciales

```
❌ Faltan credenciales de Proxmox (verifica .env o config.yaml)
```

**Solución:**
1. Verifica que existe `.env`
2. Verifica que tiene las variables requeridas
3. Verifica permisos: `chmod 600 .env`

### Error: No se puede leer .env

```
❌ Error de conexión: ...
```

**Solución:**
1. Verifica que el archivo .env existe
2. Verifica sintaxis en .env (sin espacios extras)
3. Reinstala python-dotenv: `pip install --upgrade python-dotenv`

## Respaldo Seguro

### Backup de .env

```bash
# Encriptar backup
gpg -c .env
# Genera: .env.gpg (encriptado)

# Restaurar
gpg .env.gpg
# Genera: .env (desencriptado)
```

### Almacenar en Gestor de Passwords

Considera usar gestores de passwords como:
- 1Password
- Bitwarden
- KeePassXC
- LastPass

## Auditoría

### Verificar que .env no está en Git

```bash
git ls-files | grep .env
# No debe devolver nada

git check-ignore .env
# Debe devolver: .env
```

### Verificar passwords expuestos

```bash
git log -p | grep -i password
# No debe mostrar passwords reales
```

## Referencias

- [The Twelve-Factor App - Config](https://12factor.net/config)
- [OWASP - Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [python-dotenv Documentation](https://pypi.org/project/python-dotenv/)

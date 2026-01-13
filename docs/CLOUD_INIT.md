# Guía de Cloud-Init

## Introducción

Cloud-init es el estándar de la industria para inicializar instancias cloud. Proxmox VM Creator utiliza cloud-init para configurar automáticamente las VMs al primer arranque.

## Configuración Básica

### Usuario y Contraseña

```yaml
credentials:
  user: "ubuntu"
  password: "mi_password_seguro"
```

### Claves SSH

```yaml
credentials:
  user: "ubuntu"
  ssh_keys:
    - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ... user@laptop"
    - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ... user@desktop"
```

### Red DHCP

```yaml
network_type: "dhcp"
```

### Red Estática

```yaml
network_type: "static"
ip: "192.168.1.50"
gateway: "192.168.1.1"
netmask: "24"
nameserver: "8.8.8.8"
```

## Vendor Snippets

Los vendor snippets son scripts cloud-init que se ejecutan durante el aprovisionamiento.

### Crear un Snippet

En tu servidor Proxmox:

```bash
cat > /var/lib/vz/snippets/mi-snippet.yaml << 'EOF'
#cloud-config
package_update: true
package_upgrade: true

packages:
  - vim
  - htop
  - curl

runcmd:
  - echo "Hola desde cloud-init" > /tmp/hello.txt
  - systemctl enable qemu-guest-agent
  - systemctl start qemu-guest-agent
EOF
```

### Usar el Snippet

En `config.yaml`:

```yaml
defaults:
  snippet: "local:snippets/mi-snippet.yaml"
```

Todas las VMs usarán este snippet por defecto.

## Ejemplos de Snippets

### Instalar Docker

```yaml
#cloud-config
runcmd:
  - curl -fsSL https://get.docker.com | sh
  - systemctl enable docker
  - usermod -aG docker ubuntu
```

### Configurar Timezone y Locale

```yaml
#cloud-config
timezone: America/Guayaquil
locale: es_EC.UTF-8
```

### Crear Usuarios Adicionales

```yaml
#cloud-config
users:
  - name: admin
    groups: sudo
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    ssh_authorized_keys:
      - ssh-rsa AAAAB3...
```

### Montar Volumen Adicional

```yaml
#cloud-config
disk_setup:
  /dev/sdb:
    table_type: gpt
    layout: true

fs_setup:
  - device: /dev/sdb1
    filesystem: ext4

mounts:
  - [/dev/sdb1, /data, ext4, "defaults", "0", "2"]
```

### Scripts Personalizados

```yaml
#cloud-config
write_files:
  - path: /usr/local/bin/mi-script.sh
    permissions: '0755'
    content: |
      #!/bin/bash
      echo "Script personalizado"

runcmd:
  - /usr/local/bin/mi-script.sh
```

## Debugging Cloud-Init

### Ver Logs

```bash
# En la VM después del arranque
sudo cat /var/log/cloud-init.log
sudo cat /var/log/cloud-init-output.log
```

### Estado de Cloud-Init

```bash
sudo cloud-init status
sudo cloud-init status --long
```

### Re-ejecutar Cloud-Init

```bash
sudo cloud-init clean
sudo cloud-init init
```

## Mejores Prácticas

1. **Siempre actualiza paquetes:** `package_update: true`
2. **Usa claves SSH en lugar de passwords** para producción
3. **Habilita QEMU Guest Agent** en tus snippets
4. **Testea snippets** en ambiente de desarrollo primero
5. **Documenta tus snippets** con comentarios
6. **Versiona tus snippets** en el repositorio

## Referencias

- [Cloud-init Documentation](https://cloudinit.readthedocs.io/)
- [Cloud-config Examples](https://cloudinit.readthedocs.io/en/latest/topics/examples.html)
- [Proxmox Cloud-Init](https://pve.proxmox.com/wiki/Cloud-Init_Support)

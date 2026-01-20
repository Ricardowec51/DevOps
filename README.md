# Proxmox VM Creator v4.0.0

Herramienta automatizada para crear y gestionar VMs en Proxmox VE, con deployment completo de cluster **K3s HA** (High Availability).

## Novedades v4.0

- Menu interactivo completo (`./launch.sh`)
- Deployment automatizado de K3s HA (3 masters + N workers)
- Kube-VIP para alta disponibilidad del API server
- MetalLB para servicios LoadBalancer
- Gestion completa del ciclo de vida del cluster

## Inicio Rapido

```bash
# 1. Activar entorno y ejecutar menu
./launch.sh

# 2. Seguir las opciones del menu interactivo
```

## Menu Principal

| # | Opcion | Descripcion |
|---|--------|-------------|
| 1 | Crear VMs (Produccion) | Crea VMs en Proxmox |
| 2 | Crear VMs (Dry Run) | Simulacion sin crear |
| 3 | Verificar Estado | Muestra estado de VMs |
| 4 | Iniciar VMs | Inicia todas las VMs |
| 5 | Reiniciar VMs | Reinicia VMs |
| 6 | Fix & Optimize | Resize disco, SSD, FS |
| 7 | Crear Snapshots | Snapshot Pre-K3s |
| 8 | BORRAR VMs | Elimina todas las VMs |
| 9 | Desplegar K3s | Deploy cluster HA |
| 10 | Status K3s | Ver estado del cluster |
| 11 | Iniciar K3s | Inicia servicios K3s |
| 12 | Detener K3s | Detiene servicios K3s |
| 13 | Apagar VMs | Seleccion manual |
| 14 | Remover Cloud-Init | Quita drives cloud-init |
| 15 | Instalar MetalLB | LoadBalancer standalone |
| 16 | Deploy Nginx Test | Verificar LoadBalancer |
| 17 | Setup Wizard | Configuracion inicial |

## Arquitectura K3s HA

```
                 VIP: 192.168.1.50
                        |
        +---------------+---------------+
        |               |               |
   Master-01       Master-02       Master-03
   .21             .22             .23

   Worker-01  Worker-02  Worker-03  Worker-04  Worker-05
   .24        .25        .26        .27        .28

LoadBalancer Range: 192.168.1.51-61
```

## Versiones Criticas

| Componente | Version | Notas |
|------------|---------|-------|
| K3s | v1.30.13+k3s1 | NO usar v1.32.x |
| Kube-VIP | v0.8.6 | CRITICO: NO usar v0.8.9 |
| MetalLB | v0.14.9 | Usa CRDs |
| Ubuntu | 24.04 LTS | Cloud image |

## Instalacion

```bash
# Clonar repositorio
git clone https://github.com/ricardowec51/proxmox-vm-creator.git
cd proxmox-vm-creator

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar
cp .env.example .env
cp config.yaml.example config.yaml
nano .env        # Credenciales Proxmox
nano config.yaml # Configuracion cluster
```

## Configuracion

### .env (Credenciales)
```env
PROXMOX_HOST=192.168.1.100
PROXMOX_USER=root@pam
PROXMOX_PASSWORD=your_password
PROXMOX_VERIFY_SSL=false
```

### config.yaml (Cluster)
```yaml
defaults:
  cores: 4
  memory: 4096
  storage: NFS_SERVER
  images:
    ubuntu24: NFS_SERVER:iso/noble-server-cloudimg-amd64.img

network:
  bridge: vmbr0
  gateway: 192.168.1.254
  nameserver: 192.168.1.254

k3s:
  vip: 192.168.1.50
  interface: eth0
  version: v1.30.13+k3s1
  user: rwagner
  ssh_key: ~/.ssh/id_rsa
  lb_range: 192.168.1.51-192.168.1.61

vms:
  - vmid: 3001
    name: "k3s-master-01"
    node: "Nnuc13"
    memory: 8192
    cores: 4
    ip: "192.168.1.21"
    network_type: "static"
    tags: "kubernetes,master"
```

## Workflow Tipico

1. Configurar `.env` y `config.yaml`
2. `./launch.sh` - Abrir menu
3. Opcion 1: Crear VMs
4. Opcion 4: Iniciar VMs
5. Opcion 6: Optimizar discos
6. Opcion 14: Remover cloud-init
7. Opcion 9: Desplegar K3s
8. Opcion 15: Instalar MetalLB (si fallo)
9. Opcion 16: Verificar con nginx test

## Estructura del Proyecto

```
proxmox-vm-creator/
├── main.py              # Menu principal
├── launch.sh            # Script de inicio
├── deploy.sh            # Deploy a produccion
├── config.yaml          # Configuracion
├── lib/
│   ├── config.py        # Carga config
│   ├── proxmox_client.py# Cliente API
│   ├── k3s_manager.py   # Gestion K3s
│   └── logger.py        # Logging
├── create_vm.py         # Crear VMs
├── check_vms.py         # Estado VMs
├── start_vms.py         # Iniciar VMs
├── restart_vms.py       # Reiniciar VMs
├── shutdown_vms.py      # Apagar VMs
├── delete_all_vms.py    # Eliminar VMs
├── fix_and_optimize.py  # Optimizacion
├── create_snapshot.py   # Snapshots
└── remove_cloudinit_all.py # Cloud-init
```

## Comandos Utiles (Post-Deployment)

```bash
# Ver nodos del cluster
kubectl get nodes -o wide

# Ver pods
kubectl get pods -A

# Ver servicios LoadBalancer
kubectl get svc -A | grep LoadBalancer

# Exportar KUBECONFIG (si no funciona kubectl)
export KUBECONFIG=~/.kube/config
echo 'export KUBECONFIG=~/.kube/config' >> ~/.zshrc
```

## Deploy a Produccion (Admin VM)

```bash
# Desde Mac (desarrollo)
./deploy.sh              # Solo sincroniza
./deploy.sh --run        # Sincroniza y ejecuta
```

## Troubleshooting

### kubectl no conecta
```bash
export KUBECONFIG=~/.kube/config
```

### MetalLB falla durante deploy
Usar opcion 15 del menu.

### Verificar SSH
```bash
for ip in 21 22 23 24 25 26 27 28; do
  ssh -o ConnectTimeout=2 rwagner@192.168.1.$ip hostname
done
```

## Documentacion Adicional

- [PRIMEROS_PASOS.md](PRIMEROS_PASOS.md) - Guia para nuevos usuarios
- [GUIA_RAPIDA.md](GUIA_RAPIDA.md) - Comandos rapidos
- [SETUP_CLOUD_IMAGES.md](SETUP_CLOUD_IMAGES.md) - Setup cloud images
- [CLAUDE.md](CLAUDE.md) - Referencia para Claude Code

## Changelog

### v4.0.0 (2026-01-20)
- Menu interactivo completo con Rich/Questionary
- K3s HA deployment (3 masters + 5 workers)
- Kube-VIP v0.8.6 para alta disponibilidad
- MetalLB v0.14.9 para LoadBalancer
- Opciones independientes para MetalLB y nginx test
- Fix kubeconfig automatico
- Remover cloud-init drives

### v3.2.0 (2026-01-16)
- Correccion SSH critica
- Scripts delete_all_vms.py, verify_ssh.sh
- force_copy_keys.sh

### v3.0.0 (2026-01-10)
- Soporte cloud images
- Cloud-init mejorado
- Templates reutilizables

## Autor

Ricardo Wagner - [@ricardowec51](https://github.com/ricardowec51)

## Licencia

MIT License

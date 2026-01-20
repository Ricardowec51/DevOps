# CLAUDE.md - Proxmox VM Creator

## IMPORTANTE - ENTORNOS DE TRABAJO

| Entorno | Maquina | IP | Descripcion |
|---------|---------|-----|-------------|
| **PRODUCCION** | Admin (k3s-admin) | 192.168.1.20 | Ejecuta scripts en el cluster real |
| **DESARROLLO** | est (Mac local) | - | Edicion y pruebas de codigo |

**SIEMPRE verificar en que entorno se esta trabajando antes de ejecutar comandos.**

## Punto de Entrada

```bash
./launch.sh   # Activa venv y ejecuta main.py (menu interactivo)
```

## Despliegue a Produccion

```bash
./deploy.sh              # Sincroniza codigo a Admin (192.168.1.20)
./deploy.sh --run        # Sincroniza y ejecuta en Admin
```

## Estructura del Proyecto

```
proxmox-vm-creator/
├── main.py                 # Menu principal interactivo
├── launch.sh               # Script de inicio (activa venv)
├── deploy.sh               # Despliega a Admin VM
├── config.yaml             # Configuracion principal
├── lib/
│   ├── config.py           # Carga de configuracion
│   ├── proxmox_client.py   # Cliente API Proxmox
│   ├── k3s_manager.py      # Gestion cluster K3s
│   ├── logger.py           # Sistema de logging
│   └── setup_wizard.py     # Wizard de configuracion
├── create_vm.py            # Creacion de VMs
├── check_vms.py            # Verificar estado VMs
├── start_vms.py            # Iniciar VMs
├── restart_vms.py          # Reiniciar VMs
├── shutdown_vms.py         # Apagar VMs
├── delete_all_vms.py       # Eliminar VMs
├── fix_and_optimize.py     # Optimizacion (resize, SSD)
├── create_snapshot.py      # Crear snapshots
└── remove_cloudinit_all.py # Remover cloud-init drives
```

## Menu Principal (main.py)

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

## Arquitectura del Cluster K3s

```
                    ┌─────────────────┐
                    │   VIP (HA)      │
                    │  192.168.1.50   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
│  Master-01    │   │  Master-02    │   │  Master-03    │
│ 192.168.1.21  │   │ 192.168.1.22  │   │ 192.168.1.23  │
│   (Nnuc13)    │   │    (nuc10)    │   │     (msa)     │
└───────────────┘   └───────────────┘   └───────────────┘

┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Worker-01    │   │  Worker-02    │   │  Worker-03    │
│ 192.168.1.24  │   │ 192.168.1.25  │   │ 192.168.1.26  │
│    (BOSC)     │   │    (DELL)     │   │    (msn2)     │
└───────────────┘   └───────────────┘   └───────────────┘

┌───────────────┐   ┌───────────────┐
│  Worker-04    │   │  Worker-05    │
│ 192.168.1.27  │   │ 192.168.1.28  │
│   (Nnuc13)    │   │     (msa)     │
└───────────────┘   └───────────────┘

LoadBalancer Range: 192.168.1.51 - 192.168.1.61
```

## Versiones Criticas (NO CAMBIAR)

| Componente | Version | Notas |
|------------|---------|-------|
| K3s | v1.30.13+k3s1 | NO usar v1.32.x (Containerd 2.0 breaking changes) |
| Kube-VIP | v0.8.6 | CRITICO: v0.8.9 tiene bug IPVS |
| MetalLB | v0.14.9 | Usa CRDs (no ConfigMaps) |
| k3sup | 0.13.8 | Tool de deployment |
| Ubuntu | 24.04 LTS | Cloud image |

## Nodos Proxmox

- BOSC
- DELL
- Nnuc13
- nuc10
- msa
- msn2

## Configuracion SSH

```yaml
user: rwagner
ssh_key: ~/.ssh/id_rsa
interface: eth0  # Interface de red en las VMs
```

## Comandos Utiles

```bash
# Ver estado del cluster
kubectl get nodes -o wide

# Ver pods
kubectl get pods -A

# Ver servicios LoadBalancer
kubectl get svc -A | grep LoadBalancer

# Logs de un pod
kubectl logs -n <namespace> <pod-name>
```

## Archivos de Configuracion

- `config.yaml` - Configuracion principal (VMs, red, K3s)
- `.env` - Variables de entorno (API keys Proxmox)
- `user-data.yaml` - Cloud-init template

## Troubleshooting

### KUBECONFIG no funciona
```bash
export KUBECONFIG=~/.kube/config
# Agregar a ~/.zshrc para persistir
echo 'export KUBECONFIG=~/.kube/config' >> ~/.zshrc
```

### MetalLB falla durante deploy
Usar opcion 15 del menu para instalar MetalLB por separado.

### Verificar conectividad SSH a VMs
```bash
for ip in 21 22 23 24 25 26 27 28; do
  ssh -o ConnectTimeout=2 rwagner@192.168.1.$ip "hostname" 2>/dev/null && echo "OK" || echo "FAIL"
done
```

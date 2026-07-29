# ☸️ Guía de Despliegue: Cluster K3s High Availability (HA)

Esta guía documenta el proceso completo para desplegar un cluster Kubernetes producción-ready usando **K3s** en configuración de Alta Disponibilidad (HA) sobre máquinas virtuales Proxmox.

---

## 🏗️ Arquitectura del Cluster

El cluster consta de **9 nodos** en total (1 Admin + 3 Masters + 5 Workers), diseñados para máxima resiliencia.

| Rol | Cantidad | IPs | Descripción |
|-----|----------|-----|-------------|
| **Admin VM** | 1 | `192.168.1.20` | Nodo de orquestación y gestión ("Bastion"). Desde aquí se lanzan los scripts. |
| **Masters** | 3 | `192.168.1.21` - `.23` | Control Plane + Etcd (HA). Gestionan el estado del cluster. |
| **Workers** | 5 | `192.168.1.24` - `.28` | Nodos de carga de trabajo. Aquí corren tus aplicaciones. |
| **VIP** | 1 (Virtual) | `192.168.1.50` | IP Virtual flotante (Kube-VIP) para acceso HA a la API. |
| **MetalLB** | - | `192.168.1.60`+ | Rango de IPs para LoadBalancers de servicios (Nginx, Traefik, etc.). |

---

## 📋 Prerrequisitos

Antes de instalar K3s, las VMs deben estar preparadas (generalmente manejado por `prepare_vms_headless.py`):

1.  **S.O.:** Ubuntu 22.04/24.04 LTS.
2.  **Discos:** Optimizados (200GB Masters, 400GB Workers) con emulación SSD.
3.  **Usuario Sudo:** Usuario `rwagner` con permisos sudo *sin contraseña* (`ALL=(ALL) NOPASSWD: ALL`).
4.  **SSH:** Acceso SSH habilitado.

---

## 🚀 Proceso de Instalación (Estrategia Admin VM)

Para evitar problemas de compatibilidad (macOS vs Linux) y latencia, **la instalación se ejecuta desde la VM Admin (192.168.1.20)**.

### Paso 1: Acceder a la VM Admin
```bash
ssh rwagner@192.168.1.20
```

### Paso 2: Verificar el Instalador
El script maestro es **`k3s_installer_v3.sh`**. Asegúrate de que existe y es ejecutable:
```bash
ls -l ~/k3s_installer_v3.sh
# Si no es ejecutable: chmod +x ~/k3s_installer_v3.sh
```

### Paso 3: Ejecutar la Instalación
Este script automatiza TODO el proceso:
```bash
./k3s_installer_v3.sh
```

**¿Qué hace el script v3?**
1.  **Validaciones:** Verifica versiones, conectividad SSH y requisitos de sistema.
2.  **Bootstrap Master 1:** Inicializa el cluster en el primer nodo (`.21`).
3.  **Kube-VIP:** Despliega el VIP (.50) para que la API sea redundante.
4.  **Join Masters:** Une los nodos `.22` y `.23` como Control Plane.
5.  **Join Workers:** Une los 5 nodos workers (`.24` al `.28`).
6.  **MetalLB:** Instala y configura el balanceador de carga L2.
7.  **Verificación:** Despliega una app de prueba (Nginx) para confirmar que todo funciona.

---

## 🔍 Verificación del Cluster

Una vez terminada la instalación, verifica la salud del cluster:

### 1. Estado de los Nodos
Todos deben estar en estado `Ready`:
```bash
kubectl get nodes -o wide
```

### 2. Pods del Sistema
Asegúrate de que traefik/coredns/metrics-server estén corriendo (Running):
```bash
kubectl get pods -A
```

### 3. Prueba de Carga (LoadBalancer)
El script despliega un servicio Nginx de prueba. Verifica su IP externa:
```bash
kubectl get svc nginx-test-dev-service
# Debería tener una EXTERNAL-IP asignada (ej. 192.168.1.60)
```
Prueba acceso: `curl http://192.168.1.60`

---

## 🛠️ Mantenimiento y Operaciones

### Agregar más Nodos
Simplemente edita `k3s_installer_v3.sh` para agregar la IP al array `WORKERS` y vuelve a ejecutar (el script es idempotente para joins) o usa `k3sup join` manualmente:
```bash
k3sup join --ip <NUEVA_IP> --user rwagner --server-ip 192.168.1.21 --ssh-key ~/.ssh/id_ed25519
```

### Acceso Remoto (desde tu Mac)
Para controlar el cluster desde tu máquina local (no la VM 20):
1. Copia el archivo config:
   ```bash
   scp rwagner@192.168.1.20:~/.kube/config ~/.kube/config-k3s
   ```
2. Úsalo:
   ```bash
   export KUBECONFIG=~/.kube/config-k3s
   kubectl get nodes
   ```

---

## 🐛 Solución de Problemas Comunes

**1. Error SSH "handshake failed" / "unable to authenticate"**
- **Causa:** `k3sup` intenta usar la clave RSA por defecto, pero la VM usa Ed25519.
- **Solución:** Asegúrate de usar `--ssh-key ~/.ssh/id_ed25519`. (El script v3 ya lo hace).

**2. K3s no inicia ("waiting for verification")**
- **Causa:** Interfaz de red incorrecta.
- **Solución:** Verifica si la VM usa `eth0` o `ens18`. El script v3 usa `eth0` por defecto.

**3. VIP no responde**
- **Causa:** Conflicto de ARP o Kube-VIP no desplegado.
- **Solución:** Revisa logs de kube-vip: `kubectl logs -n kube-system -l app.kubernetes.io/name=kube-vip-ds`

---
*Documentación generada automáticamente por AntiGravity - 2026-01-16*

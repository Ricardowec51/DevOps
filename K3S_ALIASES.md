# K3s Cluster - Aliases y Comandos Rápidos

## 🎯 Alias Principal de Monitoreo

### `k-view` - Vista Rápida del Cluster

El alias que tenías y que he mejorado. Muestra una vista completa del cluster en un solo comando.

```bash
k-view
```

**Muestra:**

- 📊 Estado de todos los nodos
- 🌐 Servicios LoadBalancer activos
- 📦 Top 25 pods
- 💾 Uso de recursos (si está disponible)

---

## 🚀 Nuevos Alias Agregados

### Dashboards Completos

| Alias       | Descripción                         | Comando Equivalente                                           |
| ----------- | ----------------------------------- | ------------------------------------------------------------- |
| `k-view`    | Vista rápida del cluster (mejorada) | Ver arriba                                                    |
| `k-monitor` | Dashboard visual completo (Python)  | `cd ~/proxmox-vm-creator && ./venv/bin/python k3s_monitor.py` |
| `k-status`  | Script de estado rápido             | `cd ~/proxmox-vm-creator && ./cluster-status.sh`              |

### Shortcuts de kubectl

| Alias      | Descripción                 | Comando Equivalente                                          |
| ---------- | --------------------------- | ------------------------------------------------------------ |
| `k`        | kubectl corto               | `kubectl`                                                    |
| `kk`       | kubectl corto (alternativo) | `kubectl`                                                    |
| `kgp`      | Listar todos los pods       | `kubectl get pods -A`                                        |
| `kgs`      | Listar todos los servicios  | `kubectl get svc -A`                                         |
| `kgn`      | Listar nodos con detalles   | `kubectl get nodes -o wide`                                  |
| `ktn`      | Uso de recursos por nodo    | `kubectl top nodes`                                          |
| `ktp`      | Uso de recursos por pod     | `kubectl top pods -A`                                        |
| `kevents`  | Últimos 20 eventos          | `kubectl get events -A --sort-by=.lastTimestamp \| tail -20` |
| `kpending` | Pods no Running             | `kubectl get pods -A \| grep -v Running`                     |

### Vistas por Namespace

| Alias          | Descripción                 | Namespace       |
| -------------- | --------------------------- | --------------- |
| `k-factuscan`  | Ver recursos de FactuScan   | factuscan       |
| `k-contactos`  | Ver recursos de Contactos   | contactos       |
| `k-monitoring` | Ver stack de monitoreo      | monitoring      |
| `k-longhorn`   | Ver almacenamiento Longhorn | longhorn-system |

### Utilidades Especiales

| Alias        | Descripción                      |
| ------------ | -------------------------------- |
| `k-ips`      | Lista rápida de IPs LoadBalancer |
| `k-problems` | Mostrar solo pods con problemas  |

---

## 📖 Ejemplos de Uso

### Vista Rápida del Cluster

```bash
# El comando que buscabas - vista completa
k-view
```

### Dashboard Visual Completo

```bash
# Dashboard con tablas formateadas y colores
k-monitor
```

### Verificar Estado de una Aplicación

```bash
# Ver todos los recursos de FactuScan
k-factuscan

# Ver todos los recursos de Contactos
k-contactos
```

### Troubleshooting Rápido

```bash
# Ver pods con problemas
k-problems

# Ver eventos recientes
kevents

# Ver pods que no están Running
kpending
```

### Monitoreo de Recursos

```bash
# Uso de recursos por nodo
ktn

# Uso de recursos por pod
ktp
```

### Ver IPs de LoadBalancer

```bash
# Lista rápida de servicios LoadBalancer con sus IPs
k-ips
```

**Salida ejemplo:**

```
factuscan factuscan-frontend 192.168.1.59
factuscan factuscan-backend 192.168.1.61
contactos admin-panel-service 192.168.1.53
...
```

---

## 🔧 Aliases Existentes (Preservados)

Estos alias ya existían en tu configuración:

| Alias      | Descripción                        |
| ---------- | ---------------------------------- |
| `kk`       | kubectl corto                      |
| `kkm`      | Ver nodos con contexto k3s-ha-prod |
| `k3s-prod` | Cambiar a contexto k3s-ha-prod     |

---

## 💡 Workflows Comunes

### Verificación Matutina del Cluster

```bash
# 1. Vista rápida
k-view

# 2. Si todo se ve bien, verificar recursos
ktn

# 3. Si hay problemas, ver detalles
k-problems
kevents
```

### Investigar un Problema

```bash
# 1. Ver pods con problemas
k-problems

# 2. Ver eventos recientes
kevents

# 3. Describir un pod específico
kubectl describe pod -n <namespace> <pod-name>

# 4. Ver logs
kubectl logs -n <namespace> <pod-name>
```

### Monitoreo de una Aplicación

```bash
# 1. Ver recursos de la app
k-factuscan

# 2. Ver logs del backend
kubectl logs -n factuscan -l app=factuscan-backend -f

# 3. Verificar servicio LoadBalancer
k-ips | grep factuscan
```

---

## 📝 Notas

1. **Activación de Aliases:** Los aliases se cargan automáticamente en nuevas sesiones de terminal. Para la sesión actual, ejecuta:

   ```bash
   source ~/.zshrc
   ```

2. **Ubicación:** Todos los aliases están en `~/.zshrc`

3. **Personalización:** Puedes editar `~/.zshrc` para modificar o agregar más aliases según tus necesidades.

4. **Dependencias:**
   - `k-monitor` requiere el entorno virtual Python activado
   - `k-status` requiere el script `cluster-status.sh`
   - Ambos scripts están en `/Users/rwagner/proxmox-vm-creator/`

---

## 🎯 Comando Recomendado

Para tu uso diario, el comando más útil es:

```bash
k-view
```

Este es el alias que tenías antes, ahora mejorado con mejor formato visual. Te da una vista completa del cluster en segundos.

Para análisis más detallado:

```bash
k-monitor
```

Este muestra el dashboard completo con tablas formateadas, métricas y estadísticas.

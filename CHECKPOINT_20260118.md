# CHECKPOINT - 2026-01-18 (Actualizado)

## Estado Actual: RECUPERACIÓN POST-ERROR CRÍTICO

### Resumen Ejecutivo
**ERROR GRAVE:** Las VMs 3001, 3003, 3005 fueron creadas incorrectamente en el nodo DELL en lugar de sus nodos asignados. Esto causó la necesidad de hard reset en las máquinas físicas del cluster Proxmox.

### Acciones Correctivas Realizadas
- VMs 3001, 3003, 3005 **ELIMINADAS** del nodo DELL
- Usuario realizando llamada a soporte Google
- Cluster al ~95% de recuperación

### Causa del Error
Las VMs fueron desplegadas en el nodo DELL ignorando la configuración de `vms.yaml`:
- 3001 (k3s-master-01): Debía ir a DELL → Fue a DELL ✓
- 3003 (k3s-master-03): Debía ir a **msa** → Fue a DELL ✗
- 3005 (k3s-worker-02): Debía ir a DELL → Fue a DELL ✓

---

## Historial Previo: Crisis Anterior

---

## Estado de VMs Antes del Incidente

| VMID | Nombre | Nodo | IP | Estado SSH |
|------|--------|------|-----|------------|
| 3001 | k3s-master-01 | ? | 192.168.1.12 | ✅ OK |
| 3002 | k3s-master-02 | ? | 192.168.1.13 | ✅ OK |
| 3003 | k3s-master-03 | msa | 192.168.1.14 | ❌ Sin respuesta |
| 3004 | k3s-worker-01 | ? | 192.168.1.15 | ✅ OK |
| 3005 | k3s-worker-02 | ? | 192.168.1.16 | ✅ OK |
| 3006 | k3s-worker-03 | msn2 | 192.168.1.17 | ✅ OK |
| 3007 | k3s-worker-04 | ? | 192.168.1.18 | ✅ OK |
| 3008 | k3s-worker-05 | msa | 192.168.1.19 | ✅ OK |

### VM 3003 - Problema Persistente
- Múltiples intentos de recreación
- Última creación exitosa en nodo `msa` (200.19s)
- Error Python durante verificación: `TypeError: unhashable type: 'dict'`
- Nunca respondió a SSH en IP 192.168.1.14

---

## Configuración del Proyecto

### Archivos Clave Modificados

1. **config.yaml** - Configuración principal
   - Snippet: `NFS_SERVER:snippets/user-data.yaml`
   - Admin VM: 192.168.1.20 (vmid 1102)
   - IP Plan: Masters .12-.14, Workers .15-.19

2. **deploy.sh** - Script de despliegue (NUEVO)
   - Sincroniza con rsync a VM Admin
   - Soporta: --setup, --run, --action, --confirm

3. **main.py** - Modo headless agregado
   - --action para ejecutar sin menú interactivo
   - --confirm para acciones destructivas
   - Dry-run obligatorio antes de crear VMs

4. **requirements.txt** - Dependencias actualizadas
   - Agregado: paramiko>=3.0.0, urllib3>=2.0.0

5. **lib/k3s_manager.py** - Código reparado
   - Eliminado: import duplicado de `log`
   - Eliminado: `--local-path` duplicado
   - Eliminado: bloque Kube-VIP duplicado

6. **vms-pending.yaml** - VMs faltantes (NUEVO)
   - Solo contiene: 3003, 3006, 3008

---

## Nodos Proxmox

| Nodo | IP API | Estado |
|------|--------|--------|
| msa | 192.168.1.143 | ❌ No responde |
| msn2 | ? | ❌ No responde |
| BOSC | ? | ❌ No responde |
| DELL | ? | ❌ No responde |
| Nnuc13 | ? | ❌ No responde |
| nuc10 | ? | ❌ No responde |

---

## Infraestructura

### VM Admin (k3s-admin)
- **VMID:** 1102
- **IP:** 192.168.1.20
- **Usuario:** rwagner
- **Directorio:** /home/rwagner/proxmox-vm-creator
- **Función:** Ejecuta todos los scripts de automatización

### Storage
- **NFS_SERVER:** NAS compartido por todos los nodos
- **Imágenes:** NFS_SERVER:iso/
- **Snippets:** NFS_SERVER:snippets/

### Red
- **Bridge:** vmbr0
- **Gateway:** 192.168.1.254
- **Netmask:** /24
- **VIP K3s:** 192.168.1.50

---

## Tareas Pendientes (Cuando el cluster se recupere)

1. [ ] Verificar estado de todos los nodos Proxmox post-hard reset
2. [ ] **Recrear VMs eliminadas en nodos CORRECTOS:**
   - [ ] VM 3001 (k3s-master-01) → nodo DELL
   - [ ] VM 3003 (k3s-master-03) → nodo **msa** (NO DELL)
   - [ ] VM 3005 (k3s-worker-02) → nodo DELL
3. [ ] Verificar SSH a todas las VMs (8 total)
4. [ ] Ejecutar proceso post-VM
5. [ ] Desplegar K3s HA cluster

---

## Comandos Útiles para Recuperación

```bash
# Verificar conectividad a nodos Proxmox
for ip in 192.168.1.143; do ping -c 1 $ip && echo "OK: $ip" || echo "FAIL: $ip"; done

# Verificar SSH a VMs del cluster
for ip in 12 13 14 15 16 17 18 19; do
  ssh -o ConnectTimeout=3 rwagner@192.168.1.$ip hostname 2>/dev/null && echo "OK: .${ip}" || echo "FAIL: .${ip}"
done

# Desde VM Admin - verificar VMs
cd ~/proxmox-vm-creator && source venv/bin/activate && python3 check_vms.py

# Listar todas las VMs en el cluster
./deploy.sh --action check-vms
```

---

## Archivos de Log Relevantes

- `/private/tmp/claude/-Users-rwagner-proxmox-vm-creator/tasks/b395530.output` - Último intento de recrear VM 3003
- `/private/tmp/claude/-Users-rwagner-proxmox-vm-creator/tasks/ba3cedf.output` - Última verificación SSH

---

## Notas Importantes

1. **NO ejecutar más comandos** hasta que el cluster esté estable
2. El error `TypeError: unhashable type: 'dict'` en el script de verificación NO debería causar caída del cluster
3. Posible causa: sobrecarga de API por operaciones repetidas
4. Posible causa: problema de red/storage en NFS

---

## Contacto de Sesión

- **Fecha:** 2026-01-18
- **Herramienta:** Claude Code (Opus 4.5)
- **Contexto:** Sesión continuada después de compactación
- **Transcript completo:** /Users/rwagner/.claude/projects/-Users-rwagner-proxmox-vm-creator/0965f20d-dedc-4001-8215-ed860cea3d81.jsonl

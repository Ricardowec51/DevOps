# Sistema de Logging - Proxmox VM Creator v3.1.0

Documentación completa del sistema de logging mejorado para registrar todas las operaciones de creación de VMs.

## 📋 Descripción General

El sistema de logging registra **cada detalle** de la ejecución del script `create_vm.py`:
- Parámetros de ejecución
- Configuración de cada VM
- Proceso de creación paso a paso
- Errores detallados con stack traces
- Resumen final en texto y JSON
- Tiempos de ejecución

## 📁 Estructura de Logs

### Archivos Generados

Cada ejecución de `create_vm.py` genera **3 archivos**:

```
proxmox-vm-creator/
├── vm_creation.log              # Log general (se sobrescribe cada vez)
├── logs/
│   ├── vm_creation_YYYYMMDD_HHMMSS.log    # Log específico de cada ejecución
│   └── summary_YYYYMMDD_HHMMSS.json       # Resumen en formato JSON
```

### 1. Log General (`vm_creation.log`)

**Ubicación:** `./vm_creation.log`

**Descripción:** Log general que se **sobrescribe** en cada ejecución. Útil para revisar rápidamente la última ejecución.

**Ejemplo:**
```bash
# Ver el log de la última ejecución
cat vm_creation.log

# Ver en tiempo real (si está corriendo)
tail -f vm_creation.log
```

### 2. Logs por Ejecución (`logs/vm_creation_YYYYMMDD_HHMMSS.log`)

**Ubicación:** `./logs/vm_creation_YYYYMMDD_HHMMSS.log`

**Descripción:** Log **completo y detallado** de cada ejecución con timestamp. Se **conserva permanentemente** para auditoría e historial.

**Formato del timestamp:** `YYYYMMDD_HHMMSS`
- Ejemplo: `vm_creation_20260115_153045.log` (15 de enero 2026, 15:30:45)

**Contenido:**
- Información del sistema (OS, Python version)
- Conexión a Proxmox
- Configuración completa de cada VM
- Parámetros enviados a la API
- Tiempos de ejecución
- Errores detallados con stack traces
- Resumen final

**Ejemplo:**
```bash
# Listar todos los logs
ls -lh logs/vm_creation_*.log

# Ver un log específico
cat logs/vm_creation_20260115_153045.log

# Ver últimos 50 líneas de un log
tail -50 logs/vm_creation_20260115_153045.log

# Buscar errores en un log
grep "ERROR" logs/vm_creation_20260115_153045.log
```

### 3. Resúmenes JSON (`logs/summary_YYYYMMDD_HHMMSS.json`)

**Ubicación:** `./logs/summary_YYYYMMDD_HHMMSS.json`

**Descripción:** Resumen **estructurado en JSON** de la ejecución, perfecto para procesamiento automático, reportes o dashboards.

**Contenido:**
```json
{
  "timestamp": "2026-01-15 15:30:45",
  "execution_time_seconds": 12.45,
  "mode": "production",
  "vms_file": "vms.yaml",
  "total_vms": 7,
  "successful": 7,
  "failed": 0,
  "successful_vms": [
    {
      "vmid": 2001,
      "name": "web-prod-01",
      "node": "Nnuc13",
      "memory": 4096,
      "cores": 4,
      "disk": "50G",
      "ip": "192.168.1.33",
      "status": "created"
    }
  ],
  "failed_vms": []
}
```

**Ejemplo de uso:**
```bash
# Ver resumen formateado
cat logs/summary_20260115_153045.json | python -m json.tool

# Extraer VMs exitosas
cat logs/summary_20260115_153045.json | jq '.successful_vms'

# Contar VMs creadas
cat logs/summary_20260115_153045.json | jq '.successful'

# Listar VMs fallidas
cat logs/summary_20260115_153045.json | jq '.failed_vms'
```

## 📝 Contenido Detallado del Log

### Sección 1: Información de Inicio

```
================================================================================
Proxmox VM Creator v3.1.0 - Ejecución iniciada
Timestamp: 2026-01-15 15:30:45
Log de esta ejecución: logs/vm_creation_20260115_153045.log
Sistema: Darwin 25.2.0
Python: 3.14.0
================================================================================
```

**Información registrada:**
- Versión del script
- Timestamp de inicio
- Ubicación del log
- Sistema operativo
- Versión de Python

### Sección 2: Conexión a Proxmox

```
Intentando conectar a Proxmox...
  Host: 192.168.1.143
  Usuario: root@pam
  Verify SSL: False
✅ Conectado a Proxmox 192.168.1.143
```

**Información registrada:**
- Host de Proxmox
- Usuario
- Configuración SSL
- Resultado de conexión

### Sección 3: Parámetros de Ejecución

```
================================================================================
📋 PARÁMETROS DE EJECUCIÓN
================================================================================
Archivo de VMs: vms.yaml
Modo: PRODUCCIÓN (Creación real)
================================================================================
```

**Información registrada:**
- Archivo YAML con VMs
- Modo (dry-run o producción)

### Sección 4: Creación de cada VM

```
🚀 Creando VM 2001 (web-prod-01) en Nnuc13...
────────────────────────────────────────────────────────────────────────────────
📋 Configuración de VM:
   VMID: 2001
   Nombre: web-prod-01
   Nodo: Nnuc13
   Memoria: 4096 MB
   CPU: 4 cores
   Disco: 50G
   Imagen: ubuntu22
   Network: static
   IP: 192.168.1.33
   Tags: web,production

⏳ Enviando petición a Proxmox API...
✅ VM 2001 creada exitosamente en 1.23s
   └─ Imagen: ubuntu22
   └─ RAM: 4096MB
   └─ CPU: 4 cores
   └─ Disco: NFS_SERVER:0,import-from=/mnt/pve/NFS_SERVER/template/iso/jammy-server-cloudimg-amd64.img,discard=on,size=50G
   └─ QEMU Agent: Habilitado
   └─ Cloud-init: Configurado
────────────────────────────────────────────────────────────────────────────────
```

**Información registrada:**
- Configuración completa de la VM
- Parámetros enviados a Proxmox
- Tiempo de creación
- Detalles del resultado

### Sección 5: Resumen Final

```
================================================================================
📊 RESUMEN DE EJECUCIÓN
================================================================================
✅ Exitosas: 7
❌ Fallidas: 0
⏱️  Tiempo total: 12.45s
================================================================================

✅ VMs creadas exitosamente:
   • VM 2001 (web-prod-01) en Nnuc13
   • VM 2002 (db-prod-01) en DELL
   • VM 2004 (legacy-server) en msa
   • VM 2005 (vpn-server) en msn2
   • VM 2010 (k8s-master-01) en BOSC
   • VM 2011 (k8s-worker-01) en DELL
   • VM 2012 (k8s-worker-02) en msa

📄 Resumen guardado en: logs/summary_20260115_153045.json
================================================================================
```

**Información registrada:**
- Número de VMs exitosas
- Número de VMs fallidas
- Tiempo total de ejecución
- Lista detallada de VMs creadas
- Ubicación del resumen JSON

## 🔍 Consultar Logs

### Ver el último log completo

```bash
# Ver log general (última ejecución)
cat vm_creation.log

# Ver el log más reciente con timestamp
cat $(ls -t logs/vm_creation_*.log | head -1)
```

### Ver logs en tiempo real

```bash
# Durante la ejecución
tail -f vm_creation.log

# O el log específico
tail -f logs/vm_creation_20260115_153045.log
```

### Buscar errores

```bash
# En el log general
grep -i "error" vm_creation.log

# En todos los logs
grep -i "error" logs/vm_creation_*.log

# Errores con contexto (5 líneas antes y después)
grep -i "error" -A 5 -B 5 vm_creation.log
```

### Filtrar por VM específica

```bash
# Ver logs de una VM específica
grep "VM 2001" vm_creation.log

# O en un log específico
grep "VM 2001" logs/vm_creation_20260115_153045.log
```

### Ver resúmenes de múltiples ejecuciones

```bash
# Listar todos los resúmenes
ls -lh logs/summary_*.json

# Ver resumen de cada ejecución
for file in logs/summary_*.json; do
    echo "=== $file ==="
    cat $file | jq '{timestamp, successful, failed, mode}'
done
```

### Generar reporte de todas las ejecuciones

```bash
# Crear reporte consolidado
echo "Resumen de todas las ejecuciones:" > reporte.txt
for file in logs/summary_*.json; do
    echo "" >> reporte.txt
    echo "Archivo: $file" >> reporte.txt
    cat $file | jq '{timestamp, total_vms, successful, failed}' >> reporte.txt
done
cat reporte.txt
```

## 🛠️ Mantenimiento de Logs

### Limpiar logs antiguos

```bash
# Eliminar logs de más de 30 días
find logs/ -name "vm_creation_*.log" -mtime +30 -delete
find logs/ -name "summary_*.json" -mtime +30 -delete

# Eliminar logs de más de 90 días
find logs/ -name "*.log" -mtime +90 -delete
find logs/ -name "*.json" -mtime +90 -delete
```

### Comprimir logs antiguos

```bash
# Comprimir logs de hace más de 7 días
find logs/ -name "vm_creation_*.log" -mtime +7 -exec gzip {} \;

# Descomprimir cuando sea necesario
gunzip logs/vm_creation_20260115_153045.log.gz
```

### Backup de logs

```bash
# Crear backup de todos los logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/

# Restaurar desde backup
tar -xzf logs_backup_20260115.tar.gz
```

## 📊 Niveles de Logging

El sistema usa estos niveles de logging:

| Nivel | Uso | Ejemplo |
|-------|-----|---------|
| `INFO` | Información general | "✅ VM 2001 creada" |
| `WARNING` | Advertencias no críticas | "⚠️ Template no encontrado" |
| `ERROR` | Errores que impiden la operación | "❌ Error al crear VM" |
| `DEBUG` | Información de debugging | Parámetros completos de API |

### Activar logging DEBUG

Para ver información aún más detallada (parámetros de API completos):

```python
# Editar create_vm.py y cambiar:
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar de INFO a DEBUG
    ...
)
```

Luego ejecutar:
```bash
./venv/bin/python create_vm.py
```

## 🔐 Seguridad en Logs

**IMPORTANTE:** Los logs protegen información sensible:

- ✅ **SSH keys** → Se ocultan, solo se muestra el count
- ✅ **Passwords** → Se reemplazan por `<password oculto>`
- ✅ **Tokens** → No se registran
- ❌ **IPs y nombres** → Se registran (no son sensibles)

**Ejemplo en log:**
```
sshkeys: <2 SSH keys configuradas>
cipassword: <password oculto>
```

## 📈 Casos de Uso

### 1. Auditoría: ¿Quién creó qué VM y cuándo?

```bash
# Buscar todas las VMs creadas en un día específico
ls logs/vm_creation_20260115_*.log

# Ver resumen de VMs creadas
cat logs/summary_20260115_153045.json | jq '.successful_vms[] | {vmid, name, node}'
```

### 2. Debugging: ¿Por qué falló la creación?

```bash
# Ver errores del último log
grep -A 10 "ERROR" vm_creation.log

# Ver stack trace completo
grep -A 20 "Traceback" vm_creation.log
```

### 3. Estadísticas: Tiempo promedio de creación

```bash
# Ver tiempos de todas las ejecuciones
cat logs/summary_*.json | jq '.execution_time_seconds'

# Calcular promedio
cat logs/summary_*.json | jq -s 'map(.execution_time_seconds) | add/length'
```

### 4. Reporte: VMs creadas por nodo

```bash
# Agrupar por nodo
cat logs/summary_20260115_153045.json | jq '.successful_vms | group_by(.node) | map({node: .[0].node, count: length})'
```

## 📚 Ver También

- **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** - Procedimientos de uso diario
- **[README.md](README.md)** - Overview del proyecto
- **[CHANGELOG.md](CHANGELOG.md)** - Historial de cambios

---

**Versión:** 3.1.0
**Última actualización:** 2026-01-15
**Autor:** Ricardo Wagner

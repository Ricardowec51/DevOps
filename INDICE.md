# Índice de Documentación - Proxmox VM Creator v3.1.0

Guía rápida para encontrar la documentación que necesitas.

## 🎯 ¿Qué quieres hacer?

### 🆕 SOY NUEVO - Empezar desde cero
**SIGUE ESTOS PASOS EN ORDEN:**

1. **[PRIMEROS_PASOS.md](PRIMEROS_PASOS.md)** - ⭐⭐⭐ **EMPIEZA AQUÍ** - Guía completa paso a paso (20 min)
2. **[README.md](README.md)** - Overview del proyecto y documentación de referencia
3. **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** - Referencia rápida de comandos

**O si prefieres hacerlo manualmente:**
1. Configura `.env` con tus credenciales
2. **[SETUP_CLOUD_IMAGES.md](SETUP_CLOUD_IMAGES.md)** - Descarga cloud images (SOLO UNA VEZ)
3. Copia `vms.yaml.example` a `vms.yaml` y edita
4. Ejecuta: `./venv/bin/python create_vm.py --dry-run`

### ✅ YA CONFIGURÉ TODO - Crear VMs
- **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** - ⭐ Comandos para crear, iniciar, eliminar VMs

### Usar el sistema (día a día)
- **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** - ⭐ Todo lo que necesitas:
  - Crear VMs
  - Iniciar VMs
  - Eliminar VMs
  - Scripts disponibles
  - Troubleshooting

### Entender cambios recientes
- **[CHANGELOG.md](CHANGELOG.md)** - Historial de versiones
- **[SESSION_SUMMARY.md](SESSION_SUMMARY.md)** - Resumen detallado de la última sesión

### Resolver problemas
- **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** - Sección de Troubleshooting
- **[README.md](README.md)** - Sección de Troubleshooting general

---

## 📂 Estructura de Archivos

### Documentación Principal
```
proxmox-vm-creator/
├── PRIMEROS_PASOS.md           # ⭐⭐⭐ Guía para nuevos usuarios
├── README.md                    # Overview y configuración
├── GUIA_RAPIDA.md              # ⭐ Procedimientos diarios
├── SETUP_CLOUD_IMAGES.md       # Setup inicial (una vez)
├── LOGGING.md                   # Sistema de logs
├── CHANGELOG.md                 # Historial de cambios
├── SESSION_SUMMARY.md           # Resumen de última sesión
└── INDICE.md                    # Este archivo
```

### Scripts Python
```
├── create_vm.py                 # Crear VMs
├── start_vms.py                 # Iniciar VMs
├── delete_vm.py                 # Eliminar VMs
├── list_vms.py                  # Listar VMs
├── list_nodes.py                # Listar nodos
├── check_vms.py                 # Verificar VMs específicas
├── check_images.py              # Ver cloud images
├── check_nfs_storage.py         # Ver NFS_SERVER
└── check_vm_status.py           # Estado detallado
```

### Scripts Bash
```
├── download_cloud_images.sh     # Descargar cloud images
└── update_config_for_nfs.sh     # Actualizar config
```

### Configuración
```
├── config.yaml                  # Configuración general (NO en Git)
├── config.yaml.example          # Plantilla de configuración
├── vms.yaml                     # VMs a crear (NO en Git)
├── templates.yaml               # Templates reutilizables
├── .env                         # Credenciales (NO en Git)
└── .env.example                 # Plantilla de credenciales
```

---

## 🔍 Búsqueda Rápida

| Quiero... | Ver documento |
|-----------|---------------|
| **Soy nuevo, empezar desde cero** | [PRIMEROS_PASOS.md](PRIMEROS_PASOS.md) ⭐⭐⭐ |
| **Crear mi primera VM** | [PRIMEROS_PASOS.md](PRIMEROS_PASOS.md#paso-3-definir-tu-primera-vm) |
| **Crear una VM nueva** | [GUIA_RAPIDA.md](GUIA_RAPIDA.md#procedimiento-para-crear-e-iniciar-vms) |
| **Iniciar VMs** | [GUIA_RAPIDA.md](GUIA_RAPIDA.md#paso-4-iniciar-las-vms) |
| **Eliminar una VM** | [GUIA_RAPIDA.md](GUIA_RAPIDA.md#procedimiento-para-eliminar-vms) |
| **Ver todos los scripts** | [GUIA_RAPIDA.md](GUIA_RAPIDA.md#scripts-disponibles) o [README.md](README.md#scripts-disponibles) |
| **Configurar cloud images** | [SETUP_CLOUD_IMAGES.md](SETUP_CLOUD_IMAGES.md) |
| **Entender los logs** | [LOGGING.md](LOGGING.md) |
| **Resolver un problema** | [GUIA_RAPIDA.md](GUIA_RAPIDA.md#troubleshooting) |
| **Ver qué cambió** | [CHANGELOG.md](CHANGELOG.md) |
| **Entender el proyecto** | [README.md](README.md) |

---

## 📖 Lectura Recomendada por Orden

Si eres nuevo en el proyecto, lee en este orden:

1. **[PRIMEROS_PASOS.md](PRIMEROS_PASOS.md)** (20 min) ⭐⭐⭐
   - Tutorial completo paso a paso
   - Te lleva de cero a tu primera VM funcionando
   - **EMPIEZA AQUÍ**

2. **[README.md](README.md)** (10 min)
   - Overview del proyecto
   - Explicación de todos los archivos
   - Configuración detallada

3. **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** (15 min)
   - Referencia rápida de comandos
   - Guarda como favorito para uso diario

4. **[LOGGING.md](LOGGING.md)** (5 min - opcional)
   - Sistema de logs
   - Cómo auditar ejecuciones

5. **[CHANGELOG.md](CHANGELOG.md)** (5 min - opcional)
   - Ver historial de cambios

---

## 💡 Tips

- **Marca GUIA_RAPIDA.md como favorito** - lo usarás constantemente
- **Configura las cloud images UNA SOLA VEZ** - luego olvídate del setup
- **Siempre usa --dry-run primero** antes de crear VMs
- **Los scripts de Python necesitan el venv activado** o usar `./venv/bin/python`

---

**Versión:** 3.1.0
**Última actualización:** 2026-01-15

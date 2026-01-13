# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [3.0.0] - 2026-01-10

### Agregado
- Soporte completo para cloud images (Ubuntu, Debian, Rocky Linux)
- Configuración mediante cloud-init
- QEMU Guest Agent habilitado automáticamente
- Templates reutilizables para tipos comunes de servidores
- Modo `--dry-run` para simulación sin crear VMs
- Logging detallado con archivos de log
- Soporte para vendor snippets personalizados
- Configuración de red estática o DHCP
- Claves SSH configurables
- Tags para organización de VMs
- Auto-start de VMs opcional

### Cambiado
- Migración de imágenes ISO a cloud images
- Simplificación de configuración YAML
- Mejora en manejo de errores y validaciones

### Corregido
- Validación de credenciales Proxmox
- Manejo de excepciones en creación de VMs

## [2.0.0] - 2026-01-09

### Agregado
- Uso de biblioteca `proxmoxer` para API de Proxmox
- Creación básica de VMs
- Configuración mediante archivos YAML
- Logs básicos

### Cambiado
- Refactorización completa del código
- Separación de configuración en archivos YAML

## [1.0.0] - Fecha anterior

### Agregado
- Primera versión funcional
- Script básico con `paramiko` y `requests`
- Creación manual de VMs

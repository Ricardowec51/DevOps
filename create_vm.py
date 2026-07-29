#!/usr/bin/env python3
"""
Proxmox VM Creator v3.2.0
Cloud-init con imágenes cloud de Ubuntu y snippet único
Características:
- Checks pre-vuelo (duplicados, espacio)
- Ejecución serializada
"""

import yaml
import logging
import sys
import os
import argparse
import json
from datetime import datetime
from typing import Dict, List
from proxmoxer import ProxmoxAPI
import requests
from dotenv import load_dotenv
from urllib.parse import quote
import platform
import time

# Cargar variables de entorno desde .env
load_dotenv()

requests.packages.urllib3.disable_warnings()

# Crear nombre de archivo de log con timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = f'logs/vm_creation_{timestamp}.log'
log_general = 'vm_creation.log'

# Crear directorio de logs si no existe
os.makedirs('logs', exist_ok=True)

# Configurar logging con dos archivos: uno general y uno por ejecución
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_general),           # Log general (se sobrescribe)
        logging.FileHandler(log_filename),          # Log específico de esta ejecución
        logging.StreamHandler(sys.stdout)           # Consola
    ]
)
logger = logging.getLogger(__name__)

# Log de inicio
logger.info("="*80)
logger.info(f"Proxmox VM Creator v3.2.0 - Ejecución iniciada")
logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info(f"Log de esta ejecución: {log_filename}")
logger.info(f"Sistema: {platform.system()} {platform.release()}")
logger.info(f"Python: {platform.python_version()}")
logger.info("="*80)


class ProxmoxVMCreator:
    def __init__(self, config_file='config.yaml'):
        with open(config_file) as f:
            self.config = yaml.safe_load(f)

        # Obtener credenciales Proxmox (prioridad: .env > config.yaml)
        px = self.config.get('proxmox', {})
        px_host = os.getenv('PROXMOX_HOST', px.get('host'))
        px_user = os.getenv('PROXMOX_USER', px.get('user'))
        px_password = os.getenv('PROXMOX_PASSWORD', px.get('password'))
        px_verify_ssl = os.getenv('PROXMOX_VERIFY_SSL', str(px.get('verify_ssl', False))).lower() == 'true'

        if not all([px_host, px_user, px_password]):
            logger.error("❌ Faltan credenciales de Proxmox (verifica .env o config.yaml)")
            sys.exit(1)

        try:
            logger.info(f"Intentando conectar a Proxmox...")
            logger.info(f"  Host: {px_host}")
            logger.info(f"  Usuario: {px_user}")
            logger.info(f"  Verify SSL: {px_verify_ssl}")

            self.proxmox = ProxmoxAPI(
                px_host,
                user=px_user,
                password=px_password,
                verify_ssl=px_verify_ssl
            )
            logger.info(f"✅ Conectado a Proxmox {px_host}")
        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            logger.exception("Detalles completos del error:")
            sys.exit(1)
    
    def load_templates(self, file='templates.yaml'):
        try:
            with open(file) as f:
                return yaml.safe_load(f).get('templates', {})
        except:
            return {}
    
    def load_vms(self, file=None):
        """Carga VMs desde config.yaml (por defecto) o archivo especificado"""
        if file and file != 'config.yaml':
            with open(file) as f:
                return yaml.safe_load(f).get('vms', [])
        # Por defecto, usar config.yaml ya cargado
        return self.config.get('vms', [])
    
    def merge_config(self, vm):
        if 'template' in vm:
            templates = self.load_templates()
            if vm['template'] in templates:
                base = templates[vm['template']].copy()
                base.update(vm)
                vm = base

        # Defaults desde config.yaml
        defaults = self.config.get('defaults', {})

        # Override con variables de entorno si existen
        env_defaults = {
            'storage': os.getenv('DEFAULT_STORAGE'),
            'memory': os.getenv('DEFAULT_MEMORY'),
            'cores': os.getenv('DEFAULT_CORES'),
            'disk_size': os.getenv('DEFAULT_DISK_SIZE'),
        }

        # Actualizar defaults con env vars (solo si existen)
        for k, v in env_defaults.items():
            if v is not None:
                defaults[k] = int(v) if k in ['memory', 'cores'] else v

        # Aplicar defaults a la VM
        for k, v in defaults.items():
            if k not in vm:
                vm[k] = v

        return vm
    
    def build_params(self, vm):
        params = {
            'vmid': vm['vmid'],
            'name': vm['name'],
            'memory': vm.get('memory', 2048),
            'cores': vm.get('cores', 2),
            'sockets': vm.get('sockets', 1),
            'ostype': vm.get('ostype', 'l26'),
            'onboot': 1 if vm.get('onboot', False) else 0,
            'agent': '1',  # QEMU Agent habilitado
        }
        
        # Obtener imagen cloud
        image_key = vm.get('image', 'ubuntu22')
        if 'images' not in self.config['defaults']:
            logger.error("❌ No hay imágenes configuradas en config.yaml")
            raise ValueError("Configuración de imágenes faltante")
        
        if image_key not in self.config['defaults']['images']:
            logger.error(f"❌ Imagen '{image_key}' no encontrada en config.yaml")
            raise ValueError(f"Imagen {image_key} no existe")
        
        image_path = self.config['defaults']['images'][image_key]
        storage = vm.get('storage', 'local-lvm')
        disk_size = str(vm.get('disk_size', '20G')).rstrip('G')

        # Convertir NFS_SERVER:iso/filename a path absoluto
        if image_path.startswith('NFS_SERVER:iso/'):
            # Extraer el nombre del archivo
            filename = image_path.replace('NFS_SERVER:iso/', '')
            image_path = f"/mnt/pve/NFS_SERVER/template/iso/{filename}"
        elif image_path.startswith('NFS_SERVER:'):
            # Si está en otro subdirectorio
            filename = image_path.replace('NFS_SERVER:', '')
            image_path = f"/mnt/pve/NFS_SERVER/{filename}"

        # Importar disco desde imagen cloud
        params['scsihw'] = 'virtio-scsi-pci'
        params['scsi0'] = f"{storage}:0,import-from={image_path},discard=on"
        
        # Redimensionar disco si es necesario
        if int(disk_size) > 20:  # Las imágenes cloud suelen ser 2-3GB
            params['scsi0'] += f",size={disk_size}G"
        
        # Cloud-init drive
        params['ide2'] = f"{storage}:cloudinit"
        
        # Red
        net_cfg = self.config.get('network', {})
        bridge = vm.get('bridge', os.getenv('NETWORK_BRIDGE', net_cfg.get('bridge', 'vmbr0')))
        model = vm.get('model', net_cfg.get('model', 'virtio'))
        params['net0'] = f"{model},bridge={bridge}"
        
        # Boot desde disco
        params['boot'] = 'order=scsi0'
        
        # Serial console para cloud-init
        params['serial0'] = 'socket'
        params['vga'] = 'serial0'
        
        if 'tags' in vm:
            params['tags'] = vm['tags']

        if 'description' in vm:
            params['description'] = vm['description']

        # Cloud-init: User, Password, SSH Keys desde .env
        params['ciuser'] = os.getenv('VM_DEFAULT_USER', 'rwagner')
        params['cipassword'] = os.getenv('VM_DEFAULT_PASSWORD')

        # SSH keys desde .env (separadas por coma)
        ssh_keys_str = os.getenv('VM_SSH_KEYS', '')
        if ssh_keys_str:
            ssh_keys = ssh_keys_str.replace(',', '\n')
            params['sshkeys'] = quote(ssh_keys, safe='')

        # Configuración de red (prioridad: VM > .env > config.yaml)
        net_cfg = self.config.get('network', {})
        net_type = vm.get('network_type', self.config.get('defaults', {}).get('network_type', 'dhcp'))

        if net_type == 'static' and 'ip' in vm:
            ip = vm['ip']
            mask = vm.get('netmask', os.getenv('NETWORK_NETMASK', net_cfg.get('netmask', '24')))
            gw = vm.get('gateway', os.getenv('NETWORK_GATEWAY', net_cfg.get('gateway')))
            params['ipconfig0'] = f"ip={ip}/{mask},gw={gw}"

            dns = vm.get('nameserver', os.getenv('NETWORK_NAMESERVER', net_cfg.get('nameserver', '8.8.8.8')))
            params['nameserver'] = dns
        else:
            params['ipconfig0'] = 'ip=dhcp'
        
        return params
    
    def wait_for_task(self, node, upid):
        logger.info(f"⏳ Supervisando tarea Proxmox: {upid}")
        while True:
            try:
                task = self.proxmox.nodes(node).tasks(upid).status.get()
                if task['status'] == 'stopped':
                    if task['exitstatus'] == 'OK':
                        logger.info(f"✅ Tarea completada exitosamente")
                        return True
                    else:
                        logger.error(f"❌ Tarea falló: {task['exitstatus']}")
                        return False
            except Exception as e:
                logger.error(f"⚠️ Error verificando tarea: {e}")
            
            time.sleep(2)

    def create_vm(self, vm):
        vmid = vm['vmid']
        name = vm['name']
        node = vm['node']

        logger.info(f"\n🚀 Creando VM {vmid} ({name}) en {node}...")
        logger.info(f"{'─'*80}")

        try:
            # Log de configuración de la VM (antes de crear)
            logger.info(f"📋 Configuración de VM:")
            logger.info(f"   VMID: {vmid}")
            logger.info(f"   Nombre: {name}")
            logger.info(f"   Nodo: {node}")
            logger.info(f"   Memoria: {vm.get('memory', 2048)} MB")
            logger.info(f"   CPU: {vm.get('cores', 2)} cores")
            logger.info(f"   Disco: {vm.get('disk_size', '20G')}")
            logger.info(f"   Imagen: {vm.get('image', 'ubuntu22')}")
            logger.info(f"   Network: {vm.get('network_type', 'dhcp')}")
            if vm.get('ip'):
                logger.info(f"   IP: {vm.get('ip')}")
            if vm.get('tags'):
                logger.info(f"   Tags: {vm.get('tags')}")

            # Limpiar known_hosts en Admin para esta IP (evita error de host key changed)
            if vm.get('ip'):
                ip = vm['ip']
                admin_ip = self.config.get('admin', {}).get('ip', '192.168.1.20')
                import subprocess
                subprocess.run(
                    f"ssh -o StrictHostKeyChecking=no {admin_ip} 'ssh-keygen -f ~/.ssh/known_hosts -R {ip}' 2>/dev/null",
                    shell=True, capture_output=True
                )
                logger.info(f"   🔑 known_hosts limpiado para {ip}")

            params = self.build_params(vm)

            # Log de parámetros completos (para debugging)
            logger.debug(f"📦 Parámetros completos de Proxmox API:")
            # Ocultar SSH keys en el log por seguridad
            safe_params = params.copy()
            if 'sshkeys' in safe_params:
                safe_params['sshkeys'] = f"<{len(vm.get('credentials', {}).get('ssh_keys', []))} SSH keys configuradas>"
            if 'cipassword' in safe_params:
                safe_params['cipassword'] = "<password oculto>"
            logger.debug(json.dumps(safe_params, indent=2, default=str))

            # Crear VM
            logger.info(f"⏳ Enviando petición a Proxmox API...")
            start_time = datetime.now()
            
            # create devuelve el UPID si es exitoso
            upid = self.proxmox.nodes(node).qemu.create(**params)
            
            # Esperar a que termine la creación para evitar problemas de locking en storage
            if upid and isinstance(upid, str):
                if not self.wait_for_task(node, upid):
                    raise Exception(f"Fallo en creación de VM (Task: {upid})")

            # Redimensionar disco si es mayor a 20GB
            disk_size = str(vm.get('disk_size', '20G')).rstrip('G')
            if int(disk_size) > 20:
                logger.info(f"⏳ Redimensionando disco a {disk_size}GB...")
                resize_upid = self.proxmox.nodes(node).qemu(vmid).resize.put(disk='scsi0', size=f"{disk_size}G")
                if resize_upid and isinstance(resize_upid, str):
                    self.wait_for_task(node, resize_upid)
                logger.info(f"✅ Disco redimensionado a {disk_size}GB")

            elapsed_time = (datetime.now() - start_time).total_seconds()

            image_key = vm.get('image', 'ubuntu22')
            logger.info(f"✅ VM {vmid} creada exitosamente en {elapsed_time:.2f}s")
            logger.info(f"   └─ Imagen: {image_key}")
            logger.info(f"   └─ RAM: {params['memory']}MB")
            logger.info(f"   └─ CPU: {params['cores']} cores")
            logger.info(f"   └─ Disco: {params['scsi0']}")
            logger.info(f"   └─ QEMU Agent: Habilitado")
            logger.info(f"   └─ Cloud-init: Configurado")

            # Iniciar si está configurado
            if vm.get('start', False):
                logger.info(f"⏳ Iniciando VM...")
                self.proxmox.nodes(node).qemu(vmid).status.start.post()
                logger.info(f"✅ VM iniciada")

            logger.info(f"{'─'*80}\n")
            return True
        except Exception as e:
            logger.error(f"❌ Error al crear VM {vmid} ({name}): {e}")
            logger.error(f"{'─'*80}")
            logger.error(f"📝 Detalles del error:")
            import traceback
            logger.error(traceback.format_exc())
            logger.error(f"{'─'*80}\n")
            return False
    
            logger.error(f"{'─'*80}\n")
            return False
            
    def check_storage_space(self, node, storage, required_gb):
        try:
            status = self.proxmox.nodes(node).storage(storage).status.get()
            free_bytes = status.get('avail', 0)
            free_gb = free_bytes / (1024**3)
            
            logger.info(f"💾 Storage '{storage}' en {node}: {free_gb:.1f}GB libres (Req: {required_gb}GB)")
            
            if free_gb < required_gb:
                logger.error(f"❌ Espacio INSUFICIENTE en {node}:{storage}. Libres: {free_gb:.1f}GB, Req: {required_gb}GB")
                return False
            return True
        except Exception as e:
            logger.warning(f"⚠️ No se pudo verificar espacio en {node}:{storage} - {e}")
            return True # Asumimos que sí hay espacio si falla el check

    def validate_deployment(self, vms):
        logger.info(f"\n🔍 Ejecutando comprobaciones PRE-VUELO...")
        logger.info(f"{'─'*80}")
        
        errors = []
        
        # 1. Verificar duplicados en config.yaml
        seen_ids = set()
        seen_names = set()
        for vm in vms:
            if vm['vmid'] in seen_ids:
                errors.append(f"❌ ID DUPLICADO en config.yaml: {vm['vmid']}")
            if vm['name'] in seen_names:
                errors.append(f"❌ NOMBRE DUPLICADO en config.yaml: {vm['name']}")
            seen_ids.add(vm['vmid'])
            seen_names.add(vm['name'])

        # 2. Verificar duplicados en Cluster (ID y Nombre)
        try:
            cluster_resources = self.proxmox.cluster.resources.get(type='vm')
            existing_ids = {int(r.get('vmid')) for r in cluster_resources if r.get('vmid')}
            existing_names = {r.get('name') for r in cluster_resources if r.get('name')}
            
            for vm in vms:
                if vm['vmid'] in existing_ids:
                     errors.append(f"❌ ID YA EXISTE en Proxmox: {vm['vmid']} (Conflicts with existing VM)")
                if vm['name'] in existing_names:
                     errors.append(f"❌ NOMBRE YA EXISTE en Proxmox: {vm['name']}")
        except Exception as e:
             logger.warning(f"⚠️ No se pudo consultar el cluster para duplicados: {e}")

        # 3. Verificar espacio en disco (Aprox)
        # Agrupar por nodo/storage
        storage_reqs = {} # key: (node, storage) -> val: total_gb
        
        for vm in vms:
            vm = self.merge_config(vm) # Necesitamos defaults para saber storage y disk_size
            node = vm['node']
            storage = vm.get('storage', self.config['defaults']['storage'])
            size_str = str(vm.get('disk_size', self.config['defaults']['disk_size'])).rstrip('G')
            size_gb = int(size_str)
            
            key = (node, storage)
            storage_reqs[key] = storage_reqs.get(key, 0) + size_gb

        for (node, storage), total_gb in storage_reqs.items():
            if not self.check_storage_space(node, storage, total_gb):
                errors.append(f"❌ Espacio insuficiente en {node}:{storage} para desplegar {total_gb}GB")

        if errors:
            logger.error("\n🛑 ERRORES DE VALIDACIÓN ENCONTRADOS:")
            for err in errors:
                logger.error(err)
            logger.error("\n❌ Cancelando ejecución para evitar desastres.")
            return False
        
        logger.info("✅ Todas las comprobaciones PASARON. El plan es seguro.")
        return True
    
    def run(self, dry_run=False, vms_file=None):
        execution_start = datetime.now()

        # Log de parámetros de ejecución
        logger.info(f"\n{'='*80}")
        logger.info(f"📋 PARÁMETROS DE EJECUCIÓN")
        logger.info(f"{'='*80}")
        logger.info(f"Origen de VMs: {vms_file if vms_file else 'config.yaml'}")
        logger.info(f"Modo: {'DRY-RUN (Simulación)' if dry_run else 'PRODUCCIÓN (Creación real)'}")
        logger.info(f"{'='*80}\n")

        vms = self.load_vms(vms_file)
        logger.info(f"\n{'='*80}")
        logger.info(f"Creando {len(vms)} VM(s) con imágenes cloud")
        logger.info(f"{'='*80}\n")
        
        # Validar antes de hacer nada (incluso en dry-run)
        if not self.validate_deployment(vms) and not dry_run:
             sys.exit(1)

        if dry_run:
            logger.info("⚠️  MODO DRY-RUN - No se crearán VMs reales\n")

        # Tracking detallado
        successful_vms = []
        failed_vms = []

        for vm in vms:
            vm = self.merge_config(vm)

            if dry_run:
                logger.info(f"[DRY-RUN] VM {vm['vmid']} - {vm['name']}")
                logger.info(f"  Nodo: {vm.get('node', 'N/A')}")
                logger.info(f"  Imagen: {vm.get('image', 'ubuntu22')}")
                logger.info(f"  CPU: {vm.get('cores', 2)}, RAM: {vm.get('memory', 2048)}MB")
                logger.info(f"  Disco: {vm.get('disk_size', '20G')}")
                successful_vms.append({
                    'vmid': vm['vmid'],
                    'name': vm['name'],
                    'node': vm.get('node', 'N/A'),
                    'status': 'dry-run'
                })
            else:
                if self.create_vm(vm):
                    successful_vms.append({
                        'vmid': vm['vmid'],
                        'name': vm['name'],
                        'node': vm.get('node', 'N/A'),
                        'memory': vm.get('memory', 2048),
                        'cores': vm.get('cores', 2),
                        'disk': vm.get('disk_size', '20G'),
                        'ip': vm.get('ip', 'DHCP'),
                        'status': 'created'
                    })
                else:
                    failed_vms.append({
                        'vmid': vm['vmid'],
                        'name': vm['name'],
                        'node': vm.get('node', 'N/A'),
                        'status': 'failed'
                    })

        execution_end = datetime.now()
        elapsed_total = (execution_end - execution_start).total_seconds()

        # Resumen final
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 RESUMEN DE EJECUCIÓN")
        logger.info(f"{'='*80}")
        logger.info(f"✅ Exitosas: {len(successful_vms)}")
        logger.info(f"❌ Fallidas: {len(failed_vms)}")
        logger.info(f"⏱️  Tiempo total: {elapsed_total:.2f}s")
        logger.info(f"{'='*80}")

        if successful_vms:
            logger.info(f"\n✅ VMs creadas exitosamente:")
            for vm in successful_vms:
                logger.info(f"   • VM {vm['vmid']} ({vm['name']}) en {vm['node']}")

        if failed_vms:
            logger.info(f"\n❌ VMs que fallaron:")
            for vm in failed_vms:
                logger.info(f"   • VM {vm['vmid']} ({vm['name']}) en {vm['node']}")

        # Guardar resumen en JSON
        summary = {
            'timestamp': execution_end.strftime('%Y-%m-%d %H:%M:%S'),
            'execution_time_seconds': elapsed_total,
            'mode': 'dry-run' if dry_run else 'production',
            'vms_file': vms_file,
            'total_vms': len(vms),
            'successful': len(successful_vms),
            'failed': len(failed_vms),
            'successful_vms': successful_vms,
            'failed_vms': failed_vms
        }

        summary_file = f'logs/summary_{timestamp}.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"\n📄 Resumen guardado en: {summary_file}")
        logger.info(f"{'='*80}\n")

        # Log final
        logger.info(f"{'='*80}")
        logger.info(f"Ejecución finalizada: {execution_end.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Log completo: {log_filename}")
        logger.info(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(description='Proxmox VM Creator con Cloud Images')
    parser.add_argument('--dry-run', action='store_true', help='Simular sin crear VMs')
    parser.add_argument('--config', default='config.yaml', help='Archivo de configuración')
    parser.add_argument('--vms', default=None, help='Archivo de VMs (usa config.yaml por defecto)')
    
    args = parser.parse_args()

    creator = ProxmoxVMCreator(args.config)
    creator.run(dry_run=args.dry_run, vms_file=args.vms)


if __name__ == '__main__':
    main()


#!/usr/bin/env python3
"""
Proxmox VM Creator v3.0
Cloud-init con imágenes cloud de Ubuntu y snippet único
"""

import yaml
import logging
import sys
import argparse
from typing import Dict, List
from proxmoxer import ProxmoxAPI
import requests

requests.packages.urllib3.disable_warnings()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vm_creation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ProxmoxVMCreator:
    def __init__(self, config_file='config.yaml'):
        with open(config_file) as f:
            self.config = yaml.safe_load(f)
        
        px = self.config['proxmox']
        try:
            self.proxmox = ProxmoxAPI(
                px['host'],
                user=px['user'],
                password=px['password'],
                verify_ssl=px.get('verify_ssl', False)
            )
            logger.info(f"✅ Conectado a Proxmox {px['host']}")
        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            sys.exit(1)
    
    def load_templates(self, file='templates.yaml'):
        try:
            with open(file) as f:
                return yaml.safe_load(f).get('templates', {})
        except:
            return {}
    
    def load_vms(self, file='vms.yaml'):
        with open(file) as f:
            return yaml.safe_load(f).get('vms', [])
    
    def merge_config(self, vm):
        if 'template' in vm:
            templates = self.load_templates()
            if vm['template'] in templates:
                base = templates[vm['template']].copy()
                base.update(vm)
                vm = base
        
        defaults = self.config.get('defaults', {})
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
        
        # Importar disco desde imagen cloud
        params['scsi0'] = f"{storage}:0,import-from={image_path},discard=on"
        
        # Redimensionar disco si es necesario
        if int(disk_size) > 20:  # Las imágenes cloud suelen ser 2-3GB
            params['scsi0'] += f",size={disk_size}G"
        
        # Cloud-init drive
        params['ide0'] = f"{storage}:cloudinit"
        
        # Red
        net_cfg = self.config.get('network', {})
        bridge = vm.get('bridge', net_cfg.get('bridge', 'vmbr0'))
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
        
        # Credenciales cloud-init
        creds = vm.get('credentials', self.config.get('credentials', {}))
        if 'user' in creds:
            params['ciuser'] = creds['user']
        if 'password' in creds:
            params['cipassword'] = creds['password']
        
        # Configuración de red
        net_type = vm.get('network_type', self.config['defaults'].get('network_type', 'dhcp'))
        if net_type == 'static' and 'ip' in vm:
            net_cfg = self.config['network']
            ip = vm['ip']
            mask = vm.get('netmask', net_cfg.get('netmask', '24'))
            gw = vm.get('gateway', net_cfg.get('gateway'))
            params['ipconfig0'] = f"ip={ip}/{mask},gw={gw}"
            
            dns = vm.get('nameserver', net_cfg.get('nameserver', '8.8.8.8'))
            params['nameserver'] = dns
        else:
            params['ipconfig0'] = 'ip=dhcp'
        
        # SSH keys
        keys = creds.get('ssh_keys', [])
        if keys:
            params['sshkeys'] = '\n'.join(keys)
        
        # ⭐ SNIPPET ÚNICO para TODAS las VMs
        if 'snippet' in self.config['defaults']:
            snippet = self.config['defaults']['snippet']
            params['cicustom'] = f"vendor={snippet}"
            logger.info(f"  📄 Usando snippet: {snippet}")
        
        return params
    
    def create_vm(self, vm):
        vmid = vm['vmid']
        name = vm['name']
        node = vm['node']
        
        logger.info(f"\n🚀 Creando VM {vmid} ({name}) en {node}...")
        
        try:
            params = self.build_params(vm)
            
            # Crear VM
            self.proxmox.nodes(node).qemu.create(**params)
            
            image_key = vm.get('image', 'ubuntu22')
            logger.info(f"  ✅ VM {vmid} creada")
            logger.info(f"     Imagen: {image_key}")
            logger.info(f"     RAM: {params['memory']}MB")
            logger.info(f"     CPU: {params['cores']} cores")
            logger.info(f"     Disco: {params['scsi0']}")
            logger.info(f"     QEMU Agent: Habilitado")
            logger.info(f"     Cloud-init: Configurado")
            
            # Iniciar si está configurado
            if vm.get('start', False):
                logger.info(f"  ⏳ Iniciando VM...")
                self.proxmox.nodes(node).qemu(vmid).status.start.post()
                logger.info(f"  ✅ VM iniciada")
            
            return True
        except Exception as e:
            logger.error(f"  ❌ Error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def run(self, dry_run=False):
        vms = self.load_vms()
        logger.info(f"\n{'='*60}")
        logger.info(f"Creando {len(vms)} VM(s) con imágenes cloud")
        logger.info(f"{'='*60}\n")
        
        if dry_run:
            logger.info("⚠️  MODO DRY-RUN\n")
        
        success = 0
        failed = 0
        
        for vm in vms:
            vm = self.merge_config(vm)
            
            if dry_run:
                logger.info(f"[DRY-RUN] VM {vm['vmid']} - {vm['name']}")
                logger.info(f"  Imagen: {vm.get('image', 'ubuntu22')}")
                logger.info(f"  CPU: {vm.get('cores', 2)}, RAM: {vm.get('memory', 2048)}MB")
                success += 1
            else:
                if self.create_vm(vm):
                    success += 1
                else:
                    failed += 1
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Exitosas: {success}")
        logger.info(f"❌ Fallidas: {failed}")
        logger.info(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='Proxmox VM Creator con Cloud Images')
    parser.add_argument('--dry-run', action='store_true', help='Simular sin crear VMs')
    parser.add_argument('--config', default='config.yaml', help='Archivo de configuración')
    parser.add_argument('--vms', default='vms.yaml', help='Archivo de VMs')
    
    args = parser.parse_args()
    
    creator = ProxmoxVMCreator(args.config)
    creator.run(dry_run=args.dry_run)


if __name__ == '__main__':
    main()


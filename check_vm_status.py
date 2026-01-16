#!/usr/bin/env python3
"""
Script para verificar el estado detallado de VMs
"""

import yaml
import os
from proxmoxer import ProxmoxAPI
import requests
from dotenv import load_dotenv

load_dotenv()
requests.packages.urllib3.disable_warnings()

# Leer config
with open('config.yaml') as f:
    config = yaml.safe_load(f)

px = config.get('proxmox', {})
px_host = os.getenv('PROXMOX_HOST', px.get('host'))
px_user = os.getenv('PROXMOX_USER', px.get('user'))
px_password = os.getenv('PROXMOX_PASSWORD', px.get('password'))
px_verify_ssl = os.getenv('PROXMOX_VERIFY_SSL', str(px.get('verify_ssl', False))).lower() == 'true'

proxmox = ProxmoxAPI(
    px_host,
    user=px_user,
    password=px_password,
    verify_ssl=px_verify_ssl
)

# VMs problemáticas
# VMs del cluster K3s
problem_vms = [
    (3001, 'DELL', 'k3s-master-01'),
    (3002, 'nuc10', 'k3s-master-02'),
    (3003, 'msa', 'k3s-master-03'),
    (3004, 'BOSC', 'k3s-worker-01'),
    (3005, 'DELL', 'k3s-worker-02'),
    (3006, 'msn2', 'k3s-worker-03'),
    (3007, 'Nnuc13', 'k3s-worker-04'),
    (3008, 'msa', 'k3s-worker-05'),
]

print("\n🔍 Verificando VMs problemáticas...")
print("="*80)

for vmid, node, name in problem_vms:
    print(f"\n📋 VM {vmid} ({name}) en nodo {node}:")
    print("-"*80)

    try:
        # Configuración de la VM
        config = proxmox.nodes(node).qemu(vmid).config.get()

        print(f"  Nombre: {config.get('name', 'N/A')}")
        print(f"  RAM: {config.get('memory', 'N/A')} MB")
        print(f"  CPU: {config.get('cores', 'N/A')} cores")
        print(f"  Disco (scsi0): {config.get('scsi0', 'N/A')}")
        print(f"  Cloud-init (ide0): {config.get('ide0', 'N/A')}")
        print(f"  Agent: {config.get('agent', 'N/A')}")
        print(f"  Boot: {config.get('boot', 'N/A')}")

        # Estado actual
        status = proxmox.nodes(node).qemu(vmid).status.current.get()
        print(f"  Estado: {status.get('status', 'N/A')}")

        # Tasks recientes de esta VM
        print(f"\n  📝 Tasks recientes:")
        tasks = proxmox.nodes(node).tasks.get(vmid=vmid, limit=5)
        if tasks:
            for task in tasks[:3]:
                task_type = task.get('type', 'N/A')
                task_status = task.get('status', 'N/A')
                exitstatus = task.get('exitstatus', 'N/A')
                print(f"    - {task_type}: {task_status} (exit: {exitstatus})")
        else:
            print(f"    (Sin tasks recientes)")

    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "="*80 + "\n")

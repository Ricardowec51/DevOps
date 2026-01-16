#!/usr/bin/env python3
"""
Script para eliminar VMs de Proxmox
"""

import yaml
import os
import sys
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

if len(sys.argv) < 3:
    print("Uso: python delete_vm.py <node> <vmid>")
    print("Ejemplo: python delete_vm.py Nnuc13 9999")
    sys.exit(1)

node = sys.argv[1]
vmid = sys.argv[2]

print(f"\n🗑️  Eliminando VM {vmid} del nodo {node}...")

try:
    # Detener VM si está corriendo
    try:
        status = proxmox.nodes(node).qemu(vmid).status.current.get()
        if status['status'] == 'running':
            print(f"  ⏸️  Deteniendo VM...")
            task = proxmox.nodes(node).qemu(vmid).status.stop.post()
            # Wait for stop
            while True:
                task_status = proxmox.nodes(node).tasks(task).status.get()
                if task_status['status'] == 'stopped':
                    break
                import time
                time.sleep(1)
            time.sleep(2) # Extra safety
    except:
        pass

    # Eliminar VM
    print(f"  🗑️  Enviando orden de borrado...")
    task = proxmox.nodes(node).qemu(vmid).delete()
    
    # Wait for delete
    while True:
        task_status = proxmox.nodes(node).tasks(task).status.get()
        if task_status['status'] == 'stopped':
            if task_status['exitstatus'] == 'OK':
                print(f"  ✅ VM {vmid} eliminada exitosamente\n")
            else:
                print(f"  ❌ Error eliminando VM: {task_status['exitstatus']}\n")
            break
        import time
        time.sleep(1)

except Exception as e:
    if "does not exist" in str(e):
        print(f"  ⚠️  VM no encontrada (ya eliminada?): {e}\n")
        sys.exit(0)
    print(f"  ❌ Error: {e}\n")
    sys.exit(1)

#!/usr/bin/env python3
"""
Script para listar todas las VMs en Proxmox
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

print("\n📋 VMs en el cluster Proxmox:")
print("="*70)

nodes = proxmox.nodes.get()
for node in nodes:
    if node['status'] == 'online':
        print(f"\n🖥️  Nodo: {node['node']}")
        try:
            vms = proxmox.nodes(node['node']).qemu.get()
            if vms:
                for vm in vms:
                    status = "🟢" if vm['status'] == 'running' else "⚪"
                    print(f"  {status} VM {vm['vmid']}: {vm['name']} ({vm['status']})")
            else:
                print("  (Sin VMs)")
        except Exception as e:
            print(f"  Error: {e}")

print("="*70 + "\n")

#!/usr/bin/env python3
"""
Script para listar nodos disponibles en Proxmox
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

print("\n🖥️  Nodos disponibles en Proxmox:")
print("="*50)
nodes = proxmox.nodes.get()
for node in nodes:
    status = "🟢 online" if node['status'] == 'online' else "🔴 offline"
    print(f"  - {node['node']} ({status})")
    print(f"    CPU: {node.get('cpu', 0)*100:.1f}% | RAM: {node.get('mem', 0)/node.get('maxmem', 1)*100:.1f}%")
print("="*50)

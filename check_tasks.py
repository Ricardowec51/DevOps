#!/usr/bin/env python3
"""
Script para ver tasks recientes en Proxmox
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

print("\n📋 Tasks recientes en Proxmox:")
print("="*100)

nodes = ['Nnuc13', 'DELL', 'BOSC', 'msa', 'msn2', 'nuc10']
for node in nodes:
    try:
        tasks = proxmox.nodes(node).tasks.get(limit=20)
        print(f"\n🖥️  Nodo: {node}")
        for task in tasks[:10]:  # Solo las últimas 10
            status = task.get('status', 'unknown')
            task_type = task.get('type', 'N/A')
            upid = task.get('upid', 'N/A')

            # Buscar tareas relacionadas con qmcreate
            if 'qmcreate' in task_type or 'qm' in upid:
                print(f"  {status}: {task_type} - {upid[:80]}")
    except Exception as e:
        print(f"  Error en {node}: {e}")

print("="*100 + "\n")

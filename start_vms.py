#!/usr/bin/env python3
"""
Script para iniciar VMs en Proxmox
"""

import yaml
import os
import sys
from proxmoxer import ProxmoxAPI
import requests
from dotenv import load_dotenv
import time

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

# VMs a iniciar
vms_to_start = [
    (2001, 'Nnuc13', 'web-prod-01'),
    (2002, 'DELL', 'db-prod-01'),
    (2004, 'msa', 'legacy-server'),
    (2005, 'msn2', 'vpn-server'),
    (2010, 'BOSC', 'k8s-master-01'),
    (2011, 'DELL', 'k8s-worker-01'),
    (2012, 'msa', 'k8s-worker-02'),
]

print("\n🚀 Iniciando VMs en Proxmox...")
print("="*70)

success = 0
failed = 0
already_running = 0

for vmid, node, name in vms_to_start:
    try:
        # Verificar estado actual
        status = proxmox.nodes(node).qemu(vmid).status.current.get()
        current_status = status['status']

        if current_status == 'running':
            print(f"⚪ VM {vmid} ({name}) - Ya está corriendo")
            already_running += 1
            continue

        # Iniciar VM
        print(f"⏳ VM {vmid} ({name}) en {node} - Iniciando...", end='', flush=True)
        proxmox.nodes(node).qemu(vmid).status.start.post()

        # Esperar un momento
        time.sleep(2)

        # Verificar que inició
        status = proxmox.nodes(node).qemu(vmid).status.current.get()
        if status['status'] == 'running':
            print(f" ✅")
            success += 1
        else:
            print(f" ⚠️  Estado: {status['status']}")
            failed += 1

    except Exception as e:
        print(f" ❌ Error: {e}")
        failed += 1

print("\n" + "="*70)
print(f"✅ Iniciadas exitosamente: {success}")
print(f"⚪ Ya estaban corriendo: {already_running}")
print(f"❌ Fallidas: {failed}")
print("="*70)

if success > 0 or already_running > 0:
    print("\n📋 Estado final de las VMs:")
    print("="*70)
    for vmid, node, name in vms_to_start:
        try:
            status = proxmox.nodes(node).qemu(vmid).status.current.get()
            icon = "🟢" if status['status'] == 'running' else "⚪"
            print(f"{icon} VM {vmid}: {name} ({status['status']}) - Nodo: {node}")
        except Exception as e:
            print(f"❌ VM {vmid}: Error al verificar - {e}")
    print("="*70)

print("\n✨ Proceso completado!\n")

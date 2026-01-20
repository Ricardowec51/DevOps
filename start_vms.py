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


def start_vms():
    """Inicia todas las VMs definidas en config.yaml"""
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

    # VMs a iniciar desde config.yaml
    vms_list = config.get('vms', [])
    vms_to_start = [(vm['vmid'], vm['node'], vm['name']) for vm in vms_list]

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


if __name__ == "__main__":
    start_vms()

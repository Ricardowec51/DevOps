#!/usr/bin/env python3
"""
Script para verificar VMs específicas en Proxmox
"""

import yaml
import os
from proxmoxer import ProxmoxAPI
import requests
from dotenv import load_dotenv


def check_vms():
    """Verifica el estado de las VMs definidas en config.yaml"""
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

    # VMs que esperamos encontrar (desde config.yaml)
    vms_list = config.get('vms', [])

    # Convertir a dict para fácil acceso
    expected_vms = {
        vm['vmid']: (vm['node'], vm['name']) for vm in vms_list
    }

    print("\n🔍 Verificando VMs creadas:")
    print("="*70)

    for vmid, (node, name) in expected_vms.items():
        try:
            vm_config = proxmox.nodes(node).qemu(vmid).config.get()
            vm_status = proxmox.nodes(node).qemu(vmid).status.current.get()
            status_icon = "🟢" if vm_status['status'] == 'running' else "⚪"
            print(f"{status_icon} VM {vmid}: {vm_config.get('name', 'N/A')} ({vm_status['status']}) - Nodo: {node}")
        except Exception as e:
            print(f"❌ VM {vmid}: NO ENCONTRADA en {node} - {e}")

    print("="*70 + "\n")


if __name__ == "__main__":
    check_vms()

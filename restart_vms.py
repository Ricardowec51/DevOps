#!/usr/bin/env python3
"""
Script to Full Check-Restart K3s Cluster VMs
Required for ssd=1 flag to take effect (Hardware change)
"""

import time
import yaml
import os
from proxmoxer import ProxmoxAPI
import requests
from dotenv import load_dotenv

load_dotenv()
requests.packages.urllib3.disable_warnings()

VMS = [
    {'vmid': 3001, 'node': 'DELL'},
    {'vmid': 3002, 'node': 'nuc10'},
    {'vmid': 3003, 'node': 'msa'},
    {'vmid': 3004, 'node': 'BOSC'},
    {'vmid': 3005, 'node': 'DELL'},
    {'vmid': 3006, 'node': 'msn2'},
    {'vmid': 3007, 'node': 'Nnuc13'},
    {'vmid': 3008, 'node': 'msa'},
]

# Proxmox Setup
with open('config.yaml') as f:
    config = yaml.safe_load(f)

px = config.get('proxmox', {})
px_host = os.getenv('PROXMOX_HOST', px.get('host'))
px_user = os.getenv('PROXMOX_USER', px.get('user'))
px_password = os.getenv('PROXMOX_PASSWORD', px.get('password'))

proxmox = ProxmoxAPI(px_host, user=px_user, password=px_password, verify_ssl=False)

def wait_for_status(node, vmid, target_status, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        current = proxmox.nodes(node).qemu(vmid).status.current.get().get('status')
        if current == target_status:
            return True
        time.sleep(2)
    return False

print("🔄 Restarting VMs to apply Hardware Changes...")
print("="*60)

for vm in VMS:
    vmid = vm['vmid']
    node = vm['node']
    
    print(f"VM {vmid} ({node})...")
    
    # Check if running
    status = proxmox.nodes(node).qemu(vmid).status.current.get().get('status')
    
    if status == 'running':
        print("  🛑 Stopping...")
        try:
            proxmox.nodes(node).qemu(vmid).status.stop.post()
            if wait_for_status(node, vmid, 'stopped'):
                print("     -> Stopped.")
            else:
                print("     ⚠️  Timed out waiting for stop. Forcing...")
                proxmox.nodes(node).qemu(vmid).status.stop.post()
                time.sleep(5)
        except Exception as e:
            print(f"     ❌ Error stopping: {e}")
            
    time.sleep(2)
    
    print("  🚀 Starting...")
    try:
        proxmox.nodes(node).qemu(vmid).status.start.post()
        if wait_for_status(node, vmid, 'running'):
            print("     -> Started.")
        else:
            print("     ❌ Failed to start properly.")
    except Exception as e:
        print(f"     ❌ Error starting: {e}")

    print("-" * 40)

print("\nAll Done.")

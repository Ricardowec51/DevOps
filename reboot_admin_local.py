from proxmoxer import ProxmoxAPI
import os
import time
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings()

load_dotenv()

host = os.getenv('PROXMOX_HOST')
user = os.getenv('PROXMOX_USER')
password = os.getenv('PROXMOX_PASSWORD')

print(f"Connecting to {host}...")
proxmox = ProxmoxAPI(host, user=user, password=password, verify_ssl=False)

nodes = ['BOSC', 'DELL', 'Nnuc13', 'nuc10', 'msa', 'msn2']
admin_vm_id = None
admin_node = None

print("Searching for Admin VM...")
for node in nodes:
    try:
        vms = proxmox.nodes(node).qemu.get()
        for vm in vms:
            if 'admin' in vm.get('name', '').lower() or vm.get('vmid') == '3000': # Guessing 3000 or name
                print(f"Found Admin VM: {vm['name']} (ID: {vm['vmid']}) on {node}")
                admin_vm_id = vm['vmid']
                admin_node = node
                break
    except Exception as e:
        print(f"Error checking node {node}: {e}")
    if admin_vm_id: break

if admin_vm_id:
    print(f"Stopping VM {admin_vm_id}...")
    try:
        proxmox.nodes(admin_node).qemu(admin_vm_id).status.stop.post()
        print("Stop command sent. Waiting 10s...")
        time.sleep(10)
    except Exception as e:
        print(f"Stop failed (maybe already stopped?): {e}")

    print(f"Starting VM {admin_vm_id}...")
    proxmox.nodes(admin_node).qemu(admin_vm_id).status.start.post()
    print("Start command sent successfully.")
else:
    print("Admin VM not found! Please check name/ID.")

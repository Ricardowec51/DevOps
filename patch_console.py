
import yaml
import os
import sys
import time
from proxmoxer import ProxmoxAPI
import requests
from dotenv import load_dotenv

load_dotenv()
requests.packages.urllib3.disable_warnings()

# Load config
try:
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    with open('vms.yaml') as f:
        vms = yaml.safe_load(f)['vms']
except Exception as e:
    print(f"Error loading files: {e}")
    sys.exit(1)

# Connect to Proxmox
px = config.get('proxmox', {})
px_host = os.getenv('PROXMOX_HOST', px.get('host'))
px_user = os.getenv('PROXMOX_USER', px.get('user'))
px_password = os.getenv('PROXMOX_PASSWORD', px.get('password'))
px_verify_ssl = os.getenv('PROXMOX_VERIFY_SSL', str(px.get('verify_ssl', False))).lower() == 'true'

proxmox = ProxmoxAPI(px_host, user=px_user, password=px_password, verify_ssl=px_verify_ssl)

print("🔌 Patching VM Console Settings (vga=std)...")

for vm in vms:
    vmid = vm['vmid']
    node = vm['node']
    print(f"\nProcessing VM {vmid} on {node}...")
    
    try:
        # Update config
        print(f"  📝 Setting cicustom=vendor=NFS_SERVER:snippets/user-data.yaml...")
        proxmox.nodes(node).qemu(vmid).config.post(cicustom='vendor=NFS_SERVER:snippets/user-data.yaml')
        
        # We need to stop and start for this to take effect usually
        status = proxmox.nodes(node).qemu(vmid).status.current.get()
        if status['status'] == 'running':
             print(f"  🔄 Restarting VM to apply changes...")
             proxmox.nodes(node).qemu(vmid).status.shutdown.post()
             
             # Wait for stop
             print("     Waiting for shutdown...")
             for _ in range(30):
                 s = proxmox.nodes(node).qemu(vmid).status.current.get()
                 if s['status'] == 'stopped':
                     break
                 time.sleep(2)
            
             # Start
             print("     Starting...")
             proxmox.nodes(node).qemu(vmid).status.start.post()
             print("  ✅ Done.")
        else:
             print("  ✅ Config updated (VM was stopped).")

    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n🎉 All VMs patched.")

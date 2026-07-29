
from lib.proxmox_client import ProxmoxClient
from lib.config import Config
import sys

cfg = Config()
client = ProxmoxClient(cfg)

if not client.connect():
    print("Failed to connect")
    sys.exit(1)

# Check VM 3001 on DELL
node = "DELL"
vmid = 3001

try:
    print(f"Checking VM {vmid} on {node}...")
    vm = client.get_vm(node, vmid)
    conf = vm.config.get()
    
    # Check for cloudinit drive
    found = False
    for key, value in conf.items():
        val_str = str(value)
        if "media=cdrom" in val_str and "cloudinit" in val_str:
            print(f"Found Cloud-Init Drive: {key}: {val_str}")
            found = True
        elif key == "ide2" and "cloudinit" in val_str: 
             print(f"Found Cloud-Init Drive: {key}: {val_str}")
             found = True
             
    if not found:
        print("No Cloud-Init drive explicitly identified (might be detached or standard cdrom)")
        # Print ide2 anyway if exists
        if "ide2" in conf:
            print(f"ide2 content: {conf['ide2']}")

except Exception as e:
    print(f"Error getting config: {e}")

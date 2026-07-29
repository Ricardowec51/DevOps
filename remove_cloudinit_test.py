
from lib.core.proxmox import ProxmoxClient
from lib.core.config import Config
import sys
import time

cfg = Config()
client = ProxmoxClient(cfg)

if not client.connect():
    print("Failed to connect")
    sys.exit(1)

# Target VM
node = "nuc10" # VM 3002 is on nuc10 according to vms.yaml
vmid = 3002

try:
    print(f"Checking VM {vmid} on {node}...")
    vm = client.get_vm(node, vmid)
    conf = vm.config.get()
    
    # Check for cloudinit drive
    drive_key = None
    for key, value in conf.items():
        val_str = str(value)
        if "cloudinit" in val_str:
            print(f"Found Cloud-Init Drive: {key}: {val_str}")
            drive_key = key
            break
            
    if drive_key:
        print(f"Removing {drive_key}...")
        # To remove, we generally verify strict parameters. 
        # Using 'delete' config option or setting to none. 
        # With proxmoxer: vm.config.post(delete=drive_key)
        vm.config.post(delete=drive_key)
        print("Drive removed. Verifying...")
        
        # Verify removal
        conf_new = vm.config.get()
        if drive_key not in conf_new:
             print("✅ Drive successfully removed from config.")
        else:
             print("⚠️  Drive key still present in config (might need reload).")
             
        print("Rebooting VM...")
        vm.status.reboot.post()
        print("Reboot signal sent.")
        
    else:
        print("No Cloud-Init drive found to remove.")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

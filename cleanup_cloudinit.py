import sys
import time
from lib.core.proxmox import ProxmoxClient
from lib.core.config import Config
from lib.core.logger import log

def main():
    cfg = Config()
    client = ProxmoxClient(cfg)
    
    if not client.connect():
        sys.exit(1)

    log.info("🧹 Starting Cloud-Init Cleanup for Cluster Nodes...")
    
    # Get all VMs from config
    all_vms = cfg.vms
    
    for vm_conf in all_vms:
        vmid = vm_conf['vmid']
        name = vm_conf['name']
        node = vm_conf['node']
        
        log.info(f"🔍 Checking VM {name} ({vmid}) on node {node}...")
        
        # Remove Cloud-Init Drive
        if client.remove_cloudinit_drive(node, vmid):
            log.info(f"   ✨ Successfully removed Cloud-Init drive from {name}.")
            # Reboot checking
            log.info(f"   🔄 Rebooting {name} to apply changes...")
            try:
                vm_obj = client.get_vm(node, vmid)
                vm_obj.status.reboot.post()
                log.info(f"   ✅ Reboot signal sent to {name}.")
            except Exception as e:
                log.error(f"   ⚠️ Failed to reboot {name}: {e}")
        else:
            log.info(f"   🆗 No action needed for {name}.")

    log.info("🎉 Cleanup completed.")

if __name__ == "__main__":
    main()

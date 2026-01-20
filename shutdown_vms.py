
import questionary
from lib.config import Config
from lib.proxmox_client import ProxmoxClient
from lib.logger import log

def shutdown_vms_interactive():
    cfg = Config()
    client = ProxmoxClient(cfg)
    
    if not client.connect():
        return

    log.info("🔍 Scanning running VMs...")
    
    # Filter only VMs defined in our config
    defined_vms = cfg.vms
    running_choices = []
    
    for vm_def in defined_vms:
        vmid = vm_def['vmid']
        node = vm_def['node']
        name = vm_def['name']
        
        try:
            # Check actual status
            current = client.get_vm(node, vmid).status.current.get()
            if current['status'] == 'running':
                # Determine Role
                role = "🎯 Worker" if "worker" in name else "👑 Master" if "master" in name else "🖥️  VM"
                
                label = f"{role:<10} | {name:<20} | Node: {node:<8} | IP: {vm_def.get('ip', 'N/A')}"
                running_choices.append(questionary.Choice(title=label, value=vm_def))
                
        except Exception:
            # VM might not exist or be unreachable
            continue

    if not running_choices:
        log.warning("🚫 No running VMs found from configuration.")
        return

    selected_vms = questionary.checkbox(
        "Select VMs to SHUTDOWN (ACPI):",
        choices=running_choices
    ).ask()

    if not selected_vms:
        log.info("❌ No VMs selected.")
        return

    for vm in selected_vms:
        vmid = vm['vmid']
        node = vm['node']
        name = vm['name']
        
        try:
            log.info(f"🌙 Shutting down {name} on {node}...")
            client.get_vm(node, vmid).status.shutdown.post()
        except Exception as e:
            log.error(f"❌ Failed to shutdown {name}: {e}")

    log.info("✅ Shutdown commands sent.")

if __name__ == "__main__":
    shutdown_vms_interactive()

from lib.proxmox_client import ProxmoxClient
from lib.config import Config
import sys
import time


def remove_cloudinit_all():
    """Remueve el cloud-init drive de todas las VMs definidas en vms.yaml"""
    cfg = Config()
    client = ProxmoxClient(cfg)

    if not client.connect():
        print("Failed to connect")
        return False

    # Obtener VMs desde config
    vms_to_process = {vm['vmid']: vm['node'] for vm in cfg.vms}

    print(f"Processing {len(vms_to_process)} VMs...")

    for vmid, node in vms_to_process.items():
        try:
            print(f"\n--- Processing VM {vmid} on {node} ---")
            try:
                vm = client.get_vm(node, vmid)
                conf = vm.config.get()
            except Exception as e:
                print(f"❌ Error getting config for VM {vmid}: {e}")
                continue

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
                try:
                    vm.config.post(delete=drive_key)
                    print("✅ Drive removed.")
                except Exception as e:
                    print(f"❌ Error removing drive from VM {vmid}: {e}")
            else:
                print("ℹ️  No Cloud-Init drive found (already removed?).")

        except Exception as e:
            print(f"❌ Unexpected error for VM {vmid}: {e}")

    print("\n✅ All VMs processed.")
    return True


if __name__ == "__main__":
    remove_cloudinit_all()

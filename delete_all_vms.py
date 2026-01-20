
import yaml
import subprocess
import sys

def load_vms(file='config.yaml'):
    with open(file) as f:
        return yaml.safe_load(f).get('vms', [])

def delete_vms():
    vms = load_vms()
    print(f"🗑️  Starting cleanup of {len(vms)} VMs...")
    
    for vm in vms:
        vmid = vm['vmid']
        node = vm['node']
        print(f"  👉 Deleting VM {vmid} from {node}...")
        
        # Call delete_vm.py
        # Using the same venv python
        cmd = [sys.executable, "delete_vm.py", node, str(vmid)]
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Failed to delete VM {vmid}: {e}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    delete_vms()

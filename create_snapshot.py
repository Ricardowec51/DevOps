#!/usr/bin/env python3
"""
Script to Create Snapshots for K3s Cluster VMs
"""
import time
from lib.config import Config
from lib.proxmox_client import ProxmoxClient
from lib.logger import log

SNAPSHOT_NAME = "Pre-K3s-Install"
SNAPSHOT_DESC = "Estado limpio antes de instalar K3s HA Cluster (Discos redimensionados y optimizados)"

def wait_for_task(client, node, upid):
    while True:
        task = client.get_node(node).tasks(upid).status.get()
        if task['status'] == 'stopped':
            if task['exitstatus'] == 'OK':
                return True, "OK"
            else:
                return False, task['exitstatus']
        time.sleep(1)

def create_snapshots():
    cfg = Config()
    client = ProxmoxClient(cfg)
    
    if not client.connect():
        return

    log.info(f"📸 Creating Snapshot '{SNAPSHOT_NAME}' for all VMs...")
    log.info("="*60)

    for vm in cfg.vms:
        vmid = vm['vmid']
        node = vm['node']
        
        log.info(f"VM {vmid} ({node})...")
        
        try:
            # Check if snapshot already exists
            existing = client.get_vm(node, vmid).snapshot.get()
            if any(s['name'] == SNAPSHOT_NAME for s in existing):
                log.warning(f"  ⚠️  Snapshot '{SNAPSHOT_NAME}' already exists. Skipping.")
                continue

            log.info("  ⏳ Taking snapshot...")
            upid = client.get_vm(node, vmid).snapshot.post(
                snapname=SNAPSHOT_NAME,
                description=SNAPSHOT_DESC,
                vmstate=1 # Include RAM configuration
            )
            
            success, msg = wait_for_task(client, node, upid)
            if success:
                 log.info("     ✅ Snapshot Created.")
            else:
                 log.error(f"     ❌ Snapshot Failed: {msg}")
                 log.info("     🔄 Retrying without RAM (vmstate=0)...")
                 upid = client.get_vm(node, vmid).snapshot.post(
                    snapname=SNAPSHOT_NAME,
                    description=SNAPSHOT_DESC,
                    vmstate=0
                )
                 success, msg = wait_for_task(client, node, upid)
                 if success:
                     log.info("     ✅ Snapshot Created (Disk Only).")
                 else:
                     log.error(f"     ❌ Snapshot Failed Again: {msg}")

        except Exception as e:
            log.error(f"     ❌ Error: {e}")

    log.info("\n" + "="*60)
    log.info("Done. Ready for installation.")

if __name__ == "__main__":
    create_snapshots()

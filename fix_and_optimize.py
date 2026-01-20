#!/usr/bin/env python3
"""
Script to Fix & Optimize K3s Cluster VMs
1. Resizes disks to correct size (200G for Masters, 400G for Workers)
2. Enables SSD emulation (ssd=1)
3. Expands filesystem inside VM
"""

import time
import subprocess
import yaml
import os
from proxmoxer import ProxmoxAPI
import requests
from dotenv import load_dotenv


def fix_and_optimize():
    """Optimiza las VMs del cluster K3s: resize disk, SSD flag, expand FS"""
    load_dotenv()
    requests.packages.urllib3.disable_warnings()

    # Configuration
    VMS = [
        {'vmid': 3001, 'node': 'DELL',   'size': '200G', 'ip': '192.168.1.21'},
        {'vmid': 3002, 'node': 'nuc10',  'size': '200G', 'ip': '192.168.1.22'},
        {'vmid': 3003, 'node': 'msa',    'size': '200G', 'ip': '192.168.1.23'},
        {'vmid': 3004, 'node': 'BOSC',   'size': '400G', 'ip': '192.168.1.24'},
        {'vmid': 3005, 'node': 'DELL',   'size': '400G', 'ip': '192.168.1.25'},
        {'vmid': 3006, 'node': 'msn2',   'size': '400G', 'ip': '192.168.1.26'},
        {'vmid': 3007, 'node': 'Nnuc13', 'size': '400G', 'ip': '192.168.1.27'},
        {'vmid': 3008, 'node': 'msa',    'size': '400G', 'ip': '192.168.1.28'},
    ]

    # Proxmox Setup
    with open('config.yaml') as f:
        config = yaml.safe_load(f)

    px = config.get('proxmox', {})
    px_host = os.getenv('PROXMOX_HOST', px.get('host'))
    px_user = os.getenv('PROXMOX_USER', px.get('user'))
    px_password = os.getenv('PROXMOX_PASSWORD', px.get('password'))

    proxmox = ProxmoxAPI(px_host, user=px_user, password=px_password, verify_ssl=False)

    def run_ssh(ip, cmd):
        """Runs SSH command with strict checking disabled"""
        ssh_cmd = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null rwagner@{ip} '{cmd}'"
        return subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)

    print("🚀 Starting Disk Fix & Optimization...")
    print("="*60)

    for vm in VMS:
        vmid = vm['vmid']
        node = vm['node']
        size = vm['size']
        ip = vm['ip']

        print(f"\nProcessing VM {vmid} ({ip})...")

        try:
            # 1. Resize Disk
            print(f"  💾 Resizing disk to {size}...")
            proxmox.nodes(node).qemu(vmid).resize.put(disk='scsi0', size=size)

            # 2. Enable SSD Emulation
            print(f"  ⚡ Enabling SSD emulation...")
            vm_config = proxmox.nodes(node).qemu(vmid).config.get()
            current_scsi0 = vm_config.get('scsi0', '')

            if 'ssd=1' not in current_scsi0:
                new_scsi0 = f"{current_scsi0},ssd=1"
                proxmox.nodes(node).qemu(vmid).config.set(scsi0=new_scsi0)
                print("     -> SSD flag enabled.")
            else:
                print("     -> SSD flag already active.")

            # 3. Expand Filesystem inside VM
            print(f"  📈 Expanding filesystem inside Guest...")

            # Grow partition
            res = run_ssh(ip, "sudo growpart /dev/sda 1")
            if res.returncode != 0 and "NOCHANGE" not in res.stdout:
                 print(f"     ⚠️  Growpart issue: {res.stderr.strip()}")

            # Resize FS
            run_ssh(ip, "sudo resize2fs /dev/sda1")

            # Check result
            res = run_ssh(ip, "df -h / | grep /")
            print(f"     ✅ New Size: {res.stdout.strip()}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("\n" + "="*60)
    print("Done.")


if __name__ == "__main__":
    fix_and_optimize()

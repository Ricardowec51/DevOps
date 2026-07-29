#!/usr/bin/env python3
"""
Shutdown Script for Nightly Power Save (msa & msn2)
===================================================
This script identifies VMs running on specific Proxmox nodes (msa, msn2)
and gracefully shuts them down before powering off the physical nodes.

Targets:
- Node: msa
  - VMs: k3s-master-03 (3003), k3s-worker-05 (3008)
- Node: msn2
  - VMs: k3s-worker-03 (3006)

Usage:
    ./shutdown_target_nodes.py
"""

import os
import sys
import time
import requests
import urllib3
from proxmoxer import ProxmoxAPI
from dotenv import load_dotenv

# Disable SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target Nodes to Shutdown
TARGET_NODES = ["msa", "msn2"]

def get_proxmox_connection():
    """Connects to Proxmox API using .env credentials."""
    load_dotenv()
    host = os.getenv("PROXMOX_HOST")
    user = os.getenv("PROXMOX_USER")
    password = os.getenv("PROXMOX_PASSWORD")
    
    if not all([host, user, password]):
        print("❌ Error: Missing credentials in .env file")
        sys.exit(1)

    try:
        proxmox = ProxmoxAPI(
            host,
            user=user,
            password=password,
            verify_ssl=False,
            timeout=10
        )
        # Verify connection
        proxmox.version.get()
        return proxmox
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

def shutdown_vms_on_node(proxmox, node):
    """Finds and shuts down running VMs on a specific node."""
    print(f"\n🔍 Scanning node '{node}' for running VMs...")
    
    try:
        vms = proxmox.nodes(node).qemu.get()
    except Exception as e:
        print(f"⚠️  Could not list VMs on node {node}. Is it already offline? ({e})")
        return

    running_vms = [vm for vm in vms if vm.get('status') == 'running']
    
    if not running_vms:
        print(f"✅ No running VMs found on {node}.")
        return

    print(f"🛑 Found {len(running_vms)} running VMs on {node}. Shutting down...")
    
    for vm in running_vms:
        vmid = vm['vmid']
        name = vm.get('name', 'Unknown')
        print(f"   PLEASE WAIT: Shutting down VM {vmid} ({name})...")
        try:
            proxmox.nodes(node).qemu(vmid).status.shutdown.post()
        except Exception as e:
            print(f"   ❌ Failed to send shutdown command to {name}: {e}")

    # Wait for VMs to stop
    print(f"⏳ Waiting for VMs on {node} to stop...", end="", flush=True)
    max_retries = 180  # Wait up to 3 minutes
    while max_retries > 0:
        still_running = [
            vm['vmid'] for vm in proxmox.nodes(node).qemu.get() 
            if vm.get('status') == 'running'
        ]
        if not still_running:
            print(" Done! ✅")
            break
        time.sleep(1)
        if max_retries % 5 == 0:
            print(".", end="", flush=True)
        max_retries -= 1
    else:
        print("\n⚠️  Timeout waiting for VMs to stop. Proceeding anyway.")

def shutdown_physical_node(proxmox, node):
    """Sends shutdown command to the physical Proxmox node."""
    print(f"💤  Shutting down physical node: {node}...")
    try:
        # PVE API command to shutdown node
        proxmox.nodes(node).status.post(command="shutdown")
        print(f"✅ Shutdown signal sent to {node}.")
    except Exception as e:
        print(f"❌ Failed to shutdown node {node}: {e}")

def main():
    print("🌙 Nightly Shutdown Script for msa & msn2")
    print("=========================================")
    
    proxmox = get_proxmox_connection()
    
    for node in TARGET_NODES:
        shutdown_vms_on_node(proxmox, node)
        shutdown_physical_node(proxmox, node)
        
    print("\n👋 Nightly shutdown sequence initiated. Goodnight!")

if __name__ == "__main__":
    main()


import os
import yaml
from proxmoxer import ProxmoxAPI
import requests
requests.packages.urllib3.disable_warnings()

with open('config.yaml') as f: config = yaml.safe_load(f)
px = config.get('proxmox', {})
proxmox = ProxmoxAPI(
    os.getenv('PROXMOX_HOST', px.get('host')),
    user=os.getenv('PROXMOX_USER', px.get('user')),
    password=os.getenv('PROXMOX_PASSWORD', px.get('password')),
    verify_ssl=False
)

print("Listing VMs...")
for node in proxmox.nodes.get():
    if node['status'] != 'online': continue
    print(f"Node: {node['node']}")
    for vm in proxmox.nodes(node['node']).qemu.get():
        if vm['vmid'] == '1102' or vm['name'] == 'k3s-admin':
            print(f"  FOUND {vm['name']} (ID: {vm['vmid']}) - Status: {vm['status']}")
            try:
                # Try to get IP from agent
                if vm['status'] == 'running':
                    interfaces = proxmox.nodes(node['node']).qemu(vm['vmid']).agent.network_get_interfaces.get()
                    for iface in interfaces.get('result', []):
                        for ip in iface.get('ip-addresses', []):
                            if ip['ip-address-type'] == 'ipv4' and ip['ip-address'] != '127.0.0.1':
                                print(f"    IP: {ip['ip-address']}")
            except Exception as e:
                print(f"    Could not get agent info: {e}")

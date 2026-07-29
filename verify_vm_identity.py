from proxmoxer import ProxmoxAPI
import os
from dotenv import load_dotenv
import urllib3
import re

urllib3.disable_warnings()
load_dotenv()

host = os.getenv('PROXMOX_HOST')
user = os.getenv('PROXMOX_USER')
password = os.getenv('PROXMOX_PASSWORD')

proxmox = ProxmoxAPI(host, user=user, password=password, verify_ssl=False)

node = 'BOSC'
vmid = '1102'

try:
    config = proxmox.nodes(node).qemu(vmid).config.get()
    print(f"Config for VM {vmid} ({node}):")
    # Look for net0 or similar
    for key, value in config.items():
        if key.startswith('net'):
            print(f"{key}: {value}")
            # Extract MAC
            match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', value)
            if match:
                mac = match.group(0)
                print(f"MAC found: {mac}")
                expected_mac = "bc:24:11:63:07:27"
                if mac.lower() == expected_mac.lower():
                    print("✅ MATCHES Known Admin VM MAC!")
                else:
                    print(f"❌ DOES NOT MATCH expected MAC ({expected_mac})")
except Exception as e:
    print(f"Error: {e}")

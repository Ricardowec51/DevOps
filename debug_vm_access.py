
import yaml
import os
import sys
import time
from proxmoxer import ProxmoxAPI
import requests
from dotenv import load_dotenv

load_dotenv()
requests.packages.urllib3.disable_warnings()

# Load config
with open('config.yaml') as f:
    config = yaml.safe_load(f)

px = config.get('proxmox', {})
px_host = os.getenv('PROXMOX_HOST', px.get('host'))
px_user = os.getenv('PROXMOX_USER', px.get('user'))
px_password = os.getenv('PROXMOX_PASSWORD', px.get('password'))
px_verify_ssl = os.getenv('PROXMOX_VERIFY_SSL', str(px.get('verify_ssl', False))).lower() == 'true'

proxmox = ProxmoxAPI(
    px_host,
    user=px_user,
    password=px_password,
    verify_ssl=px_verify_ssl
)

node = "DELL"
vmid = 3001

print(f"🕵️  Debugging VM {vmid} on {node}...")

# 1. Check Agent Status
try:
    status = proxmox.nodes(node).qemu(vmid).agent('ping').post()
    print("✅ QEMU Agent is RUNNING (Ping successful)")
except Exception as e:
    print(f"❌ QEMU Agent NOT reachable: {e}")
    print("   (Cannot proceed with file inspection)")
    sys.exit(1)

def cat_file(path):
    print(f"\n📂 Reading {path}:")
    try:
        # exec command
        res = proxmox.nodes(node).qemu(vmid).agent('exec').post(
            command=['cat', path]
        )
        pid = res['pid']
        
        # wait for result
        retries = 10
        while retries > 0:
            status = proxmox.nodes(node).qemu(vmid).agent('exec-status').get(pid=pid)
            if status['exited'] == 1:
                if status['exitcode'] == 0:
                    content = status['out-data']
                    print("--- CONTENT START ---")
                    print(content)
                    print("--- CONTENT END ---")
                else:
                    print(f"❌ Error reading file (Exit code {status['exitcode']})")
                    if 'err-data' in status:
                        print(f"   Stderr: {status['err-data']}")
                return
            time.sleep(1)
            retries -= 1
        print("❌ Timeout waiting for command")
    except Exception as e:
        print(f"❌ Exception: {e}")

# 2. Check Authorized Keys
cat_file('/home/ubuntu/.ssh/authorized_keys')

# 3. Check Cloud Init Logs (Tail)
print(f"\n📂 Tailing cloud-init output log:")
try:
    res = proxmox.nodes(node).qemu(vmid).agent('exec').post(
        command=['tail', '-n', '20', '/var/log/cloud-init-output.log']
    )
    pid = res['pid']
    # wait...
    time.sleep(2)
    status = proxmox.nodes(node).qemu(vmid).agent('exec-status').get(pid=pid)
    if status.get('out-data'):
        print(status['out-data'])
except:
    pass

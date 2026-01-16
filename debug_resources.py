
import yaml
import os
import json
from proxmoxer import ProxmoxAPI
import requests
from dotenv import load_dotenv

load_dotenv()
requests.packages.urllib3.disable_warnings()

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

try:
    print("Querying cluster resources...")
    resources = proxmox.cluster.resources.get(type='vm')
    if resources:
        print(f"Found {len(resources)} resources.")
        print("First item keys:", resources[0].keys())
        print("Sample item:", json.dumps(resources[0], indent=2))
    else:
        print("No resources found.")
except Exception as e:
    print(e)

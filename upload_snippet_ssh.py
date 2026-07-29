from proxmoxer import ProxmoxAPI
import os
import sys
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings()

load_dotenv()

host = os.getenv('PROXMOX_HOST')
user = os.getenv('PROXMOX_USER')
password = os.getenv('PROXMOX_PASSWORD')

if not all([host, user, password]):
    print("Error: Missing Proxmox credentials in .env")
    sys.exit(1)

print(f"Connecting to {host}...")
proxmox = ProxmoxAPI(host, user=user, password=password, verify_ssl=False)

# Target
node = 'BOSC' # Pick a node that has access to the storage
storage = 'NFS_SERVER'
filename = 'user-data.yaml'
local_file = 'user-data.yaml'

try:
    with open(local_file, 'r') as f:
        content = f.read()
    
    # Check if snippets directory exists? API handles this usually with 'snippets' type.
    # Uploading via POST to /nodes/{node}/storage/{storage}/content
    # filename needs to be 'snippets/user-data.yaml' ideally? Or just 'user-data.yaml' and it puts it in type folder?
    # Usually we specify 'filename' and 'content', 'vmid' etc.
    # For snippets/vzdump/iso, we use 'content' type.
    
    # Official endpoint allows uploading ISO/VZTmpl. Snippet support might be tricky via raw content post if not strictly 'iso'.
    # Alternative: SSH using paramiko since valid creds are known.
    pass
except Exception as e:
    print(f"Error reading local file: {e}")
    sys.exit(1)

# Switching to Paramiko for reliability as 'content' upload API for snippets is sometimes restricted to ISOs/Images.
import paramiko

print(f"Uploading {local_file} via SSH to {host}...")
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user.split('@')[0], password=password) # root@pam -> root
    
    sftp = ssh.open_sftp()
    
    # Ensure remote directory exists
    remote_path = f"/mnt/pve/{storage}/snippets/{filename}"
    remote_dir = f"/mnt/pve/{storage}/snippets"
    
    try:
        sftp.stat(remote_dir)
    except IOError:
        print(f"Creating remote directory {remote_dir}...")
        ssh.exec_command(f"mkdir -p {remote_dir}")
    
    sftp.put(local_file, remote_path)
    print(f"✅ Successfully uploaded to {remote_path}")
    
    sftp.close()
    ssh.close()
except Exception as e:
    print(f"❌ SSH Upload failed: {e}")
    sys.exit(1)

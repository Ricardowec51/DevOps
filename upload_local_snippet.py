import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('PROXMOX_HOST')
user = os.getenv('PROXMOX_USER') # root@pam
password = os.getenv('PROXMOX_PASSWORD')

# Clean user for SSH (remove @pam)
ssh_user = "root"

print(f"🚀 Uploading user-data.yaml to {host} (Local Storage)...")

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=ssh_user, password=password)
    
    sftp = ssh.open_sftp()
    
    remote_dir = "/var/lib/vz/snippets"
    remote_path = f"{remote_dir}/user-data.yaml"
    local_path = "user-data.yaml"
    
    # Ensure dir exists
    try:
        sftp.stat(remote_dir)
    except IOError:
        print(f"Creating {remote_dir}...")
        ssh.exec_command(f"mkdir -p {remote_dir}")

    sftp.put(local_path, remote_path)
    print(f"✅ Uploaded to {remote_path}")
    
    sftp.close()
    ssh.close()
except Exception as e:
    print(f"❌ Failed: {e}")

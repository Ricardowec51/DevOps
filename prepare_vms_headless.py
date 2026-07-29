#!/usr/bin/env python3
"""
Headless VM Preparation Script
based on Ricardowec51/Initial/init-script.sh
Executes safe initialization steps on all K3s cluster nodes.
"""

import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

VMS = [
    "192.168.1.21", "192.168.1.22", "192.168.1.23",  # Masters
    "192.168.1.24", "192.168.1.25", "192.168.1.26", "192.168.1.27", "192.168.1.28" # Workers
]

USER = "rwagner"

# Define the remote bash script content executed on each node
REMOTE_SCRIPT = r"""
#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive

echo "🚀 Starting Host Initialization on $(hostname)..."

# 1. Sudo without password
echo "   [1/5] Configuring Sudo..."
echo "$(whoami) ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/$(whoami) > /dev/null
sudo chmod 0440 /etc/sudoers.d/$(whoami)

# 2. System Updates
echo "   [2/5] Updating System..."
sudo apt-get update -qq
# sudo apt-get upgrade -y -qq # Skipping heavy upgrade to save time, uncomment if needed

# 3. Utilities
echo "   [3/5] Installing Utilities..."
sudo apt-get install -y -qq httpie glances htop curl git net-tools

# 4. Timezone
echo "   [4/5] Setting Timezone to America/Guayaquil..."
sudo timedatectl set-timezone America/Guayaquil
sudo timedatectl set-ntp on

# 5. Zsh Setup (Simplified Check)
echo "   [5/5] Checking Zsh..."
if [ ! -f "$HOME/.zshrc" ]; then
    echo "       Installing Zsh config..."
    # Using the user's Zsh installer URL but handling it non-interactively if possible
    # For speed/safety in this batch run, we install base Zsh. 
    # Full OMZ might require interaction or more complex handling.
    sudo apt-get install -y -qq zsh
else
    echo "       Zsh already configured."
fi

echo "✅ Initialization Complete for $(hostname)"
"""

def prepare_node(ip):
    print(f"🔄 Connecting to {ip}...")
    try:
        # Run the script via SSH
        cmd = [
            "ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", 
            f"{USER}@{ip}", "bash -s"
        ]
        
        process = subprocess.run(cmd, input=REMOTE_SCRIPT, text=True, capture_output=True)
        
        if process.returncode == 0:
            return f"✅ {ip}: Success\n{process.stdout}"
        else:
            return f"❌ {ip}: Failed\n{process.stderr}"
            
    except Exception as e:
        return f"❌ {ip}: Error - {str(e)}"

print(f"🚀 Starting Mass Preparation on {len(VMS)} nodes...")
print("="*60)

with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(prepare_node, VMS))

for res in results:
    print(res)
    print("-" * 40)

print("\nAll nodes processed.")

#!/bin/bash
# Force copy SSH keys to all VMs (192.168.1.21 - 28)
# Password is: Gnehid.30

KEY_FILE="$HOME/.ssh/id_ed25519.pub"
USER="rwagner"

echo "🔑 Starting SSH Key Injection using ssh-copy-id..."
echo "For each VM, you may be asked for the password: Gnehid.30"
echo "--------------------------------------------------------"

for i in {21..28}; do
    IP="192.168.1.$i"
    echo ""
    echo "👉 Processing $IP..."
    
    # Remove old fingerprint to avoid conflicts
    ssh-keygen -f "$HOME/.ssh/known_hosts" -R "$IP" >/dev/null 2>&1
    
    # Copy ID
    # -o StrictHostKeyChecking=no avoids the "Are you sure..." prompt
    ssh-copy-id -o StrictHostKeyChecking=no -i "$KEY_FILE" "$USER@$IP"
done

echo ""
echo "✅ All done. Run ./verify_ssh.sh to test connectivity."

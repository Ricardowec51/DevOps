#!/bin/bash

# Routine to verify SSH connectivity to K3s Cluster VMs (192.168.1.21 - 192.168.1.28)
# User: ubuntu (default for Cloud Images)

echo "🔍 Starting SSH connectivity check..."
echo "----------------------------------------"

for i in {21..28}; do
    IP="192.168.1.$i"
    
    # Check if VM is reachable via SSH
    # -o StrictHostKeyChecking=no: Don't prompt for known_hosts
    # -o ConnectTimeout=5: Fail fast if down
    # -o BatchMode=yes: Don't prompt for password (fail if keys not working)
    
    OUTPUT=$(ssh -o StrictHostKeyChecking=no -o GlobalKnownHostsFile=/dev/null -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 -o BatchMode=yes rwagner@$IP "hostname" 2>&1)
    
    if [ $? -eq 0 ]; then
        echo "✅ $IP: Connected (Host: $OUTPUT)"
    else
        echo "❌ $IP: Failed ($OUTPUT)"
    fi
done

echo "----------------------------------------"
echo "Done."

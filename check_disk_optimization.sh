#!/bin/bash
echo "🔍 Checking Disk Optimization (Discard/TRIM & SSD flag)..."
echo "--------------------------------------------------------"

for i in {21..28}; do
    IP="192.168.1.$i"
    echo "Checking $IP..."
    
    # Check Rotational (0 = SSD, 1 = HDD)
    ROTATIONAL=$(ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null rwagner@$IP "cat /sys/block/sda/queue/rotational" 2>/dev/null)
    
    # Check Discard support (lsblk -D)
    DISC_MAX=$(ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null rwagner@$IP "lsblk -D -n -o DISC-MAX sda" 2>/dev/null)
    
    if [ "$ROTATIONAL" == "0" ]; then
        ROT_STATUS="✅ SSD (Non-rotational)"
    else
        ROT_STATUS="⚠️  HDD (Rotational)"
    fi
    
    if [ "$DISC_MAX" != "0B" ] && [ -n "$DISC_MAX" ]; then
        TRIM_STATUS="✅ TRIM Supported ($DISC_MAX)"
    else
        TRIM_STATUS="❌ TRIM NOT Supported"
    fi
    
    echo "  Rotational: $ROT_STATUS"
    echo "  Trim:       $TRIM_STATUS"
    echo "--------------------------------------------------------"
done

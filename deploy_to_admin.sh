#!/bin/bash
# Syncs the current directory to the Admin VM
# Excludes venv, git, logs, and temporary files

ADMIN_HOST="192.168.1.20"
ADMIN_USER="rwagner"
REMOTE_DIR="/home/rwagner/proxmox-vm-creator"

echo "🚀 Deploying to Admin VM ($ADMIN_HOST)..."

rsync -avz --delete \
    --exclude 'venv' \
    --exclude '.git' \
    --exclude '.env' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude 'logs/*' \
    --exclude 'temp_sync' \
    --exclude 'deploy_to_admin.sh' \
    ./ \
    $ADMIN_USER@$ADMIN_HOST:$REMOTE_DIR/

echo "✅ Deployment complete."

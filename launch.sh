#!/bin/bash
# Launcher for Proxmox VM Creator
# Placed in user root for easy access

PROJECT_DIR="$HOME/proxmox-vm-creator"

# Check if project exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Error: Project directory $PROJECT_DIR not found."
    exit 1
fi

cd "$PROJECT_DIR"

# Check/Create Venv
if [ ! -d "venv" ]; then
    echo "⚙️  Initializing Python Virtual Environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run Main Menu (pass all arguments)
exec ./venv/bin/python main.py "$@"

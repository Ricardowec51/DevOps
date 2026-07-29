#!/bin/bash
# Script de preparación para Admin VM (Ubuntu)

echo "🚀 Configurando entorno Proxmox VM Creator..."

# 1. System Updates
echo "📦 Actualizando paquetes del sistema..."
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git


# 2.5 Install K3s Tools (k3sup, kubectl)
echo "☸️  Instalando k3sup y kubectl..."
if ! command -v k3sup &> /dev/null; then
    curl -sLS https://get.k3sup.dev | sh
    sudo install k3sup /usr/local/bin/
    rm k3sup
fi

if ! command -v kubectl &> /dev/null; then
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    sudo install -v -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    rm kubectl
fi

# 3. Setup Venv
echo "🐍 Configurando entorno virtual Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 3. Activate & Install
echo "📥 Instalando dependencias..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Permissions
echo "🔑 Ajustando permisos..."
chmod +x main.py
chmod +x *.sh
chmod +x *.py

echo "✅ Configuración completada!"
echo "👉 Para iniciar, ejecuta: ./main.py"

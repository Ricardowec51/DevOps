#!/bin/bash
# K3s HA Installer - Simple & Direct Version
# Executed from Admin node (192.168.1.20)

set -e

# --- Configuration ---
USER="rwagner"
MASTER1_IP="192.168.1.21"
MASTERS=("192.168.1.22" "192.168.1.23")
WORKERS=("192.168.1.24" "192.168.1.25" "192.168.1.26" "192.168.1.27" "192.168.1.28")

VIP="192.168.1.50"
K3S_VERSION="v1.30.13+k3s1"
INTERFACE="eth0" 

# --- Connectivity Check ---
ALL_NODES=("192.168.1.21" "${MASTERS[@]}" "${WORKERS[@]}")
echo "🔍 Checking connectivity to all nodes..."
for ip in "${ALL_NODES[@]}"; do
    if ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$USER@$ip" "echo 2>&1" >/dev/null; then
        echo "   ✅ $ip: OK"
    else
        echo "   ❌ $ip: UNREACHABLE! Aborting."
        exit 1
    fi
done

# --- Install k3sup if missing ---
if ! command -v k3sup &> /dev/null; then
    echo "⬇️  Installing k3sup..."
    curl -sLS https://get.k3sup.dev | sh
    sudo install k3sup /usr/local/bin/
    rm k3sup
fi

echo "🚀 Starting K3s HA Installation..."

# --- 1. Bootstrap Master 1 ---
echo "1️⃣  Installing Master 1 ($MASTER1_IP)..."
k3sup install \
  --ip $MASTER1_IP \
  --user $USER \
  --tls-san $VIP \
  --cluster \
  --k3s-version $K3S_VERSION \
  --k3s-extra-args "--disable traefik --disable servicelb --flannel-iface=$INTERFACE --node-ip=$MASTER1_IP --node-taint node-role.kubernetes.io/master=true:NoSchedule" \
  --merge \
  --local-path ~/.kube/config \
  --context k3s-ha

echo "✅ Master 1 installed."

# --- 2. Install Kube-VIP on Master 1 ---
echo "2️⃣  Deploying Kube-VIP on Master 1..."
# Fetch RBAC manifest
curl -s https://kube-vip.io/manifests/rbac.yaml > kube-vip-rbac.yaml
export KUBECONFIG=~/.kube/config
kubectl apply -f kube-vip-rbac.yaml

# Generate Kube-VIP DaemonSet
ssh -o StrictHostKeyChecking=no $USER@$MASTER1_IP "sudo k3s ctr image pull ghcr.io/kube-vip/kube-vip:v0.8.6; \
sudo k3s run --rm --net-host ghcr.io/kube-vip/kube-vip:v0.8.6 vip /kube-vip manifest daemonset \
    --interface $INTERFACE \
    --address $VIP \
    --inCluster \
    --taint \
    --controlplane \
    --services \
    --arp \
    --leaderElection" > kube-vip.yaml

kubectl apply -f kube-vip.yaml
echo "✅ Kube-VIP deployed."

# --- 3. Join Other Masters ---
for ip in "${MASTERS[@]}"; do
    echo "3️⃣  Joining Master $ip..."
    k3sup join \
      --ip $ip \
      --user $USER \
      --server-user $USER \
      --server-ip $MASTER1_IP \
      --server \
      --k3s-version $K3S_VERSION \
      --k3s-extra-args "--disable traefik --disable servicelb --flannel-iface=$INTERFACE --node-ip=$ip --node-taint node-role.kubernetes.io/master=true:NoSchedule"
done

# --- 4. Join Workers ---
for ip in "${WORKERS[@]}"; do
    echo "4️⃣  Joining Worker $ip..."
    k3sup join \
      --ip $ip \
      --user $USER \
      --server-user $USER \
      --server-ip $MASTER1_IP \
      --k3s-version $K3S_VERSION \
      --k3s-extra-args "--flannel-iface=$INTERFACE --node-ip=$ip"
done

echo "🎉 Cluster Installation Complete!"
kubectl get nodes -o wide

#!/bin/bash
# Apagado ordenado del cluster k3s + admin
# Orden: workers → masters → admin

PVE_HOST="https://192.168.1.88:8006"
PVE_USER="root@pam"
PVE_PASS="Gnehid.30"

# Login
RESP=$(curl -sk -d "username=$PVE_USER&password=$PVE_PASS" $PVE_HOST/api2/json/access/ticket)
TICKET=$(echo $RESP | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['ticket'])")
CSRF=$(echo $RESP  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['CSRFPreventionToken'])")

shutdown_vm() {
    local node=$1 vmid=$2 name=$3
    status=$(curl -sk -b "PVEAuthCookie=$TICKET" \
        $PVE_HOST/api2/json/nodes/$node/qemu/$vmid/status/current \
        | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['status'])")

    if [ "$status" = "running" ]; then
        echo "  Apagando [$vmid] $name ($node)..."
        curl -sk -b "PVEAuthCookie=$TICKET" -H "CSRFPreventionToken: $CSRF" \
            -X POST $PVE_HOST/api2/json/nodes/$node/qemu/$vmid/status/shutdown > /dev/null
    else
        echo "  [$vmid] $name ya está detenida"
    fi
}

echo ""
echo "=== Apagado del cluster k3s ==="
echo ""

echo "[1/3] Workers..."
shutdown_vm DELL   3005 k3s-worker-02
shutdown_vm Nnuc13 3007 k3s-worker-04
shutdown_vm msn2   3008 k3s-worker-05
shutdown_vm nuc10  3004 k3s-worker-01
shutdown_vm nuc10  3006 k3s-worker-03

echo "      Esperando 20s..."
sleep 20

echo "[2/3] Masters..."
shutdown_vm DELL   3001 k3s-master-01
shutdown_vm Nnuc13 3003 k3s-master-03
shutdown_vm nuc10  3002 k3s-master-02

echo "      Esperando 15s..."
sleep 15

echo "[3/3] Admin..."
shutdown_vm DELL 1102 k3s-admin

echo ""
echo "Cluster apagado."

import os
from dotenv import load_dotenv
from proxmoxer import ProxmoxAPI
import urllib3
import json

# Deshabilitar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def explore_cluster():
    load_dotenv()
    
    host = os.getenv("PROXMOX_HOST", "192.168.1.143")
    user = os.getenv("PROXMOX_USER", "root@pam")
    password = os.getenv("PROXMOX_PASSWORD")
    verify_ssl = os.getenv("PROXMOX_VERIFY_SSL", "false").lower() == "true"

    print(f"🔌 Conectando a Proxmox en {host}...")
    
    try:
        api = ProxmoxAPI(
            host,
            user=user,
            password=password,
            verify_ssl=verify_ssl
        )
        
        print(f"✅ Conectado exitosamente como {user}\n")
        
        # 1. Información del Cluster
        print("--- [ Configuración del Cluster ] ---")
        try:
            cluster_status = api.cluster.status.get()
            for item in cluster_status:
                if item.get('type') == 'cluster':
                    print(f"Nombre del Cluster: {item.get('name')}")
                    print(f"Nodos totales: {item.get('nodes')}")
                    print(f"Quorum: {'Sí' if item.get('quorate') else 'No'}")
        except Exception as e:
            print(f"⚠️ No se pudo obtener el estado del cluster (posible single node): {e}")

        # 2. Resumen de Nodos
        print("\n--- [ Nodos ] ---")
        nodes = api.nodes.get()
        for node in nodes:
            status = "🟢" if node.get('status') == 'online' else "🔴"
            cpu = node.get('cpu', 0) * 100
            mem_pct = (node.get('memory', 0) / node.get('maxmem', 1)) * 100
            print(f"{status} {node.get('node')} | CPU: {cpu:.1f}% | RAM: {mem_pct:.1f}% | Uptime: {node.get('uptime', 0)}s")

        # 3. Almacenamiento
        print("\n--- [ Storage ] ---")
        storage = api.storage.get()
        for s in storage:
            if s.get('active'):
                used_pct = (s.get('used', 0) / s.get('total', 1)) * 100
                print(f"💾 {s.get('storage')} ({s.get('type')}) | Uso: {used_pct:.1f}% | Contenido: {s.get('content')}")

        # 4. Recursos del Cluster (VMs/CTs)
        print("\n--- [ Recursos (Top 5 VMs running) ] ---")
        resources = api.cluster.resources.get(type='vm')
        running_vms = [r for r in resources if r.get('status') == 'running']
        for vm in running_vms[:5]:
            print(f"🖥️  ID: {vm.get('vmid')} | Nombre: {vm.get('name')} | Nodo: {vm.get('node')}")

    except Exception as e:
        print(f"❌ Error crítico de conexión: {e}")

if __name__ == "__main__":
    explore_cluster()

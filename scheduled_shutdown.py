import os
import time
import sys
from dotenv import load_dotenv
from proxmoxer import ProxmoxAPI
import urllib3

# Deshabilitar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def graceful_node_shutdown(node_name, delay_minutes):
    load_dotenv()
    
    host = os.getenv("PROXMOX_HOST", "192.168.1.143")
    user = os.getenv("PROXMOX_USER", "root@pam")
    password = os.getenv("PROXMOX_PASSWORD")
    verify_ssl = os.getenv("PROXMOX_VERIFY_SSL", "false").lower() == "true"

    try:
        api = ProxmoxAPI(host, user=user, password=password, verify_ssl=verify_ssl)
        
        print(f"🕒 Programando apagado de {node_name} en {delay_minutes} minutos...")
        time.sleep(delay_minutes * 60)
        
        print(f"🚀 Iniciando proceso de apagado coordinado para el nodo: {node_name}")
        
        # 1. Identificar VMs corriendo en el nodo
        resources = api.cluster.resources.get(type='vm')
        vms_to_stop = [vm for vm in resources if vm.get('node') == node_name and vm.get('status') == 'running']
        
        if vms_to_stop:
            print(f"📦 Apagando {len(vms_to_stop)} VMs corriendo en {node_name}...")
            for vm in vms_to_stop:
                vmid = vm.get('vmid')
                print(f"  - Enviando shutdown a VM {vmid} ({vm.get('name')})")
                try:
                    api.nodes(node_name).qemu(vmid).status.shutdown.post()
                except Exception as e:
                    print(f"  ⚠️ Error apagando VM {vmid}: {e}")
            
            # Esperar a que las VMs se apaguen (máximo 5 minutos)
            print("⏳ Esperando a que las VMs finalicen (timeout 5m)...")
            start_wait = time.time()
            while time.time() - start_wait < 300:
                running = [vm for vm in api.cluster.resources.get(type='vm') 
                          if vm.get('node') == node_name and vm.get('status') == 'running']
                if not running:
                    print("✅ Todas las VMs se han apagado.")
                    break
                time.sleep(10)
        else:
            print(f"ℹ️ No hay VMs corriendo en {node_name}.")

        # 2. Apagar el Nodo
        print(f"🔌 Apagando el nodo {node_name}...")
        api.nodes(node_name).status.post(command='shutdown')
        print(f"✅ Comando de shutdown enviado a {node_name}.")

    except Exception as e:
        print(f"❌ Error durante el apagado de {node_name}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 scheduled_shutdown.py <nodo> <minutos>")
        sys.exit(1)
    
    target_node = sys.argv[1]
    wait_time = int(sys.argv[2])
    graceful_node_shutdown(target_node, wait_time)

import os
import paramiko
from dotenv import load_dotenv
from proxmoxer import ProxmoxAPI
import requests

load_dotenv()
requests.packages.urllib3.disable_warnings()

def distribute():
    host = os.getenv('PROXMOX_HOST')
    password = os.getenv('PROXMOX_PASSWORD')

    if not host or not password:
        print("❌ Missing PROXMOX_HOST or PROXMOX_PASSWORD in .env")
        return

    ssh_user = "root"

    print(f"🚀 Iniciando distribución de snippets a todos los nodos...")

    local_file = 'user-data.yaml'
    remote_snippets_dir = '/var/lib/vz/snippets'
    primary_remote_path = f"{remote_snippets_dir}/user-data.yaml"

    try:
        # Conectar a Proxmox API para obtener lista de nodos
        proxmox = ProxmoxAPI(
            host,
            user=os.getenv('PROXMOX_USER'),
            password=password,
            verify_ssl=False
        )

        # Obtener IPs de los nodos desde cluster status
        cluster_status = proxmox.cluster.status.get()
        node_ips = {}
        for item in cluster_status:
            if item.get('type') == 'node' and item.get('ip'):
                node_ips[item['name']] = item['ip']

        nodes = proxmox.nodes.get()
        online_nodes = [n for n in nodes if n['status'] == 'online']

        print(f"📋 Nodos online: {[(n['node'], node_ips.get(n['node'], 'N/A')) for n in online_nodes]}")

        # Distribuir a cada nodo directamente via SSH/SFTP
        for node in online_nodes:
            node_name = node['node']
            node_ip = node_ips.get(node_name)

            if not node_ip:
                print(f"  ⚠️  No se encontró IP para {node_name}, saltando...")
                continue

            print(f"  📤 Subiendo a {node_name} ({node_ip})...")

            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(node_ip, username=ssh_user, password=password)

                # Crear directorio si no existe
                ssh.exec_command(f"mkdir -p {remote_snippets_dir}")

                # Subir archivo
                sftp = ssh.open_sftp()
                sftp.put(local_file, primary_remote_path)
                sftp.close()
                ssh.close()

                print(f"     ✅ Subido exitosamente a {node_name}")
            except Exception as e:
                print(f"     ❌ Falló subida a {node_name}: {e}")

        print("\n🎉 Distribución de snippets finalizada.")

    except Exception as e:
        print(f"❌ Error crítico en distribución: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    distribute()

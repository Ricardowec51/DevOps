import os
from dotenv import load_dotenv
from proxmoxer import ProxmoxAPI
import urllib3
import json

# Deshabilitar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def list_all_ips():
    load_dotenv()
    
    host = os.getenv("PROXMOX_HOST", "192.168.1.143")
    user = os.getenv("PROXMOX_USER", "root@pam")
    password = os.getenv("PROXMOX_PASSWORD")
    verify_ssl = os.getenv("PROXMOX_VERIFY_SSL", "false").lower() == "true"

    try:
        api = ProxmoxAPI(host, user=user, password=password, verify_ssl=verify_ssl)
        resources = api.cluster.resources.get(type='vm')
        
        print(f"{'VMID':<8} | {'Nombre':<20} | {'Nodo':<10} | {'Status':<10} | {'IP Address'}")
        print("-" * 75)
        
        for vm in resources:
            vmid = vm.get('vmid')
            node = vm.get('node')
            name = vm.get('name')
            status = vm.get('status')
            
            ip = "Unknown / No Agent"
            
            if status == 'running':
                try:
                    # Intentar obtener IP via Guest Agent
                    interfaces = api.nodes(node).qemu(vmid).agent('network-get-interfaces').get()
                    ip_list = []
                    for iface in interfaces.get('result', []):
                        for addr in iface.get('ip-addresses', []):
                            if addr.get('ip-address-type') == 'ipv4' and addr.get('ip-address') != '127.0.0.1':
                                ip_list.append(addr.get('ip-address'))
                    if ip_list:
                        ip = ", ".join(ip_list)
                except:
                    pass
            
            print(f"{str(vmid):<8} | {str(name):<20} | {str(node):<10} | {str(status):<10} | {ip}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_all_ips()


from lib.core.config import Config
from lib.core.proxmox import ProxmoxClient
from rich.pretty import pprint

def check_ips():
    cfg = Config()
    client = ProxmoxClient(cfg)
    if client.connect():
        print("--- Cluster Status ---")
        try:
            status = client.api.cluster.status.get()
            pprint(status)
        except Exception as e:
            print(f"Error getting cluster status: {e}")

        print("\n--- Node Interfaces (Sample) ---")
        try:
            nodes = [n['node'] for n in client.api.nodes.get()]
            for node in nodes:
                print(f"Node: {node}")
                start_nets = client.api.nodes(node).network.get()
                # Filter for useful info
                for iface in start_nets:
                    if iface['type'] == 'bridge' and 'vmbr0' in iface['iface']:
                         # Likely the management IP is on vmbr0 or associated
                         pass
                
                # Proxmox sometimes puts the IP in the output of network.get()
                pprint(start_nets)
                break # Just check one for now to save output size
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_ips()

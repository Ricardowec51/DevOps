
from lib.core.config import Config
from lib.core.proxmox import ProxmoxClient
from rich.pretty import pprint

def check_nodes():
    cfg = Config()
    client = ProxmoxClient(cfg)
    if client.connect():
        nodes = client.api.nodes.get()
        pprint(nodes)

if __name__ == "__main__":
    check_nodes()

import os
import requests
from lib.core.config import Config
from lib.core.proxmox import ProxmoxClient
from lib.core.logger import log

def upload_snippets_via_api():
    cfg = Config()
    client = ProxmoxClient(cfg)
    
    if not client.connect():
        return

    # Snippet info
    local_file = 'user-data.yaml'
    storage = 'local' 
    content_type = 'snippets'
    filename = 'user-data.yaml'

    try:
        with open(local_file, 'rb') as f:
            file_content = f.read()

        nodes = client.api.nodes.get()
        
        log.info(f"🚀 Iniciando carga de snippets via API a storage '{storage}'...")

        for node in nodes:
            node_name = node['node']
            if node['status'] != 'online':
                log.warning(f"  ⚠️  Nodo {node_name} offline, saltando.")
                continue

            log.info(f"  📤 Subiendo a {node_name}...")
            
            try:
                # API Endpoint: POST /nodes/{node}/storage/{storage}/upload
                # params: content (type), filename, file
                # Note: proxmoxer handles multipart upload if 'file' kwarg is passed
                
                # Check if storage exists/is active on node
                try:
                    client.api.nodes(node_name).storage(storage).status.get()
                except Exception:
                     log.warning(f"     ⚠️  Storage '{storage}' no disponible en {node_name}")
                     continue

                client.api.nodes(node_name).storage(storage).upload.post(
                    content=content_type,
                    filename=filename,
                    file=file_content 
                )
                log.info(f"     ✅ Carga exitosa en {node_name}")
                
            except Exception as e:
                log.error(f"     ❌ Falló carga en {node_name}: {e}")

    except FileNotFoundError:
        log.error(f"❌ Archivo local {local_file} no encontrado.")
    except Exception as e:
         log.error(f"❌ Error general: {e}")

if __name__ == "__main__":
    upload_snippets_via_api()

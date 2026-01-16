#!/usr/bin/env python3
"""
Script para verificar contenido del storage NFS_SERVER
"""

import yaml
import os
from proxmoxer import ProxmoxAPI
import requests
from dotenv import load_dotenv

load_dotenv()
requests.packages.urllib3.disable_warnings()

# Leer config
with open('config.yaml') as f:
    config = yaml.safe_load(f)

px = config.get('proxmox', {})
px_host = os.getenv('PROXMOX_HOST', px.get('host'))
px_user = os.getenv('PROXMOX_USER', px.get('user'))
px_password = os.getenv('PROXMOX_PASSWORD', px.get('password'))
px_verify_ssl = os.getenv('PROXMOX_VERIFY_SSL', str(px.get('verify_ssl', False))).lower() == 'true'

proxmox = ProxmoxAPI(
    px_host,
    user=px_user,
    password=px_password,
    verify_ssl=px_verify_ssl
)

print("\n📦 Información del storage NFS_SERVER:")
print("="*80)

# Buscar NFS_SERVER en cualquier nodo
nodes = ['BOSC', 'DELL', 'Nnuc13', 'nuc10', 'msa', 'msn2']

for node in nodes:
    try:
        storages = proxmox.nodes(node).storage.get()
        for storage in storages:
            if storage['storage'] == 'NFS_SERVER':
                print(f"\n🖥️  Nodo: {node}")
                print(f"   Storage: {storage['storage']}")
                print(f"   Type: {storage.get('type', 'N/A')}")
                print(f"   Active: {storage.get('active', 0)}")
                print(f"   Enabled: {storage.get('enabled', 0)}")

                # Obtener info detallada
                storage_info = proxmox.nodes(node).storage('NFS_SERVER').status.get()
                print(f"   Available: {storage_info.get('avail', 0) / (1024**3):.2f} GB")
                print(f"   Used: {storage_info.get('used', 0) / (1024**3):.2f} GB")
                print(f"   Total: {storage_info.get('total', 0) / (1024**3):.2f} GB")

                # Tipos de contenido soportados
                storage_config = proxmox.storage('NFS_SERVER').get()
                print(f"   Content types: {storage_config.get('content', 'N/A')}")

                # Listar contenido
                print(f"\n   📁 Contenido en NFS_SERVER:")
                try:
                    # Intentar listar ISOs
                    content = proxmox.nodes(node).storage('NFS_SERVER').content.get(content='iso')
                    if content:
                        for item in content:
                            volid = item.get('volid', '')
                            size_mb = item.get('size', 0) / (1024*1024)
                            print(f"      [ISO] {volid} ({size_mb:.1f} MB)")
                    else:
                        print(f"      (Sin ISOs)")
                except Exception as e:
                    print(f"      ISOs: {e}")

                try:
                    # Intentar listar imágenes
                    content = proxmox.nodes(node).storage('NFS_SERVER').content.get(content='images')
                    if content:
                        for item in content:
                            volid = item.get('volid', '')
                            size_gb = item.get('size', 0) / (1024**3)
                            print(f"      [IMG] {volid} ({size_gb:.2f} GB)")
                except Exception as e:
                    print(f"      Images: {e}")

                break
    except Exception as e:
        pass

print("\n" + "="*80 + "\n")

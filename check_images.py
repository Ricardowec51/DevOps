#!/usr/bin/env python3
"""
Script para verificar que las cloud images existen en Proxmox
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

print("\n📁 Verificando cloud images en Proxmox:")
print("="*80)

# Imágenes configuradas
images = config['defaults']['images']

# Verificar en cada nodo
nodes = ['Nnuc13', 'DELL', 'BOSC', 'msa', 'msn2', 'nuc10']

for image_name, image_path in images.items():
    print(f"\n🔍 Imagen: {image_name}")
    print(f"   Ruta configurada: {image_path}")

    found = False
    for node in nodes:
        try:
            # Listar archivos en el storage 'local' del nodo
            storages = proxmox.nodes(node).storage.get()
            for storage in storages:
                if storage['storage'] in ['local', 'local:iso']:
                    try:
                        # Listar contenido del storage
                        content = proxmox.nodes(node).storage(storage['storage']).content.get()
                        for item in content:
                            if image_path in item.get('volid', ''):
                                print(f"   ✅ Encontrada en {node} - Storage: {storage['storage']}")
                                print(f"      volid: {item.get('volid')}")
                                found = True
                                break
                    except:
                        pass
        except Exception as e:
            pass

    if not found:
        print(f"   ❌ NO encontrada en ningún nodo")

print("\n" + "="*80)

# Listar todos los ISOs/images disponibles
print("\n📦 Cloud images disponibles en el cluster:")
print("="*80)

for node in nodes:
    try:
        print(f"\n🖥️  Nodo: {node}")
        storages = proxmox.nodes(node).storage.get()
        for storage in storages:
            if storage['storage'] == 'local':
                try:
                    content = proxmox.nodes(node).storage('local').content.get(content='iso')
                    for item in content:
                        volid = item.get('volid', '')
                        if 'cloud' in volid.lower() or '.img' in volid or '.qcow2' in volid:
                            size_mb = item.get('size', 0) / (1024*1024)
                            print(f"   📀 {volid} ({size_mb:.1f} MB)")
                except:
                    pass
    except Exception as e:
        print(f"   Error: {e}")

print("="*80 + "\n")

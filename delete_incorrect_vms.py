#!/usr/bin/env python3
"""
Script para eliminar VMs creadas incorrectamente en nodo DELL
"""
import time
from lib.core.config import Config
from lib.core.proxmox import ProxmoxClient
from lib.core.logger import log

# VMs a eliminar - todas en nodo DELL (donde fueron creadas incorrectamente)
VMS_TO_DELETE = [
    {'vmid': 3001, 'node': 'DELL'},
    {'vmid': 3003, 'node': 'DELL'},
    {'vmid': 3005, 'node': 'DELL'},
]

def delete_vms():
    cfg = Config()
    client = ProxmoxClient(cfg)

    if not client.connect():
        log.error("No se pudo conectar a Proxmox")
        return

    log.info(f"🗑️  Eliminando {len(VMS_TO_DELETE)} VMs incorrectamente creadas en DELL...")

    for vm in VMS_TO_DELETE:
        vmid = vm['vmid']
        node = vm['node']

        log.info(f"  👉 Eliminando VM {vmid} de {node}...")

        try:
            # Detener si está corriendo
            try:
                status = client.api.nodes(node).qemu(vmid).status.current.get()
                if status.get('status') == 'running':
                    log.info(f"     🛑 Deteniendo VM {vmid}...")
                    client.api.nodes(node).qemu(vmid).status.stop.post()
                    time.sleep(5)
            except Exception as e:
                log.debug(f"     Status check: {e}")

            # Eliminar
            task = client.api.nodes(node).qemu(vmid).delete()
            log.info(f"     ✅ Orden de borrado enviada (Task: {task})")
            time.sleep(2)

        except Exception as e:
            if "does not exist" in str(e).lower():
                log.warning(f"     ⚠️  VM {vmid} no existe en {node}")
            else:
                log.error(f"     ❌ Error eliminando {vmid}: {e}")

    log.info("🏁 Proceso de eliminación completado")

if __name__ == "__main__":
    delete_vms()

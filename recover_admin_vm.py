
import time
from lib.core.config import Config
from lib.core.proxmox import ProxmoxClient
from lib.core.logger import log

def recover():
    cfg = Config()
    client = ProxmoxClient(cfg)
    if not client.connect():
        return

    node = "BOSC"
    vmid = 1102

    log.info(f"🔄 Restarting Admin VM {vmid} on {node}...")

    try:
        # Try Shutdown first
        log.info("   Sending shutdown command...")
        client.get_vm(node, vmid).status.shutdown.post()
        
        # Wait for stop
        for i in range(30):
            status = client.get_vm(node, vmid).status.current.get()['status']
            if status == 'stopped':
                break
            time.sleep(2)
        
        # Force stop if needed
        status = client.get_vm(node, vmid).status.current.get()['status']
        if status != 'stopped':
             log.warning("   Shutdown timed out. Forcing stop...")
             client.get_vm(node, vmid).status.stop.post()
             time.sleep(5)

        # Start
        log.info("   Starting VM...")
        client.get_vm(node, vmid).status.start.post()
        
        log.info("✅ VM Restart command sent. Waiting for boot...")
        
    except Exception as e:
        log.error(f"❌ Error: {e}")

if __name__ == "__main__":
    recover()

#!/usr/bin/env python3
"""
Test SSH connectivity to all VMs from Admin
"""
import subprocess
import sys
from lib.core.config import Config
from lib.core.logger import log

def ping_host(ip, timeout=3):
    """Ping a host with timeout"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', str(timeout), ip],
            capture_output=True,
            timeout=timeout + 1
        )
        return result.returncode == 0
    except:
        return False

def test_ssh_host(ip, user='rwagner', timeout=10):
    """Test SSH connection and logout properly"""
    try:
        result = subprocess.run(
            [
                'ssh',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'BatchMode=yes',
                '-o', f'ConnectTimeout={timeout}',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'LogLevel=ERROR',
                f'{user}@{ip}',
                'hostname; exit 0'  # exit explicitly
            ],
            capture_output=True,
            text=True,
            timeout=timeout + 2
        )

        if result.returncode == 0:
            return True, result.stdout.strip().split('\n')[0]
        else:
            return False, result.stderr.strip()[:50] if result.stderr else "Connection failed"
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)[:50]

def test_ssh():
    """Prueba conectividad SSH a todas las VMs configuradas"""
    cfg = Config()

    log.info("\n🔐 Probando conectividad a VMs:")
    log.info("=" * 70)

    success = 0
    failed = 0

    for vm in cfg.vms:
        vmid = vm['vmid']
        name = vm['name']
        ip = vm.get('ip', 'N/A')

        if ip == 'N/A':
            log.warning(f"⚠️  VM {vmid} ({name}): Sin IP configurada")
            failed += 1
            continue

        # Step 1: Ping (3 sec max)
        if not ping_host(ip, timeout=3):
            log.warning(f"❌ VM {vmid} ({name}) @ {ip}: No responde ping")
            failed += 1
            continue

        # Step 2: SSH (10 sec max)
        ok, result = test_ssh_host(ip, timeout=10)

        if ok:
            log.info(f"✅ VM {vmid} ({name}) @ {ip}: {result}")
            success += 1
        else:
            log.warning(f"❌ VM {vmid} ({name}) @ {ip}: {result}")
            failed += 1

    log.info("=" * 70)
    log.info(f"\n📊 Resultado: ✅ {success} | ❌ {failed}")

    return failed == 0

def wait_for_ssh(max_wait=120, interval=10):
    """Espera hasta que todas las VMs respondan por SSH"""
    import time

    cfg = Config()
    total_vms = len(cfg.vms)

    log.info(f"\n⏳ Esperando SSH en {total_vms} VMs (máx {max_wait}s)...")

    start_time = time.time()

    while time.time() - start_time < max_wait:
        ready = 0

        for vm in cfg.vms:
            ip = vm.get('ip')
            if not ip:
                continue

            # Quick ping first (3 sec)
            if not ping_host(ip, timeout=3):
                continue

            # Then SSH (10 sec)
            ok, _ = test_ssh_host(ip, timeout=10)
            if ok:
                ready += 1

        elapsed = int(time.time() - start_time)
        log.info(f"  [{elapsed}s] {ready}/{total_vms} VMs listas...")

        if ready == total_vms:
            log.info(f"\n✅ Todas las VMs listas en {elapsed}s")
            return True

        time.sleep(interval)

    log.warning(f"\n⚠️  Timeout: Solo {ready}/{total_vms} VMs respondieron")
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--wait':
        wait_for_ssh()
    else:
        test_ssh()

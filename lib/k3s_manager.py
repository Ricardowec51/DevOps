import os
import subprocess
import time
from lib.logger import log
from lib.config import Config
from rich.console import Console

console = Console()


class K3sManager:
    def __init__(self):
        self.cfg = Config()
        self.k3s_cfg = self.cfg.data.get('k3s', {})
        self.vip = self.k3s_cfg.get('vip', '192.168.1.50')
        self.user = self.k3s_cfg.get('user', 'rwagner')
        self.version = self.k3s_cfg.get('version', 'v1.30.13+k3s1')
        self.interface = self.k3s_cfg.get('interface', 'eth0')
        self.master_taint = self.k3s_cfg.get('master_taint', 'node-role.kubernetes.io/master=true:NoSchedule')
        self.kubeconfig_path = os.path.expanduser('~/.kube/config')
        self.ssh_key = self.k3s_cfg.get('ssh_key', '~/.ssh/id_rsa')

        # Filter nodes
        self.masters = [vm for vm in self.cfg.vms if 'master' in vm.get('tags', '') or 'master' in vm.get('name', '')]
        self.workers = [vm for vm in self.cfg.vms if 'worker' in vm.get('tags', '') or 'worker' in vm.get('name', '')]

    def _run_cmd(self, cmd, with_kubeconfig=False):
        """Ejecuta un comando. Si with_kubeconfig=True, exporta KUBECONFIG primero."""
        if with_kubeconfig:
            cmd = f"KUBECONFIG={self.kubeconfig_path} {cmd}"
        log.info(f"   ⚙️  Exec: {cmd}")
        try:
            subprocess.run(cmd, shell=True, check=True, env={**os.environ, 'KUBECONFIG': self.kubeconfig_path})
            return True
        except subprocess.CalledProcessError as e:
            log.error(f"   ❌ Error executing command: {e}")
            return False

    def _setup_kubeconfig(self, master_ip):
        """Obtiene el kubeconfig del master y lo configura localmente."""
        log.info("   📋 Configurando kubeconfig...")

        # Crear directorio ~/.kube si no existe
        kube_dir = os.path.expanduser('~/.kube')
        os.makedirs(kube_dir, exist_ok=True)

        # Obtener kubeconfig del master
        cmd = f"ssh -o StrictHostKeyChecking=no {self.user}@{master_ip} 'sudo cat /etc/rancher/k3s/k3s.yaml'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            log.error(f"   ❌ Error obteniendo kubeconfig: {result.stderr}")
            return False

        # Reemplazar 127.0.0.1 por la IP del master
        kubeconfig_content = result.stdout.replace('127.0.0.1', master_ip)

        # Guardar kubeconfig
        with open(self.kubeconfig_path, 'w') as f:
            f.write(kubeconfig_content)

        os.chmod(self.kubeconfig_path, 0o600)

        # Exportar KUBECONFIG en el entorno actual
        os.environ['KUBECONFIG'] = self.kubeconfig_path

        log.info(f"   ✅ Kubeconfig guardado en {self.kubeconfig_path}")
        return True

    def deploy(self):
        console.clear()
        console.print(r"""
 [yellow blink]    ____  _____ ____    _    ____  ____   ___     [/yellow blink]
 [yellow blink]   |  _ \|_   _/ ___|  / \  |  _ \|  _ \ / _ \    [/yellow blink]
 [yellow blink]   | |_) | | || |     / _ \ | |_) | | | | | | |   [/yellow blink]
 [yellow blink]   |  _ <  | || |___ / ___ \|  _ <| |_| | |_| |   [/yellow blink]
 [yellow blink]   |_| \_\ |_| \____/_/   \_\_| \_\____/ \___/    [/yellow blink]

 [cyan blink]   ____  _______     __  _____ _____ ____ _____  [/cyan blink]
 [cyan blink]  |  _ \| ____\ \   / / |_   _| ____/ ___|_   _| [/cyan blink]
 [cyan blink]  | | | |  _|  \ \ / /    | | |  _| \___ \ | |   [/cyan blink]
 [cyan blink]  | |_| | |___  \ V /     | | | |___ ___) || |   [/cyan blink]
 [cyan blink]  |____/|_____|  \_/      |_| |_____|____/ |_|   [/cyan blink]
 [green blink]    Versión Completa con Pruebas y Tracking     [/green blink]
 [green blink]        https://github.com/ricardowec51          [/green blink]
""")
        log.info("🚀 Starting K3s HA Deployment...")
        log.info(f"   Masters: {len(self.masters)}")
        log.info(f"   Workers: {len(self.workers)}")
        
        if not self.masters:
            log.error("❌ No masters found in configuration.")
            return

        first_master = self.masters[0]
        other_masters = self.masters[1:]

        # 1. Bootstrap First Master
        log.info(f"1️⃣  Bootstrapping First Master: {first_master['name']} ({first_master['ip']})")

        cmd = (
            f"k3sup install "
            f"--ip {first_master['ip']} "
            f"--user {self.user} "
            f"--tls-san {self.vip} "
            f"--cluster "
            f"--k3s-version {self.version} "
            f"--k3s-extra-args '--disable traefik --disable servicelb --flannel-iface={self.interface} --node-ip={first_master['ip']} --node-taint {self.master_taint}' "
            f"--merge "
            f"--sudo "
            f"--local-path {self.kubeconfig_path} "
            f"--context k3s-ha "
            f"--ssh-key {self.ssh_key}"
        )
        if not self._run_cmd(cmd): return

        # 1.5. Setup kubeconfig properly
        log.info("1️⃣.5️⃣  Configurando kubeconfig...")
        time.sleep(10)  # Esperar a que K3s esté listo
        if not self._setup_kubeconfig(first_master['ip']):
            log.error("❌ No se pudo configurar kubeconfig")
            return

        # Verificar conexión al cluster
        log.info("   🔍 Verificando conexión al cluster...")
        if not self._run_cmd("kubectl get nodes"):
            log.error("❌ No se puede conectar al cluster")
            return

        # 2. Deploy Kube-VIP
        log.info("2️⃣  Deploying Kube-VIP...")
        self._deploy_kubevip(first_master['ip'])

        # 3. Deploy MetalLB
        log.info("3️⃣  Deploying MetalLB (LoadBalancer)...")
        self._deploy_metallb(first_master['ip'])

        # 4. Join Other Masters
        for m in other_masters:
            log.info(f"4️⃣  Joining Master: {m['name']} ({m['ip']})")
            cmd = (
                f"k3sup join "
                f"--ip {m['ip']} "
                f"--user {self.user} "
                f"--server-user {self.user} "
                f"--server-ip {first_master['ip']} "
                f"--server "
                f"--sudo "
                f"--k3s-version {self.version} "
                f"--k3s-extra-args '--disable traefik --disable servicelb --flannel-iface={self.interface} --node-ip={m['ip']} --node-taint {self.master_taint}' "
                f"--ssh-key {self.ssh_key}"
            )
            self._run_cmd(cmd)

        # 5. Join Workers
        for w in self.workers:
            log.info(f"5️⃣  Joining Worker: {w['name']} ({w['ip']})")
            cmd = (
                f"k3sup join "
                f"--ip {w['ip']} "
                f"--user {self.user} "
                f"--server-user {self.user} "
                f"--server-ip {first_master['ip']} "
                f"--sudo "
                f"--k3s-version {self.version} "
                f"--k3s-extra-args '--flannel-iface={self.interface} --node-ip={w['ip']}' "
                f"--ssh-key {self.ssh_key}"
            )
            self._run_cmd(cmd)

        log.info("🎉 Cluster Deployment Completed!")
        self._run_cmd("kubectl get nodes -o wide")

    def _deploy_kubevip(self, master_ip):
        # RBAC
        self._run_cmd("curl -s https://kube-vip.io/manifests/rbac.yaml > kube-vip-rbac.yaml")
        self._run_cmd("kubectl apply -f kube-vip-rbac.yaml") # Assumes ~/.kube/config is set by k3sup

        # DaemonSet Generation & Apply
        # Note: This uses SSH to run remote k3s/ctr commands to generate manifest
        log.info("   Generating Kube-VIP manifest...")
        # Download template and replace variables (interface, vip, version)
        url = "https://raw.githubusercontent.com/JamesTurland/JimsGarage/main/Kubernetes/K3S-Deploy/kube-vip"
        cmd = (
            f"curl -s {url} | "
            f"sed 's/$interface/{self.interface}/g' | "
            f"sed 's/$vip/{self.vip}/g' | "
            f"sed 's/v0.8.2/v0.8.6/g' > kube-vip.yaml"
        )
        if self._run_cmd(cmd):
            self._run_cmd("kubectl apply -f kube-vip.yaml")
            log.info("   ✅ Kube-VIP applied.")
        else:
            log.error("   ❌ Failed to generate Kube-VIP manifest")

    def _deploy_metallb(self, master_ip=None):
        # 1. Download and Apply MetalLB Native Manifest
        log.info("   Downloading MetalLB Native Manifest...")
        metallb_url = "https://raw.githubusercontent.com/metallb/metallb/v0.14.9/config/manifests/metallb-native.yaml"
        # Download first, then apply (avoids URL parsing issues)
        if not self._run_cmd(f"curl -sLO {metallb_url}"):
            log.error("   Failed to download MetalLB manifest")
            return False
        if not self._run_cmd("kubectl apply -f metallb-native.yaml"):
            log.error("   Failed to apply MetalLB manifest")
            return False
        
        log.info("   Waiting for MetalLB Controller to be ready...")
        # Simple wait loop handled by kubectl wait usually, but generic sleep is safer for simple scripts
        time.sleep(30) 
        
        # 2. Configure IPAddressPool
        log.info("   Configuring MetalLB IP Address Pool...")
        
        # Define range - defaulting to .240-.250 if not specified in config
        lb_range = self.k3s_cfg.get('lb_range', '192.168.1.240-192.168.1.250')
        
        pool_config = f"""
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: dev-pool
  namespace: metallb-system
spec:
  addresses:
  - {lb_range}
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: dev-l2-advertisement
  namespace: metallb-system
spec:
  ipAddressPools:
  - dev-pool
"""
        # Write config locally then apply
        with open("metallb-config.yaml", "w") as f:
            f.write(pool_config)
            
        self._run_cmd("kubectl apply -f metallb-config.yaml")
        log.info(f"   ✅ MetalLB configured with range: {lb_range}")
        return True

    def install_metallb(self):
        """Instala MetalLB de forma independiente (para cuando falla durante deploy)."""
        log.info("☸️  Installing MetalLB...")

        # Verificar kubeconfig
        if not os.path.exists(self.kubeconfig_path):
            log.error("❌ Kubeconfig not found. Run deployment first or setup kubeconfig manually.")
            return False

        os.environ['KUBECONFIG'] = self.kubeconfig_path

        # Verificar conexión
        if not self._run_cmd("kubectl get nodes"):
            log.error("❌ Cannot connect to cluster")
            return False

        return self._deploy_metallb()

    def deploy_nginx_test(self):
        """Despliega nginx de prueba con LoadBalancer."""
        log.info("🌐 Deploying nginx test application...")

        os.environ['KUBECONFIG'] = self.kubeconfig_path

        # Crear deployment
        if not self._run_cmd("kubectl create deployment nginx-test --image=nginx"):
            log.warning("   Deployment may already exist")

        # Exponer con LoadBalancer
        if not self._run_cmd("kubectl expose deployment nginx-test --port=80 --type=LoadBalancer"):
            log.warning("   Service may already exist")

        # Mostrar IP asignada
        time.sleep(5)
        self._run_cmd("kubectl get svc nginx-test")
        log.info("✅ Nginx test deployed. Check EXTERNAL-IP above.")


    def stop_cluster(self):
        log.info("🛑 Stopping K3s Cluster...")
        
        # Stop Workers First
        for w in self.workers:
            log.info(f"   Stopping K3s Agent on Worker: {w['name']} ({w['ip']})")
            cmd = f"ssh -o StrictHostKeyChecking=no {self.user}@{w['ip']} \"sudo systemctl stop k3s-agent\""
            self._run_cmd(cmd)

        # Stop Masters
        for m in self.masters:
            log.info(f"   Stopping K3s Server on Master: {m['name']} ({m['ip']})")
            cmd = f"ssh -o StrictHostKeyChecking=no {self.user}@{m['ip']} \"sudo systemctl stop k3s\""
            self._run_cmd(cmd)
            
        log.info("✅ Cluster Stopped.")

    def start_cluster(self):
        log.info("🚀 Starting K3s Cluster...")
        
        # Start Masters First
        for m in self.masters:
            log.info(f"   Starting K3s Server on Master: {m['name']} ({m['ip']})")
            cmd = f"ssh -o StrictHostKeyChecking=no {self.user}@{m['ip']} \"sudo systemctl start k3s\""
            self._run_cmd(cmd)

        # Start Workers
        for w in self.workers:
            log.info(f"   Starting K3s Agent on Worker: {w['name']} ({w['ip']})")
            cmd = f"ssh -o StrictHostKeyChecking=no {self.user}@{w['ip']} \"sudo systemctl start k3s-agent\""
            self._run_cmd(cmd)
            
        log.info("✅ Cluster Started.")

    def show_status(self):
        from rich.table import Table
        from rich.console import Console
        console = Console()
        
        table = Table(title="K3s Cluster Status")
        table.add_column("VM Name", style="cyan")
        table.add_column("IP Address", style="magenta")
        table.add_column("Role", style="blue")
        table.add_column("Proxmox Node", style="green")
        table.add_column("Service Status", style="yellow")
        
        nodes = []
        for m in self.masters:
            nodes.append({**m, 'role': 'Master', 'service': 'k3s'})
        for w in self.workers:
            nodes.append({**w, 'role': 'Worker', 'service': 'k3s-agent'})
            
        for node in nodes:
            # Check service status
            try:
                cmd = f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 {self.user}@{node['ip']} \"systemctl is-active {node['service']}\""
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                status = "🟢 Active" if "active" in result.stdout else "🔴 Inactive"
            except:
                status = "❓ Unreachable"
            
            table.add_row(
                node['name'],
                node['ip'],
                node['role'],
                node.get('node', 'Unknown'),
                status
            )
            
        console.print(table)

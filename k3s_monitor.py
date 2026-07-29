#!/usr/bin/env python3
"""
K3s Cluster Monitor - Comprehensive Cluster Status Dashboard
Provides a complete view of the K3s cluster from your Mac Mini
"""

import subprocess
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
import time

console = Console()


def run_kubectl(cmd):
    """Execute kubectl command and return output"""
    try:
        result = subprocess.run(
            f"kubectl {cmd}",
            shell=True,
            capture_output=True,
            text=True,
            env={'KUBECONFIG': '/Users/rwagner/.kube/config'}
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        return None


def get_nodes_status():
    """Get nodes status with detailed information"""
    output = run_kubectl("get nodes -o wide --no-headers")
    if not output:
        return []
    
    nodes = []
    for line in output.split('\n'):
        parts = line.split()
        if len(parts) >= 7:
            nodes.append({
                'name': parts[0],
                'status': parts[1],
                'roles': parts[2],
                'age': parts[3],
                'version': parts[4],
                'ip': parts[5],
                'os': parts[6] if len(parts) > 6 else 'N/A'
            })
    return nodes


def get_nodes_metrics():
    """Get resource usage metrics for nodes"""
    output = run_kubectl("top nodes --no-headers")
    if not output:
        return {}
    
    metrics = {}
    for line in output.split('\n'):
        parts = line.split()
        if len(parts) >= 5:
            metrics[parts[0]] = {
                'cpu': parts[1],
                'cpu_pct': parts[2],
                'memory': parts[3],
                'memory_pct': parts[4]
            }
    return metrics


def get_pods_summary():
    """Get summary of pods by namespace"""
    output = run_kubectl("get pods -A --no-headers")
    if not output:
        return {}
    
    summary = {}
    for line in output.split('\n'):
        parts = line.split()
        if len(parts) >= 4:
            namespace = parts[0]
            status = parts[3]
            
            if namespace not in summary:
                summary[namespace] = {'total': 0, 'running': 0, 'pending': 0, 'failed': 0, 'other': 0}
            
            summary[namespace]['total'] += 1
            if 'Running' in status:
                summary[namespace]['running'] += 1
            elif 'Pending' in status or 'ContainerCreating' in status:
                summary[namespace]['pending'] += 1
            elif 'Error' in status or 'CrashLoopBackOff' in status:
                summary[namespace]['failed'] += 1
            else:
                summary[namespace]['other'] += 1
    
    return summary


def get_services_lb():
    """Get LoadBalancer services"""
    output = run_kubectl("get svc -A --no-headers")
    if not output:
        return []
    
    services = []
    for line in output.split('\n'):
        parts = line.split()
        if len(parts) >= 5 and 'LoadBalancer' in parts[3]:
            services.append({
                'namespace': parts[0],
                'name': parts[1],
                'type': parts[3],
                'cluster_ip': parts[4],
                'external_ip': parts[5] if len(parts) > 5 else '<pending>',
                'ports': parts[6] if len(parts) > 6 else 'N/A'
            })
    return services


def create_nodes_table(nodes, metrics):
    """Create a rich table for nodes"""
    table = Table(title="🖥️  Cluster Nodes", show_header=True, header_style="bold cyan")
    
    table.add_column("Node", style="cyan", width=15)
    table.add_column("Status", justify="center", width=8)
    table.add_column("Role", style="blue", width=20)
    table.add_column("CPU", justify="right", width=10)
    table.add_column("Memory", justify="right", width=12)
    table.add_column("IP", style="magenta", width=15)
    table.add_column("Version", style="green", width=15)
    
    for node in nodes:
        status_icon = "✅" if node['status'] == 'Ready' else "❌"
        status = f"{status_icon} {node['status']}"
        
        node_metrics = metrics.get(node['name'], {})
        cpu = f"{node_metrics.get('cpu', 'N/A')} ({node_metrics.get('cpu_pct', 'N/A')})"
        memory = f"{node_metrics.get('memory', 'N/A')} ({node_metrics.get('memory_pct', 'N/A')})"
        
        table.add_row(
            node['name'],
            status,
            node['roles'],
            cpu,
            memory,
            node['ip'],
            node['version']
        )
    
    return table


def create_pods_table(pods_summary):
    """Create a rich table for pods summary"""
    table = Table(title="📦 Pods by Namespace", show_header=True, header_style="bold yellow")
    
    table.add_column("Namespace", style="cyan", width=20)
    table.add_column("Total", justify="right", width=8)
    table.add_column("Running", justify="right", style="green", width=10)
    table.add_column("Pending", justify="right", style="yellow", width=10)
    table.add_column("Failed", justify="right", style="red", width=8)
    table.add_column("Other", justify="right", width=8)
    
    for namespace, stats in sorted(pods_summary.items()):
        table.add_row(
            namespace,
            str(stats['total']),
            str(stats['running']),
            str(stats['pending']),
            str(stats['failed']),
            str(stats['other'])
        )
    
    return table


def create_services_table(services):
    """Create a rich table for LoadBalancer services"""
    table = Table(title="🌐 LoadBalancer Services", show_header=True, header_style="bold green")
    
    table.add_column("Namespace", style="cyan", width=15)
    table.add_column("Service", style="yellow", width=25)
    table.add_column("External IP", style="magenta", width=15)
    table.add_column("Ports", style="green", width=20)
    
    for svc in services:
        table.add_row(
            svc['namespace'],
            svc['name'],
            svc['external_ip'],
            svc['ports']
        )
    
    return table


def get_cluster_info():
    """Get cluster info"""
    output = run_kubectl("cluster-info")
    return output if output else "Unable to get cluster info"


def main():
    console.clear()
    
    # Header
    console.print(Panel.fit(
        "[bold cyan]K3s Cluster Monitor[/bold cyan]\n"
        "[yellow]Mac Mini M4 (192.168.1.201)[/yellow]\n"
        f"[green]Time: {time.strftime('%Y-%m-%d %H:%M:%S')}[/green]",
        border_style="blue"
    ))
    
    console.print("\n[bold]Fetching cluster data...[/bold]\n")
    
    # Get all data
    nodes = get_nodes_status()
    metrics = get_nodes_metrics()
    pods_summary = get_pods_summary()
    services = get_services_lb()
    
    # Display cluster info
    cluster_info = get_cluster_info()
    console.print(Panel(cluster_info, title="🎯 Cluster Info", border_style="green"))
    console.print()
    
    # Display nodes
    if nodes:
        console.print(create_nodes_table(nodes, metrics))
        console.print()
    else:
        console.print("[red]❌ Unable to fetch nodes information[/red]\n")
    
    # Display pods summary
    if pods_summary:
        console.print(create_pods_table(pods_summary))
        console.print()
    else:
        console.print("[red]❌ Unable to fetch pods information[/red]\n")
    
    # Display LoadBalancer services
    if services:
        console.print(create_services_table(services))
        console.print()
    else:
        console.print("[yellow]⚠️  No LoadBalancer services found[/yellow]\n")
    
    # Summary stats
    total_nodes = len(nodes)
    ready_nodes = sum(1 for n in nodes if n['status'] == 'Ready')
    total_pods = sum(s['total'] for s in pods_summary.values())
    running_pods = sum(s['running'] for s in pods_summary.values())
    total_lb = len(services)
    
    summary = (
        f"[bold cyan]Nodes:[/bold cyan] {ready_nodes}/{total_nodes} Ready  |  "
        f"[bold green]Pods:[/bold green] {running_pods}/{total_pods} Running  |  "
        f"[bold magenta]LoadBalancers:[/bold magenta] {total_lb} Active"
    )
    
    console.print(Panel(summary, title="📊 Summary", border_style="cyan"))
    
    # Quick commands
    console.print("\n[bold]Quick Commands:[/bold]")
    console.print("  [cyan]kubectl get pods -A[/cyan]           - List all pods")
    console.print("  [cyan]kubectl get svc -A[/cyan]            - List all services")
    console.print("  [cyan]kubectl top nodes[/cyan]             - Node resource usage")
    console.print("  [cyan]kubectl top pods -A[/cyan]           - Pod resource usage")
    console.print("  [cyan]kubectl get events -A --sort-by='.lastTimestamp'[/cyan] - Recent events\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)

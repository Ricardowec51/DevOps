#!/usr/bin/env python3
"""
PostgreSQL Monitor for K3s Cluster
Monitors PostgreSQL instances running in the cluster
"""

import subprocess
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def run_kubectl(cmd):
    """Execute kubectl command"""
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


def get_postgres_pods():
    """Get all PostgreSQL pods"""
    output = run_kubectl("get pods -A --no-headers | grep postgres")
    if not output:
        return []
    
    pods = []
    for line in output.split('\n'):
        parts = line.split()
        if len(parts) >= 5:
            pods.append({
                'namespace': parts[0],
                'name': parts[1],
                'ready': parts[2],
                'status': parts[3],
                'restarts': parts[4],
                'age': parts[5] if len(parts) > 5 else 'N/A'
            })
    return pods


def get_postgres_services():
    """Get PostgreSQL services"""
    output = run_kubectl("get svc -A --no-headers | grep postgres")
    if not output:
        return []
    
    services = []
    for line in output.split('\n'):
        parts = line.split()
        if len(parts) >= 6:
            services.append({
                'namespace': parts[0],
                'name': parts[1],
                'type': parts[2],
                'cluster_ip': parts[3],
                'external_ip': parts[4],
                'ports': parts[5]
            })
    return services


def exec_in_pod(namespace, pod, command):
    """Execute command in pod"""
    cmd = f"exec -n {namespace} {pod} -- {command}"
    return run_kubectl(cmd)


def get_databases(namespace, pod):
    """List databases in PostgreSQL instance"""
    output = exec_in_pod(namespace, pod, "psql -U postgres -t -c 'SELECT datname FROM pg_database WHERE datistemplate = false;'")
    if output:
        return [db.strip() for db in output.split('\n') if db.strip()]
    return []


def get_pg_version(namespace, pod):
    """Get PostgreSQL version"""
    output = exec_in_pod(namespace, pod, "psql -U postgres -t -c 'SELECT version();'")
    if output:
        return output.strip()
    return "Unknown"


def get_connections(namespace, pod):
    """Get active connections"""
    output = exec_in_pod(namespace, pod, "psql -U postgres -t -c 'SELECT count(*) FROM pg_stat_activity;'")
    if output:
        return output.strip()
    return "0"


def get_database_sizes(namespace, pod):
    """Get database sizes"""
    output = exec_in_pod(namespace, pod, 
        "psql -U postgres -t -c \"SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database WHERE datistemplate = false;\"")
    if output:
        sizes = {}
        for line in output.split('\n'):
            if '|' in line:
                parts = line.split('|')
                if len(parts) == 2:
                    sizes[parts[0].strip()] = parts[1].strip()
        return sizes
    return {}


def main():
    console.clear()
    
    # Header
    console.print(Panel.fit(
        "[bold cyan]PostgreSQL Cluster Monitor[/bold cyan]\n"
        "[yellow]K3s Cluster Database Status[/yellow]",
        border_style="blue"
    ))
    
    # Get PostgreSQL pods
    pods = get_postgres_pods()
    
    if not pods:
        console.print("[red]❌ No PostgreSQL pods found[/red]")
        return
    
    # Display pods table
    pods_table = Table(title="🐘 PostgreSQL Pods", show_header=True, header_style="bold cyan")
    pods_table.add_column("Namespace", style="cyan")
    pods_table.add_column("Pod Name", style="yellow")
    pods_table.add_column("Ready", justify="center")
    pods_table.add_column("Status", justify="center")
    pods_table.add_column("Restarts", justify="right")
    pods_table.add_column("Age", justify="right")
    
    for pod in pods:
        status_icon = "✅" if pod['status'] == 'Running' else "⚠️" if pod['status'] == 'Completed' else "❌"
        pods_table.add_row(
            pod['namespace'],
            pod['name'],
            pod['ready'],
            f"{status_icon} {pod['status']}",
            pod['restarts'],
            pod['age']
        )
    
    console.print(pods_table)
    console.print()
    
    # Display services
    services = get_postgres_services()
    if services:
        svc_table = Table(title="🌐 PostgreSQL Services", show_header=True, header_style="bold green")
        svc_table.add_column("Namespace", style="cyan")
        svc_table.add_column("Service", style="yellow")
        svc_table.add_column("Type", style="blue")
        svc_table.add_column("External IP", style="magenta")
        svc_table.add_column("Ports", style="green")
        
        for svc in services:
            svc_table.add_row(
                svc['namespace'],
                svc['name'],
                svc['type'],
                svc['external_ip'],
                svc['ports']
            )
        
        console.print(svc_table)
        console.print()
    
    # Get detailed info from running pods
    running_pods = [p for p in pods if p['status'] == 'Running' and p['ready'].startswith('1/')]
    
    if running_pods:
        console.print("[bold]📊 Database Details:[/bold]\n")
        
        for pod in running_pods[:2]:  # Limit to first 2 running pods
            console.print(f"[cyan]Pod:[/cyan] {pod['name']}")
            
            # Version
            version = get_pg_version(pod['namespace'], pod['name'])
            if version and version != "Unknown":
                console.print(f"  [green]Version:[/green] {version[:80]}...")
            
            # Connections
            connections = get_connections(pod['namespace'], pod['name'])
            console.print(f"  [yellow]Active Connections:[/yellow] {connections}")
            
            # Databases
            databases = get_databases(pod['namespace'], pod['name'])
            if databases:
                console.print(f"  [blue]Databases:[/blue] {', '.join(databases)}")
            
            # Database sizes
            sizes = get_database_sizes(pod['namespace'], pod['name'])
            if sizes:
                console.print(f"  [magenta]Sizes:[/magenta]")
                for db, size in sizes.items():
                    console.print(f"    • {db}: {size}")
            
            console.print()
    
    # Quick commands
    console.print("[bold]Quick Commands:[/bold]")
    console.print("  [cyan]pg-connect[/cyan]           - Connect to PostgreSQL")
    console.print("  [cyan]pg-databases[/cyan]         - List all databases")
    console.print("  [cyan]pg-connections[/cyan]       - Show active connections")
    console.print("  [cyan]pg-backup[/cyan]            - Check backup status\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)

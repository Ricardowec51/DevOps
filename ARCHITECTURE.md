# System Architecture

## Overview

The `proxmox-vm-creator` system is designed around a **Central Controller** pattern. Instead of running scripts from a laptop which might change networks or context, all logic is centralized on a permanent **Admin VM**.

## Diagram

```mermaid
graph TD
    User[User Laptop] -->|SSH| Admin[Admin VM (Controller)]
    Admin -->|Proxmox API (443)| PVECluster[Proxmox Cluster]
    
    subgraph PVECluster [Physical Infrastructure]
        NodeA[Node: DELL]
        NodeB[Node: Nnuc13]
        NodeC[Node: BOSC]
        NodeD[Node: msa]
        NodeE[Node: msn2]
    end
    
    Admin -.->|SSH (22)| Masters[K3s Masters]
    Admin -.->|SSH (22)| Workers[K3s Workers]
    
    PVECluster -->|Hosts| Masters
    PVECluster -->|Hosts| Workers
```

## Components

### 1. Admin VM (The Brain)
- **IP**: `192.168.1.20`
- **OS**: Ubuntu Server
- **Role**: 
  - Hosts the `proxmox-vm-creator` codebase.
  - Maintains configuration state (`config.yaml`).
  - Holds SSH keys for accessing all child VMs.
  - Runs the Interactive CLI Menu.

### 2. Proxmox API Client
- **Protocol**: HTTPS (Port 8006 usually, via `proxmoxer` library).
- **Function**:
  - Clones VMs from templates.
  - Resizes disks.
  - Injects `cloud-init` configuration (User Data).
  - Manages Power State (Start/Stop/Reboot).

### 3. K3s Manager (Orchestrator)
- **Protocol**: SSH.
- **Tools**: `k3sup`, `kubectl`, `systemctl`.
- **Function**:
  - **Bootstrap**: Installs K3s on the first master.
  - **HA**: Deploys `kube-vip` DaemonSet for IP failover (`192.168.1.50`).
  - **Join**: Adds secondary masters and workers to the cluster.
  - **Lifecycle**: Can start/stop systemd services on all nodes for maintenance.

## Network Flow

1.  **Deployment**:
    Admin VM -> PVE API -> Create VM 3001 (Master-01).
    Admin VM -> PVE API -> Start VM 3001.
    VM 3001 boots -> DHCP/Static IP assigned via Cloud-Init.

2.  **K3s Installation**:
    Admin VM -> SSH (Master-01) -> Install K3s (Server).
    Admin VM -> SSH (Master-01) -> Apply Kube-VIP.
    Admin VM -> SSH (Worker-01) -> Join Cluster.

3.  **Maintenance (Stop Cluster)**:
    Admin VM -> SSH (Worker-01) -> `systemctl stop k3s-agent`.
    Admin VM -> SSH (Master-01) -> `systemctl stop k3s`.

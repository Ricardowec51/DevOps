#!/usr/bin/env python3
"""
Unified CLI Menu for Proxmox VM Creator
"""
import sys
import os
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Import Action Scripts
try:
    from lib.logger import log
    from create_vm import ProxmoxVMCreator
    from check_vms import check_vms
    from fix_and_optimize import fix_and_optimize
    from create_snapshot import create_snapshots
    from delete_all_vms import delete_vms
    from start_vms import start_vms
    from restart_vms import restart_vms
    from shutdown_vms import shutdown_vms_interactive
    from remove_cloudinit_all import remove_cloudinit_all
    from lib.k3s_manager import K3sManager
    from lib.setup_wizard import SetupWizard
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Ensure you are running from the project root and have dependencies installed.")
    sys.exit(1)

console = Console()

def print_header():
    console.clear()
    title = Text("🚀 Proxmox VM Creator Manager", style="bold cyan")
    console.print(Panel(title, border_style="cyan"))
    
def main():
    while True:
        print_header()
        
        action = questionary.select(
            "Selecciona una acción:",
            choices=[
                "1. 🚀 Crear VMs (Producción)",
                "2. 🧪 Crear VMs (Dry Run / Simulación)",
                "3. 🔍 Verificar Estado de VMs",
                "4. ▶️  Iniciar Todas las VMs",
                "5. 🔄 Reiniciar VMs (Aplicar cambios HW)",
                "6. 🛠️  Fix & Optimize (Resize Disk, SSD, FS)",
                "7. 📸 Crear Snapshots 'Pre-K3s'",
                "8. 🗑️  BORRAR Todas las VMs",
                "9. ☸️  Desplegar Cluster K3s (HA)",
                "10. 📊 Ver Estatus Cluster K3s (Nodos/IPs)",
                "11. 🚀 Iniciar Cluster K3s",
                "12. 🛑 Detener Cluster K3s",
                "13. 🌙 Apagar VMs (Selección Manual)",
                "14. 💿 Remover Cloud-Init Drives",
                "15. ☸️  Instalar MetalLB (LoadBalancer)",
                "16. 🌐 Deploy Nginx Test (verificar LB)",
                questionary.Separator(),
                "17. 🪄  Configuración / Setup Wizard",
                "0. ❌ Salir"
            ]
        ).ask()

        if not action or "Salir" in action:
            console.print("[bold cyan]¡Hasta luego! 👋[/bold cyan]")
            sys.exit(0)

        console.print(f"\n[bold green]Ejecutando: {action}...[/bold green]\n")
        
        # Extract the number from the selection (e.g. "1. Create" -> "1")
        choice_num = action.split('.')[0].strip()

        try:
            if choice_num == "1":
                if questionary.confirm("¿Seguro que deseas CREAR las VMs en Proxmox?").ask():
                    creator = ProxmoxVMCreator()
                    creator.run(dry_run=False)
            
            elif choice_num == "2":
                creator = ProxmoxVMCreator()
                creator.run(dry_run=True)
                
            elif choice_num == "3":
                check_vms()
                
            elif choice_num == "4":
                start_vms()
                
            elif choice_num == "5":
                if questionary.confirm("Esto REINICIARÁ las VMs. ¿Continuar?").ask():
                    restart_vms()
                    
            elif choice_num == "6":
                fix_and_optimize()
                
            elif choice_num == "7":
                create_snapshots()
                
            elif choice_num == "8":
                if questionary.text("Escribe 'borrar' para confirmar:").ask() == 'borrar':
                     delete_vms()
                else:
                    console.print("[red]Cancelado.[/red]")

            elif choice_num == "9":
                if questionary.confirm("🚀 ¿Desplegar K3s HA Cluster? (Asegúrate de haber iniciado las VMs)").ask():
                    k3s = K3sManager()
                    k3s.deploy()

            elif choice_num == "10":
                k3s = K3sManager()
                k3s.show_status()

            elif choice_num == "11":
                if questionary.confirm("🚀 ¿Iniciar servicios K3s en todo el cluster?").ask():
                    k3s = K3sManager()
                    k3s.start_cluster()

            elif choice_num == "12":
                if questionary.confirm("⚠️  ¿Detener todos los servicios K3s en el cluster?").ask():
                    k3s = K3sManager()
                    k3s.stop_cluster()

            elif choice_num == "13":
                shutdown_vms_interactive()

            elif choice_num == "14":
                if questionary.confirm("¿Remover Cloud-Init drives de todas las VMs?").ask():
                    remove_cloudinit_all()

            elif choice_num == "15":
                if questionary.confirm("¿Instalar MetalLB en el cluster K3s?").ask():
                    k3s = K3sManager()
                    k3s.install_metallb()

            elif choice_num == "16":
                if questionary.confirm("¿Desplegar nginx de prueba con LoadBalancer?").ask():
                    k3s = K3sManager()
                    k3s.deploy_nginx_test()

            elif choice_num == "17":
                wizard = SetupWizard()
                wizard.run()

        except Exception as e:
            console.print(f"[bold red]Error en la ejecución:[/bold red] {e}")
        
        input("\nPresiona Enter para volver al menú...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold cyan]Saliendo...[/bold cyan]")

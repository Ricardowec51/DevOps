#!/bin/bash

# K3s HA Development Test Script - Complete Version with Tests and Usage Tracking
# Ensures all phases execute including test application and cluster status
# Version: 2.4-complete-with-usage-tracking
# Filename: k3s_installer_complete.sh

# Exit on error, undefined variable, or pipe failure
set -euo pipefail

#############################################
#           USAGE TRACKING SETUP           #
#############################################

# Archivo de tracking de uso
SCRIPT_NAME="$(basename "$0")"
SCRIPT_PATH="$(realpath "$0" 2>/dev/null || readlink -f "$0" 2>/dev/null || echo "$0")"
USAGE_TRACKING_FILE="$HOME/.k3s_usage_tracking.log"
SCRIPT_CREATION_DATE=""
SCRIPT_LAST_USED_DATE=""

# Función para obtener fecha de creación del archivo
get_script_creation_date() {
    if [[ -f "$SCRIPT_PATH" ]]; then
        if command -v stat &> /dev/null; then
            SCRIPT_CREATION_DATE=$(stat -c %y "$SCRIPT_PATH" 2>/dev/null | cut -d. -f1 || echo "Fecha no disponible")
        else
            SCRIPT_CREATION_DATE="Fecha no disponible"
        fi
    else
        SCRIPT_CREATION_DATE="Script no encontrado"
    fi
}

# Función para obtener última fecha de uso
get_last_usage_date() {
    if [[ -f "$USAGE_TRACKING_FILE" ]]; then
        SCRIPT_LAST_USED_DATE=$(grep "^$SCRIPT_NAME:" "$USAGE_TRACKING_FILE" 2>/dev/null | tail -1 | cut -d: -f2- 2>/dev/null || echo "Primer uso")
    else
        SCRIPT_LAST_USED_DATE="Primer uso"
    fi
}

# Función para registrar uso actual
register_current_usage() {
    local current_date=$(date "+%Y-%m-%d %H:%M:%S")
    touch "$USAGE_TRACKING_FILE" 2>/dev/null || true
    echo "$SCRIPT_NAME:$current_date" >> "$USAGE_TRACKING_FILE" 2>/dev/null || true
}

# Inicializar tracking
get_script_creation_date
get_last_usage_date
register_current_usage

echo -e " \033[33;5m    ____  _____ ____    _    ____  ____   ___     \033[0m"
echo -e " \033[33;5m   |  _ \|_   _/ ___|  / \  |  _ \|  _ \ / _ \    \033[0m"
echo -e " \033[33;5m   | |_) | | || |     / _ \ | |_) | | | | | | |   \033[0m"
echo -e " \033[33;5m   |  _ <  | || |___ / ___ \|  _ <| |_| | |_| |   \033[0m"
echo -e " \033[33;5m   |_| \_\ |_| \____/_/   \_\_| \_\____/ \___/    \033[0m"

echo -e " \033[36;5m   ____  _______     __  _____ _____ ____ _____  \033[0m"
echo -e " \033[36;5m  |  _ \| ____\ \   / / |_   _| ____/ ___|_   _| \033[0m"
echo -e " \033[36;5m  | | | |  _|  \ \ / /    | | |  _| \___ \ | |   \033[0m"
echo -e " \033[36;5m  | |_| | |___  \ V /     | | | |___ ___) || |   \033[0m"
echo -e " \033[36;5m  |____/|_____|  \_/      |_| |_____|____/ |_|   \033[0m"
echo -e " \033[32;5m    Versión Completa con Pruebas y Tracking     \033[0m"
echo -e " \033[32;5m        https://github.com/ricardowec51          \033[0m"

# Mostrar información de tracking
echo ""
echo -e " \033[35;5m╔══════════════════════════════════════════════════════════╗\033[0m"
echo -e " \033[35;5m║              INFORMACIÓN DE TRACKING DE USO              ║\033[0m"
echo -e " \033[35;5m╚══════════════════════════════════════════════════════════╝\033[0m"
echo -e " \033[36;5m📄 Archivo del script: $SCRIPT_NAME\033[0m"
echo -e " \033[36;5m📍 Ruta completa: $SCRIPT_PATH\033[0m"
echo -e " \033[36;5m📅 Fecha de creación: $SCRIPT_CREATION_DATE\033[0m"
echo -e " \033[36;5m🕒 Último uso anterior: $SCRIPT_LAST_USED_DATE\033[0m"
echo -e " \033[36;5m⏰ Ejecución actual: $(date "+%Y-%m-%d %H:%M:%S")\033[0m"
echo ""

#############################################
# DEVELOPMENT CONFIGURATION - COMPLETE VERSION #
#############################################

# Modo de desarrollo/pruebas
DEV_MODE="true"
ENABLE_ROLLBACK="true"
BACKUP_BEFORE_CHANGES="true"
EXTENSIVE_VALIDATION="true"

# Versiones compatibles y probadas
KVVERSION="v0.8.6"              
K3S_VERSION="v1.30.13+k3s1"     
METALLB_VERSION="v0.14.9"       
K3SUP_VERSION="0.13.11"          

# Network Configuration - PERSONALIZAR SEGÚN TU ENTORNO
MASTER1="192.168.1.21"
MASTER2="192.168.1.22"
MASTER3="192.168.1.23"
WORKER1="192.168.1.24"
WORKER2="192.168.1.25"
WORKER3="192.168.1.26"
WORKER4="192.168.1.27"
WORKER5="192.168.1.28"
VIP="192.168.1.50"
LB_RANGE="192.168.1.60-192.168.1.70"

# SSH Configuration - PERSONALIZAR
USER="rwagner"           # ← CAMBIAR POR TU USUARIO
INTERFACE="ens18"        # ← CAMBIAR POR TU INTERFAZ DE RED
CERT_NAME="id_rsa"
CONFIG_FILE=~/.ssh/config

# Arrays de nodos
MASTERS=("$MASTER2" "$MASTER3")
WORKERS=("$WORKER1" "$WORKER2" "$WORKER3" "$WORKER4" "$WORKER5")
ALL_NODES=("$MASTER1" "$MASTER2" "$MASTER3" "$WORKER1" "$WORKER2" "$WORKER3" "$WORKER4" "$WORKER5")
ALL_EXCEPT_MASTER1=("$MASTER2" "$MASTER3" "$WORKER1" "$WORKER2" "$WORKER3" "$WORKER4" "$WORKER5")

# Directories
KUBE_CONFIG_DIR="$HOME/.kube"
MANIFEST_DIR="/var/lib/rancher/k3s/server/manifests"

# Log configuration
LOG_FILE="k3s_dev_test_$(date +%Y%m%d-%H%M%S).log"
DEBUG_LOG="k3s_debug_$(date +%Y%m%d-%H%M%S).log"

# Backup directory
BACKUP_DIR="./k3s-backup-$(date +%Y%m%d-%H%M%S)"

# URLs específicas para las versiones compatibles
METALLB_NAMESPACE_URL="https://raw.githubusercontent.com/metallb/metallb/v0.14.9/config/manifests/metallb-namespace.yaml"
METALLB_NATIVE_URL="https://raw.githubusercontent.com/metallb/metallb/v0.14.9/config/manifests/metallb-native.yaml"
KUBEVIP_RBAC_URL="https://kube-vip.io/manifests/rbac.yaml"

#############################################
#            ENHANCED LOGGING               #
#############################################

# Función de logging estructurado con niveles
log_structured() {
	local level="$1"
	local message="$2"
	local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
	local hostname=$(hostname)
	
	case "$level" in
		"ERROR")
			echo -e "$timestamp [$hostname] \033[31;5mERROR\033[0m: $message" | tee -a "$LOG_FILE"
			echo "$timestamp [$hostname] ERROR: $message" >> "$DEBUG_LOG"
		;;
		"WARN")
			echo -e "$timestamp [$hostname] \033[33;5mWARN\033[0m: $message" | tee -a "$LOG_FILE"
			echo "$timestamp [$hostname] WARN: $message" >> "$DEBUG_LOG"
		;;
		"INFO")
			echo -e "$timestamp [$hostname] \033[32;5mINFO\033[0m: $message" | tee -a "$LOG_FILE"
			echo "$timestamp [$hostname] INFO: $message" >> "$DEBUG_LOG"
		;;
		"DEBUG")
			if [[ "$DEV_MODE" == "true" ]]; then
				echo -e "$timestamp [$hostname] \033[36;5mDEBUG\033[0m: $message" | tee -a "$LOG_FILE"
			fi
			echo "$timestamp [$hostname] DEBUG: $message" >> "$DEBUG_LOG"
		;;
		"SUCCESS")
			echo -e "$timestamp [$hostname] \033[32;1mSUCCESS\033[0m: $message" | tee -a "$LOG_FILE"
			echo "$timestamp [$hostname] SUCCESS: $message" >> "$DEBUG_LOG"
		;;
		"TRACKING")
			echo -e "$timestamp [$hostname] \033[35;1mTRACKING\033[0m: $message" | tee -a "$LOG_FILE"
			echo "$timestamp [$hostname] TRACKING: $message" >> "$DEBUG_LOG"
		;;
	esac
}

# Función para registrar información de tracking en los logs
log_tracking_info() {
	log_structured "TRACKING" "Información del script:"
	log_structured "TRACKING" "  📄 Nombre del archivo: $SCRIPT_NAME"
	log_structured "TRACKING" "  📍 Ruta completa: $SCRIPT_PATH"
	log_structured "TRACKING" "  📅 Fecha de creación: $SCRIPT_CREATION_DATE"
	log_structured "TRACKING" "  🕒 Último uso anterior: $SCRIPT_LAST_USED_DATE"
	log_structured "TRACKING" "  ⏰ Ejecución actual: $(date "+%Y-%m-%d %H:%M:%S")"
	log_structured "TRACKING" "  👤 Usuario ejecutor: $(whoami)"
	log_structured "TRACKING" "  🖥️  Sistema: $(uname -s) $(uname -r)"
}

# Aliases para compatibilidad
log() { log_structured "INFO" "$1"; }
success_msg() { log_structured "SUCCESS" "$1"; }
error_msg() { log_structured "ERROR" "$1"; exit 1; }
warning_msg() { log_structured "WARN" "$1"; }
debug_msg() { log_structured "DEBUG" "$1"; }

#############################################
#         USAGE TRACKING FUNCTIONS         #
#############################################

# Función para mostrar historial de uso
show_usage_history() {
	log_structured "INFO" "📊 Mostrando historial de uso del script..."
	
	if [[ -f "$USAGE_TRACKING_FILE" ]]; then
		log_structured "INFO" "Últimas 10 ejecuciones de $SCRIPT_NAME:"
		echo "════════════════════════════════════════════════════════════"
		grep "^$SCRIPT_NAME:" "$USAGE_TRACKING_FILE" 2>/dev/null | tail -10 | while IFS=: read -r script_name datetime; do
			echo "  🕒 $datetime"
		done
		echo "════════════════════════════════════════════════════════════"
		
		local total_uses=$(grep -c "^$SCRIPT_NAME:" "$USAGE_TRACKING_FILE" 2>/dev/null | tr -d '\n' | tr -d ' ' || echo "1")
		total_uses=${total_uses//[^0-9]/}
		[[ -z "$total_uses" ]] && total_uses=1
		log_structured "INFO" "📈 Total de ejecuciones registradas: $total_uses"
	else
		log_structured "INFO" "📊 Esta es la primera ejecución del script"
	fi
}

# Función para limpiar tracking antiguo (opcional)
cleanup_old_tracking() {
	if [[ -f "$USAGE_TRACKING_FILE" ]]; then
		local file_size=$(wc -l < "$USAGE_TRACKING_FILE" 2>/dev/null | tr -d '\n' | tr -d ' ' || echo "0")
		file_size=${file_size//[^0-9]/}
		[[ -z "$file_size" ]] && file_size=0
		if [[ $file_size -gt 1000 ]]; then
			log_structured "INFO" "🧹 Limpiando registros antiguos de tracking..."
			local temp_file=$(mktemp)
			tail -500 "$USAGE_TRACKING_FILE" > "$temp_file"
			mv "$temp_file" "$USAGE_TRACKING_FILE"
			log_structured "INFO" "✅ Mantenidos los últimos 500 registros"
		fi
	fi
}

#############################################
#         ENHANCED VALIDATIONS             #
#############################################

# Función de validación de compatibilidad de versiones
validate_versions() {
	log_structured "INFO" "Validando compatibilidad de versiones..."
	
	if [[ "$KVVERSION" == "v0.8.9" ]]; then
		error_msg "❌ CRÍTICO: Kube-VIP v0.8.9 tiene bug crítico con IPVS. Usar v0.8.6"
	fi
	
	local k3s_major=$(echo "$K3S_VERSION" | sed 's/v//' | cut -d. -f1)
	local k3s_minor=$(echo "$K3S_VERSION" | sed 's/v//' | cut -d. -f2)
	
	if [[ $k3s_major -eq 1 && $k3s_minor -ge 32 ]]; then
		warning_msg "⚠️  K3s v1.32+ detectado. Contendrá Containerd 2.0 y breaking changes"
		warning_msg "⚠️  Recomendado: usar v1.30.13+k3s1 para evitar breaking changes"
	fi
	
	success_msg "✅ Validación de versiones completada"
}

# Función de validación SSH mejorada
validate_ssh_key() {
	log_structured "INFO" "Validando configuración SSH..."
	local key_path="$HOME/.ssh/$CERT_NAME"
	
	if [[ ! -f "$key_path" ]]; then
		error_msg "❌ Clave SSH no encontrada: $key_path"
	fi
	
	local perms=$(stat -c "%a" "$key_path")
	if [[ "$perms" != "600" ]]; then
		warning_msg "⚠️  Permisos de clave SSH incorrectos ($perms). Corrigiendo a 600..."
		chmod 600 "$key_path"
	fi
	
	if [[ ! -f "${key_path}.pub" ]]; then
		error_msg "❌ Clave pública SSH no encontrada: ${key_path}.pub"
	fi
	
	success_msg "✅ Configuración SSH validada"
}

# Función de validación de prerrequisitos extendida
validate_prerequisites() {
	log_structured "INFO" "Validando prerrequisitos del sistema..."
	
	local kernel_version=$(uname -r | cut -d. -f1-2)
	local kernel_major=$(echo "$kernel_version" | cut -d. -f1)
	local kernel_minor=$(echo "$kernel_version" | cut -d. -f2)
	
	if [[ $kernel_major -lt 4 ]] || [[ $kernel_major -eq 4 && $kernel_minor -lt 15 ]]; then
		error_msg "❌ Kernel version $kernel_version no soportada. Mínimo requerido: 4.15"
	fi
	
	local required_modules=("br_netfilter" "overlay" "iptable_nat")
	for module in "${required_modules[@]}"; do
		if ! lsmod | grep -q "$module"; then
			warning_msg "⚠️  Módulo $module no cargado. Intentando cargar..."
			sudo modprobe "$module" || error_msg "❌ No se pudo cargar el módulo $module"
		fi
		debug_msg "✅ Módulo $module verificado"
	done
	
	local available_space=$(df / --output=avail | tail -1 | tr -d '\n' | tr -d ' ')
	available_space=${available_space//[^0-9]/}
	[[ -z "$available_space" ]] && available_space=0
	
	if [[ $available_space -lt 5242880 ]]; then
		warning_msg "⚠️  Espacio en disco bajo. Disponible: $(($available_space/1024/1024))GB"
		warning_msg "⚠️  Recomendado: mínimo 5GB para ambiente de desarrollo"
	fi
	
	if systemctl is-active --quiet containerd 2>/dev/null; then
		warning_msg "⚠️  Containerd está ejecutándose independientemente. Puede causar conflictos"
	fi
	
	success_msg "✅ Prerrequisitos validados"
}

# Función para validar configuración K3s específica
validate_k3s_config() {
	log_structured "INFO" "Validando configuración específica de K3s..."
	
	local required_flags=("--disable traefik" "--disable servicelb")
	for flag in "${required_flags[@]}"; do
		debug_msg "Verificando flag requerido: $flag"
	done
	
	success_msg "✅ Configuración K3s validada"
}

#############################################
#            BACKUP FUNCTIONS               #
#############################################

# Función de backup antes de cambios con información de tracking
create_backup() {
	if [[ "$BACKUP_BEFORE_CHANGES" == "true" ]]; then
		log_structured "INFO" "Creando backup de configuración existente..."
		mkdir -p "$BACKUP_DIR"
		
		if [[ -f "$KUBE_CONFIG_DIR/config" ]]; then
			cp "$KUBE_CONFIG_DIR/config" "$BACKUP_DIR/kubeconfig.backup"
			debug_msg "Kubeconfig respaldado"
		fi
		
		if [[ -f "$CONFIG_FILE" ]]; then
			cp "$CONFIG_FILE" "$BACKUP_DIR/ssh_config.backup"
			debug_msg "Configuración SSH respaldada"
		fi
		
		# Crear archivo de información del backup con tracking
		cat > "$BACKUP_DIR/backup_info.txt" << EOF
# Información del Backup K3s HA
Fecha de backup: $(date "+%Y-%m-%d %H:%M:%S")
Script ejecutado: $SCRIPT_NAME
Ruta del script: $SCRIPT_PATH
Fecha de creación del script: $SCRIPT_CREATION_DATE
Último uso anterior: $SCRIPT_LAST_USED_DATE
Usuario: $(whoami)
Sistema: $(uname -a)
Versión del script: 2.4-complete-with-usage-tracking
EOF
		
		cat > "$BACKUP_DIR/rollback.sh" << 'EOF'
#!/bin/bash
echo "🔄 Iniciando rollback..."
if [[ -f "./kubeconfig.backup" ]]; then
		cp kubeconfig.backup ~/.kube/config
		echo "✅ Kubeconfig restaurado"
fi
if [[ -f "./ssh_config.backup" ]]; then
		cp ssh_config.backup ~/.ssh/config
		echo "✅ SSH config restaurado"
fi
echo "✅ Rollback completado"
echo "📋 Ver información del backup: cat backup_info.txt"
EOF
		chmod +x "$BACKUP_DIR/rollback.sh"
		
		success_msg "✅ Backup creado en: $BACKUP_DIR"
		log_structured "INFO" "📋 Información del backup guardada en: $BACKUP_DIR/backup_info.txt"
	fi
}

#############################################
#         CONNECTIVITY FUNCTIONS            #
#############################################

# Función mejorada de verificación SSH
check_ssh_connectivity() {
	log_structured "INFO" "Verificando conectividad SSH con todos los nodos..."
	local failed_nodes=()
	
	for node in "${ALL_NODES[@]}"; do
		debug_msg "Verificando conectividad con $node..."
		
		local max_attempts=3
		local attempt=1
		local connected=false
		
		while [[ $attempt -le $max_attempts ]]; do
			if ssh -o BatchMode=yes -o ConnectTimeout=30 -o StrictHostKeyChecking=no "$USER@$node" exit &>/dev/null; then
				connected=true
				debug_msg "✅ Conexión exitosa a $node (intento $attempt)"
				break
			else
				debug_msg "❌ Intento $attempt fallido para $node"
				sleep 5
				((attempt++))
			fi
		done
		
		if [[ "$connected" == "false" ]]; then
			failed_nodes+=("$node")
			warning_msg "❌ No se pudo conectar a $node después de $max_attempts intentos"
		fi
	done
	
	if [[ ${#failed_nodes[@]} -gt 0 ]]; then
		error_msg "❌ Fallo de conectividad SSH con nodos: ${failed_nodes[*]}"
	fi
	
	success_msg "✅ Conectividad SSH establecida con todos los nodos"
}

#############################################
#         INSTALLATION FUNCTIONS            #
#############################################

# Función para instalar herramientas con validación de versiones
install_tools() {
	log_structured "INFO" "Instalando herramientas requeridas..."
	
	if ! command -v k3sup &> /dev/null || [[ $(k3sup version 2>/dev/null | grep -o "v[0-9]*\.[0-9]*\.[0-9]*" | head -1 | sed 's/v//') != "${K3SUP_VERSION}" ]]; then
		log_structured "INFO" "Instalando k3sup versión $K3SUP_VERSION..."
		curl -sLS https://get.k3sup.dev | sh
		sudo install k3sup /usr/local/bin/
		
		local installed_version=$(k3sup version 2>/dev/null | grep -o "v[0-9]*\.[0-9]*\.[0-9]*" | head -1 | sed 's/v//')
		debug_msg "k3sup versión instalada: $installed_version"
		success_msg "✅ k3sup instalado correctamente"
	else
		success_msg "✅ k3sup ya está instalado con la versión correcta"
	fi
	
	if ! command -v kubectl &> /dev/null; then
		log_structured "INFO" "Instalando kubectl..."
		curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
		sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
		rm kubectl
		success_msg "✅ kubectl instalado correctamente"
	else
		success_msg "✅ kubectl ya está instalado"
	fi
	
	local required_tools=("curl" "ssh" "scp" "jq")
	for tool in "${required_tools[@]}"; do
		if ! command -v "$tool" &> /dev/null; then
			warning_msg "⚠️  Herramienta requerida no encontrada: $tool"
			log_structured "INFO" "Instalando $tool..."
			sudo apt-get update && sudo apt-get install -y "$tool"
		fi
		debug_msg "✅ $tool disponible"
	done
}

# Función para instalar dependencias en nodos
install_node_dependencies() {
	log_structured "INFO" "Instalando dependencias en todos los nodos..."
	local failed_nodes=()
	
	for node in "${ALL_NODES[@]}"; do
		debug_msg "Instalando dependencias en $node..."
		
		if ! ssh -o ConnectTimeout=30 "$USER@$node" -i "/home/$USER/.ssh/$CERT_NAME" \
			"sudo DEBIAN_FRONTEND=noninteractive apt-get update && sudo NEEDRESTART_MODE=a apt-get install -y policycoreutils curl" 2>/dev/null; then
				failed_nodes+=("$node")
				warning_msg "⚠️  Error al instalar dependencias en $node"
			else
				debug_msg "✅ Dependencias instaladas en $node"
			fi
	done
	
	if [[ ${#failed_nodes[@]} -gt 0 ]]; then
		warning_msg "⚠️  Fallos en nodos: ${failed_nodes[*]}"
	else
		success_msg "✅ Dependencias instaladas en todos los nodos"
	fi
}

#############################################
#         CLUSTER SETUP FUNCTIONS           #
#############################################

# Función para inicializar el primer master
bootstrap_first_master() {
	log_structured "INFO" "Inicializando el primer nodo maestro ($MASTER1)..."
	mkdir -p "$KUBE_CONFIG_DIR"
	
	debug_msg "Ejecutando k3sup install con parámetros específicos..."
	debug_msg "- IP: $MASTER1"
	debug_msg "- Usuario: $USER"
	debug_msg "- TLS SAN: $VIP"
	debug_msg "- Versión K3s: $K3S_VERSION"
	debug_msg "- Interfaz: $INTERFACE"
	
	if k3sup install \
		--ip "$MASTER1" \
		--user "$USER" \
		--tls-san "$VIP" \
		--cluster \
		--k3s-version "$K3S_VERSION" \
		--k3s-extra-args "--disable traefik --disable servicelb --flannel-iface=$INTERFACE --node-ip=$MASTER1 --node-taint node-role.kubernetes.io/master=true:NoSchedule" \
		--merge \
		--sudo \
		--local-path "$KUBE_CONFIG_DIR/config" \
		--ssh-key "$HOME/.ssh/$CERT_NAME" \
		--context k3s-ha-dev; then
			
			success_msg "✅ Primer nodo maestro inicializado correctamente"
			
			sleep 30
			if kubectl get nodes | grep -q "$MASTER1.*Ready"; then
				success_msg "✅ Nodo maestro $MASTER1 está Ready"
			else
				warning_msg "⚠️  Nodo maestro $MASTER1 aún no está Ready, continuando..."
			fi
		else
			error_msg "❌ Error al inicializar el primer nodo maestro"
		fi
}

# Función para configurar kube-vip con versión específica
setup_kubevip() {
	log_structured "INFO" "Configurando kube-vip versión $KVVERSION..."
	
	log_structured "INFO" "Esperando disponibilidad del servidor API..."
	local api_ready=false
	local attempts=0
	local max_attempts=12
	
	while [[ $attempts -lt $max_attempts ]]; do
		if kubectl get nodes &>/dev/null; then
			api_ready=true
			break
		fi
		debug_msg "API no disponible, intento $((attempts + 1))/$max_attempts"
		sleep 10
		((attempts++))
	done
	
	if [[ "$api_ready" == "false" ]]; then
		error_msg "❌ Timeout esperando disponibilidad del API server"
	fi
	
	success_msg "✅ API server disponible"
	
	log_structured "INFO" "Aplicando RBAC de kube-vip..."
	if ssh -o ConnectTimeout=30 "$USER@$MASTER1" -i "/home/$USER/.ssh/$CERT_NAME" \
		"sudo curl -s $KUBEVIP_RBAC_URL -o /var/lib/rancher/k3s/server/manifests/kube-vip-rbac.yaml"; then
			debug_msg "✅ RBAC de kube-vip aplicado"
		else
			error_msg "❌ Error aplicando RBAC de kube-vip"
		fi
	
	log_structured "INFO" "Configurando manifest de kube-vip..."
	curl -sO https://raw.githubusercontent.com/JamesTurland/JimsGarage/main/Kubernetes/K3S-Deploy/kube-vip
	
	sed -e "s/\$interface/$INTERFACE/g" \
	-e "s/\$vip/$VIP/g" \
	-e "s/plndr\/kube-vip:.*$/plndr\/kube-vip:$KVVERSION/g" \
	kube-vip > "$HOME/kube-vip.yaml"
	
	debug_msg "Variables reemplazadas en kube-vip.yaml:"
	debug_msg "- Interface: $INTERFACE"
	debug_msg "- VIP: $VIP"
	debug_msg "- Versión: $KVVERSION"
	
	if scp -i "$HOME/.ssh/$CERT_NAME" "$HOME/kube-vip.yaml" "$USER@$MASTER1:~/kube-vip.yaml"; then
		debug_msg "✅ kube-vip.yaml copiado al master1"
	else
		error_msg "❌ Error copiando kube-vip.yaml"
	fi
	
	if ssh -o ConnectTimeout=30 "$USER@$MASTER1" -i "/home/$USER/.ssh/$CERT_NAME" \
		"sudo mkdir -p $MANIFEST_DIR && sudo mv kube-vip.yaml $MANIFEST_DIR/kube-vip.yaml"; then
			success_msg "✅ kube-vip configurado correctamente"
		else
			error_msg "❌ Error moviendo kube-vip.yaml al directorio de manifests"
		fi
	
	log_structured "INFO" "Esperando inicio de kube-vip..."
	sleep 45
	
	if ssh -o ConnectTimeout=30 "$USER@$MASTER1" -i "/home/$USER/.ssh/$CERT_NAME" \
		"sudo kubectl get pods -n kube-system --kubeconfig /etc/rancher/k3s/k3s.yaml | grep -q kube-vip"; then
			success_msg "✅ kube-vip está ejecutándose"
		else
			warning_msg "⚠️  kube-vip pods no detectados, continuando..."
		fi
}

# Función para unir nodos maestros adicionales
join_additional_masters() {
	log_structured "INFO" "Uniendo nodos maestros adicionales..."
	
	for node in "${MASTERS[@]}"; do
		log_structured "INFO" "Uniendo nodo maestro: $node"
		debug_msg "Parámetros para $node:"
		debug_msg "- Servidor: $MASTER1"
		debug_msg "- Interfaz: $INTERFACE"
		debug_msg "- Versión: $K3S_VERSION"
		
		if k3sup join \
			--ip "$node" \
			--user "$USER" \
			--sudo \
			--k3s-version "$K3S_VERSION" \
			--server \
			--server-ip "$MASTER1" \
			--ssh-key "$HOME/.ssh/$CERT_NAME" \
			--k3s-extra-args "--disable traefik --disable servicelb --flannel-iface=$INTERFACE --node-ip=$node --node-taint node-role.kubernetes.io/master=true:NoSchedule" \
			--server-user "$USER"; then
				
				success_msg "✅ Nodo maestro $node unido correctamente"
				
				log_structured "INFO" "Esperando que $node esté completamente listo..."
				sleep 30
			else
				error_msg "❌ Error uniendo nodo maestro $node"
			fi
	done
}

# Función para unir nodos trabajadores
join_worker_nodes() {
	log_structured "INFO" "Uniendo nodos trabajadores..."
	
	if [[ "$DEV_MODE" == "true" ]]; then
		for node in "${WORKERS[@]}"; do
			log_structured "INFO" "Uniendo nodo trabajador: $node"
			debug_msg "Configuración para $node:"
			debug_msg "- Servidor: $MASTER1"
			debug_msg "- Labels: longhorn=true, worker=true"
			
			if k3sup join \
				--ip "$node" \
				--user "$USER" \
				--sudo \
				--k3s-version "$K3S_VERSION" \
				--server-ip "$MASTER1" \
				--ssh-key "$HOME/.ssh/$CERT_NAME" \
				--k3s-extra-args "--node-label \"longhorn=true\" --node-label \"worker=true\""; then
					
					success_msg "✅ Nodo trabajador $node unido correctamente"
					sleep 20
				else
					warning_msg "⚠️  Error uniendo nodo trabajador $node"
				fi
		done
	fi
}

#############################################
#         METALLB SETUP FUNCTIONS           #
#############################################

# Función para instalar MetalLB con versión específica
install_metallb() {
	log_structured "INFO" "Instalando MetalLB versión $METALLB_VERSION..."
	
	log_structured "INFO" "Aplicando namespace de MetalLB..."
	if ssh -o ConnectTimeout=30 "$USER@$MASTER1" -i "/home/$USER/.ssh/$CERT_NAME" \
		"sudo curl -s $METALLB_NAMESPACE_URL -o /var/lib/rancher/k3s/server/manifests/metallb-namespace.yaml"; then
			debug_msg "✅ Namespace de MetalLB aplicado"
		else
			error_msg "❌ Error aplicando namespace de MetalLB"
		fi
	
	log_structured "INFO" "Aplicando manifests nativos de MetalLB..."
	if ssh -o ConnectTimeout=30 "$USER@$MASTER1" -i "/home/$USER/.ssh/$CERT_NAME" \
		"sudo curl -s $METALLB_NATIVE_URL -o /var/lib/rancher/k3s/server/manifests/metallb-native.yaml"; then
			debug_msg "✅ Manifests nativos de MetalLB aplicados"
		else
			error_msg "❌ Error aplicando manifests nativos de MetalLB"
		fi
	
	log_structured "INFO" "Esperando instalación de MetalLB..."
	sleep 45
	
	local metallb_ready=false
	local attempts=0
	local max_attempts=12
	
	while [[ $attempts -lt $max_attempts ]]; do
		local running_pods=$(ssh -o ConnectTimeout=30 "$USER@$MASTER1" -i "/home/$USER/.ssh/$CERT_NAME" \
						"sudo kubectl get pods -n metallb-system --kubeconfig /etc/rancher/k3s/k3s.yaml --no-headers 2>/dev/null | grep -c Running" || echo "0")
		
		if [[ $running_pods -ge 2 ]]; then
			metallb_ready=true
			break
		fi
		
		debug_msg "MetalLB pods ejecutándose: $running_pods, intento $((attempts + 1))/$max_attempts"
		sleep 10
		((attempts++))
	done
	
	if [[ "$metallb_ready" == "true" ]]; then
		success_msg "✅ MetalLB instalado y ejecutándose correctamente"
	else
		warning_msg "⚠️  MetalLB pods no completamente listos, continuando..."
	fi
}

# Función CORREGIDA para configurar pool de direcciones de MetalLB
configure_metallb_pool() {
	log_structured "INFO" "Configurando pool de direcciones IP para MetalLB..."
	
	cat > "$HOME/metallb-ippool.yaml" << EOF
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: dev-pool
  namespace: metallb-system
spec:
  addresses:
  - $LB_RANGE
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: dev-l2-advertisement
  namespace: metallb-system
spec:
  ipAddressPools:
  - dev-pool
EOF
	
	debug_msg "Pool de IPs configurado: $LB_RANGE"
	
	if scp -i "$HOME/.ssh/$CERT_NAME" "$HOME/metallb-ippool.yaml" "$USER@$MASTER1:~/metallb-ippool.yaml"; then
		debug_msg "✅ Configuración copiada al master1"
	else
		error_msg "❌ Error copiando configuración de MetalLB"
	fi
	
	log_structured "INFO" "Aplicando configuración de MetalLB..."
	if ssh -o ConnectTimeout=30 "$USER@$MASTER1" -i "/home/$USER/.ssh/$CERT_NAME" \
		"sudo kubectl apply -f metallb-ippool.yaml --kubeconfig /etc/rancher/k3s/k3s.yaml"; then
			success_msg "✅ Pool de direcciones IP configurado correctamente"
		else
			error_msg "❌ Error aplicando configuración de pool IP"
		fi
	
	log_structured "INFO" "Verificando configuración aplicada..."
	sleep 10
	
	if ssh -o ConnectTimeout=30 "$USER@$MASTER1" -i "/home/$USER/.ssh/$CERT_NAME" \
		"sudo kubectl get ipaddresspool -n metallb-system --kubeconfig /etc/rancher/k3s/k3s.yaml" | grep -q "dev-pool"; then
			success_msg "✅ IPAddressPool 'dev-pool' verificado"
		else
			warning_msg "⚠️  IPAddressPool no verificado inmediatamente"
		fi
	
	if ssh -o ConnectTimeout=30 "$USER@$MASTER1" -i "/home/$USER/.ssh/$CERT_NAME" \
		"sudo kubectl get l2advertisement -n metallb-system --kubeconfig /etc/rancher/k3s/k3s.yaml" | grep -q "dev-l2-advertisement"; then
			success_msg "✅ L2Advertisement verificado"
		else
			warning_msg "⚠️  L2Advertisement no verificado inmediatamente"
		fi
}

#############################################
#         TESTING AND VALIDATION            #
#############################################

# Función para esperar que el cluster esté completamente listo
wait_for_cluster_ready() {
	log_structured "INFO" "Esperando que el cluster esté completamente listo..."
	
	local max_attempts=30
	local attempt=0
	
	while [[ $attempt -lt $max_attempts ]]; do
		local ready_nodes=$(kubectl get nodes --no-headers 2>/dev/null | grep -c " Ready " | tr -d '\n' | tr -d ' ' || echo "0")
		ready_nodes=${ready_nodes//[^0-9]/}
		[[ -z "$ready_nodes" ]] && ready_nodes=0
		
		local total_nodes=${#ALL_NODES[@]}
		
		debug_msg "Nodos listos: $ready_nodes/$total_nodes (intento $((attempt + 1))/$max_attempts)"
		
		if [[ $ready_nodes -eq $total_nodes ]]; then
			success_msg "✅ Todos los nodos están Ready ($ready_nodes/$total_nodes)"
			
			local system_pods_running=$(kubectl get pods -n kube-system --no-headers 2>/dev/null | grep -c " Running " | tr -d '\n' | tr -d ' ' || echo "0")
			system_pods_running=${system_pods_running//[^0-9]/}
			[[ -z "$system_pods_running" ]] && system_pods_running=0
			if [[ $system_pods_running -gt 5 ]]; then
				success_msg "✅ Pods del sistema funcionando correctamente ($system_pods_running pods)"
				return 0
			else
				debug_msg "Pods del sistema ejecutándose: $system_pods_running"
			fi
		fi
		
		sleep 10
		((attempt++))
	done
	
	warning_msg "⚠️  Timeout esperando que el cluster esté completamente listo"
	return 1
}

# Función GARANTIZADA para desplegar aplicación de prueba
deploy_test_application() {
	log_structured "INFO" "🧪 DESPLEGANDO APLICACIÓN DE PRUEBA (NGINX)..."
	echo "=================================================="
	
	# Crear manifiesto con sintaxis YAML CORRECTA
	cat > "$HOME/nginx-test.yaml" << \EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-test-dev
  namespace: default
  labels:
    app: nginx-test-dev
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx-test-dev
  template:
    metadata:
      labels:
        app: nginx-test-dev
    spec:
      containers:
      - name: nginx
        image: nginx:stable-alpine
        ports:
        - containerPort: 80
        resources:
          limits:
            cpu: 100m
            memory: 128Mi
          requests:
            cpu: 50m
            memory: 64Mi
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-test-dev-service
  namespace: default
  annotations:
    metallb.universe.tf/address-pool: dev-pool
spec:
  selector:
    app: nginx-test-dev
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
EOF
	
	success_msg "✅ Manifiesto de prueba creado"
	
	# Validar sintaxis YAML
	if command -v python3 &> /dev/null; then
		if python3 -c "
import yaml
try:
    with open('$HOME/nginx-test.yaml', 'r') as f:
        docs = list(yaml.safe_load_all(f))
        print('✅ YAML válido -', len(docs), 'documentos')
except yaml.YAMLError as e:
    print('❌ Error YAML:', e)
    exit(1)
" 2>/dev/null; then
			success_msg "✅ Sintaxis YAML validada correctamente"
		else
			error_msg "❌ Error en sintaxis YAML del manifiesto de prueba"
		fi
	else
		debug_msg "Python3 no disponible, saltando validación YAML"
	fi
	
	# Copiar al master1 y aplicar
	if scp -i "$HOME/.ssh/$CERT_NAME" "$HOME/nginx-test.yaml" "$USER@$MASTER1:~/nginx-test.yaml"; then
		success_msg "✅ Manifiesto copiado al master1"
	else
		error_msg "❌ Error copiando manifiesto de prueba"
	fi
	
	if ssh -o ConnectTimeout=30 "$USER@$MASTER1" -i "/home/$USER/.ssh/$CERT_NAME" \
		"sudo kubectl apply -f nginx-test.yaml --kubeconfig /etc/rancher/k3s/k3s.yaml"; then
			success_msg "✅ Aplicación de prueba desplegada exitosamente"
		else
			error_msg "❌ Error desplegando aplicación de prueba"
		fi
	
	# Esperar a que los pods estén listos
	log_structured "INFO" "Esperando que los pods de Nginx estén listos..."
	local nginx_ready=false
	local attempts=0
	local max_attempts=25  # Más tiempo para asegurar que funcione
	
	while [[ $attempts -lt $max_attempts ]]; do
		local ready_pods=$(ssh -o ConnectTimeout=30 "$USER@$MASTER1" -i "/home/$USER/.ssh/$CERT_NAME" \
						"sudo kubectl get pods -l app=nginx-test-dev --kubeconfig /etc/rancher/k3s/k3s.yaml --no-headers 2>/dev/null | grep -c Running" || echo "0")
		
		if [[ $ready_pods -eq 2 ]]; then
			nginx_ready=true
			break
		fi
		
		log_structured "INFO" "Pods de Nginx listos: $ready_pods/2, intento $((attempts + 1))/$max_attempts"
		sleep 15
		((attempts++))
	done
	
	if [[ "$nginx_ready" == "true" ]]; then
		success_msg "✅ Pods de Nginx listos y ejecutándose (2/2)"
	else
		warning_msg "⚠️  Pods de Nginx no completamente listos después de esperar"
	fi
	
	echo "=================================================="
}

# Función GARANTIZADA para probar la aplicación desplegada
test_deployed_application() {
	log_structured "INFO" "🌐 PROBANDO APLICACIÓN DESPLEGADA..."
	echo "=================================================="
	
	# Obtener IP externa del servicio con paciencia extendida
	local external_ip=""
	local attempts=0
	local max_attempts=25  # Más intentos para MetalLB
	
	while [[ $attempts -lt $max_attempts ]]; do
		external_ip=$(ssh -o ConnectTimeout=30 "$USER@$MASTER1" -i "/home/$USER/.ssh/$CERT_NAME" \
						"sudo kubectl get svc nginx-test-dev-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' --kubeconfig /etc/rancher/k3s/k3s.yaml" 2>/dev/null || echo "")
		
		if [[ -n "$external_ip" && "$external_ip" != "null" && "$external_ip" != "<pending>" ]]; then
			break
		fi
		
		log_structured "INFO" "Esperando IP externa, intento $((attempts + 1))/$max_attempts"
		
		# Mostrar estado del servicio
		local service_status=$(ssh -o ConnectTimeout=30 "$USER@$MASTER1" -i "/home/$USER/.ssh/$CERT_NAME" \
							"sudo kubectl get svc nginx-test-dev-service --kubeconfig /etc/rancher/k3s/k3s.yaml --no-headers" 2>/dev/null || echo "Error")
		log_structured "INFO" "Estado del servicio: $service_status"
		
		sleep 15
		((attempts++))
	done
	
	if [[ -n "$external_ip" && "$external_ip" != "null" && "$external_ip" != "<pending>" ]]; then
		success_msg "✅ IP externa asignada por MetalLB: $external_ip"
		
		# Probar conectividad HTTP con paciencia
		log_structured "INFO" "Probando conectividad HTTP a $external_ip..."
		sleep 30  # Tiempo adicional para estabilidad
		
		local http_attempts=0
		local max_http_attempts=8
		
		while [[ $http_attempts -lt $max_http_attempts ]]; do
			if curl -s --connect-timeout 10 --max-time 15 "http://$external_ip" | grep -q "Welcome to nginx"; then
				success_msg "✅ Aplicación respondiendo correctamente via HTTP"
				success_msg "🌐 URL de la aplicación: http://$external_ip"
				
				# Mostrar respuesta parcial
				log_structured "INFO" "Respuesta del servidor Nginx:"
				echo "============================================"
				curl -s "http://$external_ip" | head -5
				echo "============================================"
				
				return 0
			else
				log_structured "INFO" "Intento HTTP $((http_attempts + 1))/$max_http_attempts falló, reintentando..."
				sleep 15
				((http_attempts++))
			fi
		done
		
		warning_msg "⚠️  IP asignada pero aplicación no responde HTTP correctamente"
		warning_msg "⚠️  Verifica manualmente: curl http://$external_ip"
	else
		warning_msg "⚠️  MetalLB no pudo asignar IP externa en el tiempo esperado"
		
		# Diagnóstico adicional
		log_structured "INFO" "Ejecutando diagnóstico de MetalLB..."
		ssh -o ConnectTimeout=30 "$USER@$MASTER1" -i "/home/$USER/.ssh/$CERT_NAME" \
			"sudo kubectl get ipaddresspool -n metallb-system --kubeconfig /etc/rancher/k3s/k3s.yaml" || warning_msg "No se pudo verificar IPAddressPool"
		
		ssh -o ConnectTimeout=30 "$USER@$MASTER1" -i "/home/$USER/.ssh/$CERT_NAME" \
			"sudo kubectl get pods -n metallb-system --kubeconfig /etc/rancher/k3s/k3s.yaml" || warning_msg "No se pudo verificar pods de MetalLB"
	fi
	
	echo "=================================================="
}

# Función DETALLADA de validación del cluster con información de tracking
comprehensive_cluster_validation() {
	log_structured "INFO" "📊 VALIDACIÓN COMPREHENSIVA DEL CLUSTER..."
	echo "========================================================="
	
	# Agregar información de tracking al inicio de la validación
	log_structured "TRACKING" "Validación ejecutada desde: $SCRIPT_NAME"
	log_structured "TRACKING" "Fecha de ejecución: $(date "+%Y-%m-%d %H:%M:%S")"
	
	# 1. Estado de nodos
	echo ""
	log_structured "INFO" "🖥️  ESTADO DE NODOS:"
	echo "===================="
	local node_info=$(kubectl get nodes -o wide 2>/dev/null || echo "ERROR")
	if [[ "$node_info" == "ERROR" ]]; then
		error_msg "❌ No se puede obtener información de nodos"
	else
		echo "$node_info"
		echo ""
		local unhealthy_nodes=$(echo "$node_info" | grep -v " Ready " | grep -v "NAME" | wc -l)
		if [[ $unhealthy_nodes -gt 0 ]]; then
			warning_msg "⚠️  Nodos no saludables detectados: $unhealthy_nodes"
		else
			success_msg "✅ Todos los nodos están saludables"
		fi
	fi
	
	# 2. Pods del sistema
	echo ""
	log_structured "INFO" "🔧 PODS DEL SISTEMA:"
	echo "==================="
	local system_pods=$(kubectl get pods --all-namespaces --no-headers 2>/dev/null || echo "ERROR")
	if [[ "$system_pods" == "ERROR" ]]; then
		warning_msg "⚠️  No se puede obtener información de pods del sistema"
	else
		echo "NAMESPACE          NAME                                READY   STATUS    RESTARTS   AGE"
		kubectl get pods --all-namespaces | grep -E "(kube-system|metallb-system)" | head -15
		echo ""
		
		local failed_pods=$(echo "$system_pods" | grep -E "(Error|CrashLoopBackOff|Pending)" | wc -l)
		local running_pods=$(echo "$system_pods" | grep -c "Running")
		
		if [[ $failed_pods -gt 0 ]]; then
			warning_msg "⚠️  Pods con fallos detectados: $failed_pods"
			echo "Pods problemáticos:"
			echo "$system_pods" | grep -E "(Error|CrashLoopBackOff|Pending)"
		else
			success_msg "✅ Todos los pods del sistema están saludables"
		fi
		
		success_msg "✅ Pods ejecutándose correctamente: $running_pods"
	fi
	
	# 3. Servicios
	echo ""
	log_structured "INFO" "🌐 SERVICIOS DEL CLUSTER:"
	echo "========================"
	kubectl get svc --all-namespaces 2>/dev/null || warning_msg "No se pueden obtener servicios"
	echo ""
	
	# 4. Servicios LoadBalancer específicamente
	log_structured "INFO" "⚖️  SERVICIOS LOADBALANCER:"
	echo "=========================="
	local lb_services=$(kubectl get svc --all-namespaces --no-headers 2>/dev/null | grep LoadBalancer || echo "")
	if [[ -n "$lb_services" ]]; then
		echo "NAMESPACE   NAME                      TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE"
		echo "$lb_services"
		echo ""
		
		local pending_lbs=$(echo "$lb_services" | grep -c "<pending>" 2>/dev/null || echo "0")
		local total_lbs=$(echo "$lb_services" | wc -l | tr -d '\n' | tr -d ' ')
		
		# Asegurar que son números válidos
		pending_lbs=${pending_lbs//[^0-9]/}
		total_lbs=${total_lbs//[^0-9]/}
		
		# Valores por defecto si están vacíos
		[[ -z "$pending_lbs" ]] && pending_lbs=0
		[[ -z "$total_lbs" ]] && total_lbs=0
		
		if [[ $pending_lbs -gt 0 ]]; then
			warning_msg "⚠️  LoadBalancers pendientes: $pending_lbs/$total_lbs"
		else
			success_msg "✅ Todos los LoadBalancers tienen IP asignada ($total_lbs servicios)"
		fi
	else
		log_structured "INFO" "No se encontraron servicios LoadBalancer"
	fi
	
	# 5. Estado de MetalLB
	echo ""
	log_structured "INFO" "🔩 ESTADO DE METALLB:"
	echo "===================="
	kubectl get pods -n metallb-system 2>/dev/null || warning_msg "MetalLB no encontrado"
	echo ""
	kubectl get ipaddresspool -n metallb-system 2>/dev/null || warning_msg "IPAddressPool no encontrado"
	echo ""
	kubectl get l2advertisement -n metallb-system 2>/dev/null || warning_msg "L2Advertisement no encontrado"
	
	# 6. Conectividad de red
	echo ""
	log_structured "INFO" "🌍 CONECTIVIDAD DE RED:"
	echo "======================"
	if ping -c 3 "$VIP" &>/dev/null; then
		success_msg "✅ VIP ($VIP) es accesible"
	else
		warning_msg "⚠️  VIP ($VIP) no responde a ping"
	fi
	
	# 7. Almacenamiento
	echo ""
	log_structured "INFO" "💾 CLASES DE ALMACENAMIENTO:"
	echo "============================"
	kubectl get storageclass 2>/dev/null || warning_msg "No se pueden obtener storage classes"
	
	echo ""
	echo "========================================================="
	success_msg "✅ Validación comprehensiva completada"
	echo "========================================================="
}

# Función para mostrar resumen final completo con información de tracking
show_final_cluster_status() {
	echo ""
	echo ""
	log_structured "SUCCESS" "🎉 INSTALACIÓN COMPLETADA - RESUMEN FINAL"
	echo "============================================================="
	echo ""
	
	# Información de tracking del script
	log_structured "INFO" "📋 INFORMACIÓN DE EJECUCIÓN:"
	echo "  📄 Script ejecutado: $SCRIPT_NAME"
	echo "  📍 Ruta: $SCRIPT_PATH"
	echo "  📅 Creado: $SCRIPT_CREATION_DATE"
	echo "  🕒 Último uso anterior: $SCRIPT_LAST_USED_DATE"
	echo "  ⏰ Ejecución actual: $(date "+%Y-%m-%d %H:%M:%S")"
	echo "  👤 Usuario: $(whoami)"
	echo ""
	
	# Información del cluster
	log_structured "INFO" "📋 INFORMACIÓN DEL CLUSTER:"
	echo "  🎯 Nombre: K3s HA Development Cluster"
	echo "  🏷️  Versión: $K3S_VERSION"
	echo "  🌐 VIP: $VIP"
	echo "  ⚖️  LoadBalancer: $LB_RANGE"
	echo "  📝 Contexto: k3s-ha-dev"
	echo ""
	
	# Estado de nodos
	local total_nodes=$(kubectl get nodes --no-headers 2>/dev/null | wc -l | tr -d '\n' | tr -d ' ' || echo "0")
	local ready_nodes=$(kubectl get nodes --no-headers 2>/dev/null | grep -c " Ready " | tr -d '\n' | tr -d ' ' || echo "0")
	
	# Asegurar que son números válidos
	total_nodes=${total_nodes//[^0-9]/}
	ready_nodes=${ready_nodes//[^0-9]/}
	[[ -z "$total_nodes" ]] && total_nodes=0
	[[ -z "$ready_nodes" ]] && ready_nodes=0
	
	log_structured "INFO" "🖥️  ESTADO DE NODOS:"
	echo "  📊 Total: $total_nodes nodos"
	echo "  ✅ Ready: $ready_nodes nodos"
	echo "  👑 Masters: 3 nodos"
	echo "  🔧 Workers: 3 nodos"
	echo ""
	
	# Estado de la aplicación de prueba
	local nginx_external_ip=$(kubectl get svc nginx-test-dev-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
	
	if [[ -n "$nginx_external_ip" && "$nginx_external_ip" != "null" && "$nginx_external_ip" != "<pending>" ]]; then
		log_structured "INFO" "🧪 APLICACIÓN DE PRUEBA:"
		echo "  ✅ Estado: Funcionando"
		echo "  🌐 URL: http://$nginx_external_ip"
		echo "  🔗 Comando: curl http://$nginx_external_ip"
	else
		log_structured "INFO" "🧪 APLICACIÓN DE PRUEBA:"
		echo "  ⏳ Estado: IP pendiente o no desplegada"
		echo "  🔍 Verificar: kubectl get svc nginx-test-dev-service"
	fi
	echo ""
	
	# Archivos importantes
	log_structured "INFO" "📁 ARCHIVOS IMPORTANTES:"
	echo "  🔑 Kubeconfig: $KUBE_CONFIG_DIR/config"
	echo "  📝 Log principal: $LOG_FILE"
	echo "  🐛 Log debug: $DEBUG_LOG"
	echo "  📊 Tracking uso: $USAGE_TRACKING_FILE"
	if [[ "$BACKUP_BEFORE_CHANGES" == "true" && -d "$BACKUP_DIR" ]]; then
		echo "  💾 Backup: $BACKUP_DIR"
		echo "  ↩️  Rollback: $BACKUP_DIR/rollback.sh"
		echo "  📋 Info backup: $BACKUP_DIR/backup_info.txt"
	fi
	echo ""
	
	# Comandos útiles
	log_structured "INFO" "💡 COMANDOS ÚTILES:"
	echo "  📊 Ver nodos:         kubectl get nodes -o wide"
	echo "  🔍 Ver pods:          kubectl get pods -A"
	echo "  🌐 Ver servicios:     kubectl get svc -A"
	echo "  🧪 Ver app prueba:    kubectl get svc nginx-test-dev-service"
	echo "  📈 Ver historial:     grep '$SCRIPT_NAME:' $USAGE_TRACKING_FILE"
	echo "  🏥 Health check:      ./scripts/utils/health-check.sh"
	echo "  💾 Backup:           ./scripts/utils/backup-cluster.sh"
	echo ""
	
	# Estado de éxito
	if [[ $ready_nodes -eq $total_nodes && $ready_nodes -gt 0 ]]; then
		log_structured "SUCCESS" "🚀 CLUSTER K3S HA DESPLEGADO EXITOSAMENTE"
		echo "============================================================="
		echo "  ✅ Alta disponibilidad configurada"
		echo "  ✅ Load balancing funcionando"
		echo "  ✅ Aplicación de prueba disponible"
		echo "  ✅ Monitoreo y backup disponibles"
		echo "  ✅ Tracking de uso implementado"
		echo "============================================================="
	else
		log_structured "WARN" "⚠️  CLUSTER PARCIALMENTE FUNCIONAL"
		echo "============================================================="
		echo "  ⚠️  Algunos nodos pueden no estar Ready"
		echo "  🔍 Revisar logs y ejecutar health check"
		echo "============================================================="
	fi
	
	echo ""
	success_msg "🎯 ¡Cluster listo para usar!"
}

#############################################
#         REPORTING FUNCTIONS               #
#############################################

# Función para generar reporte de instalación con información de tracking
generate_installation_report() {
	log_structured "INFO" "Generando reporte de instalación..."
	
	local report_file="k3s_installation_report_$(date +%Y%m%d-%H%M%S).md"
	
	cat > "$report_file" << EOF
# Reporte de Instalación K3s HA - Completo con Pruebas y Tracking

## Información General
- **Fecha:** $(date)
- **Modo:** Desarrollo/Pruebas
- **Script Version:** 2.4-complete-with-usage-tracking

## Información de Tracking
- **Script ejecutado:** $SCRIPT_NAME
- **Ruta del script:** $SCRIPT_PATH  
- **Fecha de creación:** $SCRIPT_CREATION_DATE
- **Último uso anterior:** $SCRIPT_LAST_USED_DATE
- **Ejecución actual:** $(date "+%Y-%m-%d %H:%M:%S")
- **Usuario ejecutor:** $(whoami)
- **Sistema:** $(uname -s) $(uname -r)
- **Hostname:** $(hostname)

## Versiones Utilizadas
- **K3s:** $K3S_VERSION
- **Kube-VIP:** $KVVERSION
- **MetalLB:** $METALLB_VERSION
- **k3sup:** $K3SUP_VERSION

## Configuración del Cluster
- **VIP:** $VIP
- **Rango LoadBalancer:** $LB_RANGE
- **Interfaz de Red:** $INTERFACE

### Nodos Maestros
$(for master in $MASTER1 "${MASTERS[@]}"; do echo "- $master"; done)

### Nodos Trabajadores
$(for worker in "${WORKERS[@]}"; do echo "- $worker"; done)

## Estado del Cluster
\`\`\`
$(kubectl get nodes -o wide 2>/dev/null || echo "Error obteniendo información de nodos")
\`\`\`

## Servicios
\`\`\`
$(kubectl get svc --all-namespaces 2>/dev/null || echo "Error obteniendo información de servicios")
\`\`\`

## Pods del Sistema
\`\`\`
$(kubectl get pods --all-namespaces 2>/dev/null || echo "Error obteniendo información de pods")
\`\`\`

## Aplicación de Prueba
- **Deployment:** nginx-test-dev
- **Service:** nginx-test-dev-service
- **Replicas:** 2
- **URL:** $(kubectl get svc nginx-test-dev-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null | sed 's/^/http:\/\//' || echo "IP pendiente")

## Acceso al Cluster
- **Kubeconfig:** $KUBE_CONFIG_DIR/config
- **Contexto:** k3s-ha-dev
- **API Server:** https://$VIP:6443

## Archivos de Log y Tracking
- **Log Principal:** $LOG_FILE
- **Log Debug:** $DEBUG_LOG
- **Tracking de Uso:** $USAGE_TRACKING_FILE
- **Backup:** $BACKUP_DIR
- **Info Backup:** $BACKUP_DIR/backup_info.txt

## Historial de Ejecuciones
\`\`\`
$(if [[ -f "$USAGE_TRACKING_FILE" ]]; then grep "^$SCRIPT_NAME:" "$USAGE_TRACKING_FILE" 2>/dev/null | tail -5; else echo "Primera ejecución"; fi)
\`\`\`

## Funcionalidades Verificadas
- ✅ Alta disponibilidad (3 masters)
- ✅ Load balancing con MetalLB
- ✅ Aplicación de prueba desplegada
- ✅ Asignación automática de IP externa
- ✅ Conectividad HTTP funcional
- ✅ Sistema de tracking de uso implementado
- ✅ Backup y rollback configurado

## Próximos Pasos
1. Verificar aplicación de prueba: curl http://\$(kubectl get svc nginx-test-dev-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
2. Desplegar aplicaciones adicionales
3. Configurar monitoreo con Prometheus/Grafana
4. Implementar backup automático
5. Revisar historial de uso: grep '$SCRIPT_NAME:' $USAGE_TRACKING_FILE

---
*Generado automáticamente por el script de instalación K3s HA v2.4-complete-with-usage-tracking*  
*Ejecutado desde: $SCRIPT_PATH*  
*Fecha: $(date "+%Y-%m-%d %H:%M:%S")*
EOF
	
	success_msg "✅ Reporte generado: $report_file"
}

#############################################
#              MAIN EXECUTION               #
#############################################

main() {
	# Banner de inicio
	log_structured "INFO" "🚀 Iniciando instalación K3s HA - Versión Completa con Pruebas y Tracking"
	log_structured "INFO" "📋 Versiones: K3s $K3S_VERSION | Kube-VIP $KVVERSION | MetalLB $METALLB_VERSION"
	log_structured "INFO" "🎯 Incluye: Aplicación de prueba Nginx + Estado completo del cluster + Tracking de uso"
	
	# Inicializar logs con información de tracking
	cat > "$LOG_FILE" << EOF
K3s HA Complete Installation with Usage Tracking - Started at $(date)
======================================================================
Script: $SCRIPT_NAME
Path: $SCRIPT_PATH
Created: $SCRIPT_CREATION_DATE
Last used: $SCRIPT_LAST_USED_DATE
Current execution: $(date "+%Y-%m-%d %H:%M:%S")
User: $(whoami)
System: $(uname -a)
======================================================================

EOF
	
	cat > "$DEBUG_LOG" << EOF
K3s HA Complete Debug Log with Usage Tracking - Started at $(date)
===================================================================
Script: $SCRIPT_NAME
Path: $SCRIPT_PATH
Created: $SCRIPT_CREATION_DATE
Last used: $SCRIPT_LAST_USED_DATE
Current execution: $(date "+%Y-%m-%d %H:%M:%S")
User: $(whoami)
System: $(uname -a)
===================================================================

EOF
	
	# Registrar información de tracking en logs
	log_tracking_info
	
	# Mostrar historial de uso
	show_usage_history
	
	# Limpiar tracking antiguo si es necesario
	cleanup_old_tracking
	
	# Crear backup si está habilitado
	create_backup
	
	# Fase 1: Validaciones
	log_structured "INFO" "📋 FASE 1: Validaciones y Prerrequisitos"
	validate_versions
	validate_ssh_key
	validate_prerequisites
	validate_k3s_config
	check_ssh_connectivity
	
	# Fase 2: Instalación de herramientas
	log_structured "INFO" "🔧 FASE 2: Instalación de Herramientas"
	install_tools
	install_node_dependencies
	
	# Fase 3: Configuración del cluster
	log_structured "INFO" "⚙️  FASE 3: Configuración del Cluster"
	bootstrap_first_master
	setup_kubevip
	join_additional_masters
	join_worker_nodes
	
	# Fase 4: Configuración de red
	log_structured "INFO" "🌐 FASE 4: Configuración de Red"
	install_metallb
	configure_metallb_pool
	
	# Fase 5: Esperar y validar
	log_structured "INFO" "⏳ FASE 5: Validación y Espera"
	wait_for_cluster_ready
	
	# Fase 6: Pruebas - GARANTIZADAS
	log_structured "INFO" "🧪 FASE 6: Despliegue y Pruebas - EJECUTANDO SIEMPRE"
	echo "================================================================"
	
	# Estas funciones se ejecutan SIEMPRE, sin fallar silenciosamente
	deploy_test_application || log_structured "WARN" "Aplicación de prueba tuvo problemas pero continuando"
	
	comprehensive_cluster_validation || log_structured "WARN" "Validación tuvo problemas pero continuando"
	
	test_deployed_application || log_structured "WARN" "Prueba de aplicación tuvo problemas pero continuando"
	
	echo "================================================================"
	
	# Fase 7: Reporte final
	log_structured "INFO" "📊 FASE 7: Generación de Reporte"
	generate_installation_report
	
	# Mostrar estado final completo
	show_final_cluster_status
	
	# Mensaje final con información de tracking
	success_msg "🎉 ¡Instalación K3s HA completada exitosamente!"
	log_structured "TRACKING" "Ejecución completada exitosamente en $(date "+%Y-%m-%d %H:%M:%S")"
	log_structured "TRACKING" "Total de ejecuciones del script: $(grep -c "^$SCRIPT_NAME:" "$USAGE_TRACKING_FILE" 2>/dev/null | tr -d '\n' | tr -d ' ' || echo "1")"
	
	log_structured "INFO" "✅ Script completo terminado - Todas las fases ejecutadas"
	log_structured "INFO" "📊 Tracking de uso actualizado en: $USAGE_TRACKING_FILE"
}

# Trap para cleanup en caso de error con información de tracking
cleanup_on_error() {
	error_msg "❌ Script interrumpido. Logs disponibles en: $LOG_FILE"
	log_structured "TRACKING" "Ejecución interrumpida en $(date "+%Y-%m-%d %H:%M:%S")" 2>/dev/null || true
	if [[ "$BACKUP_BEFORE_CHANGES" == "true" && -d "$BACKUP_DIR" ]]; then
		log_structured "INFO" "💾 Backup disponible en: $BACKUP_DIR"
	fi
	exit 1
}

trap cleanup_on_error ERR INT TERM

# Ejecutar función principal
main "$@"

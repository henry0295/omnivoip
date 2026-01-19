#!/bin/bash
# =============================================================================
# OmniVoIP Automated Deployment Script
# =============================================================================
# Description: Automated deployment for VPS/Cloud environments
# Usage:       export HOST_IP=x.x.x.x && ./deploy.sh
#              export DOMAIN=your-domain.com && ./deploy.sh
# =============================================================================

set -Eeu
IFS=$'\n\t'

# -----------------------------------------------------------------------------
# Logging & Error Handling
# -----------------------------------------------------------------------------
log_info()  { echo -e "\033[0;32m[INFO]\033[0m $1"; }
log_warn()  { echo -e "\033[0;33m[WARN]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1" >&2; exit 1; }

on_error() {
    local code=$?
    echo -e "\033[0;31m[ERROR]\033[0m Failed at line $LINENO. Check logs above." >&2
    exit 1
}
trap on_error ERR

# Require root
if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
    log_error "This script must be run as root (use sudo)"
fi

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
PROJECT_NAME="omnivoip"
REPO_URL="https://github.com/henry0295/omnivoip.git"
INSTALL_DIR="/opt/$PROJECT_NAME"

# Network interface (adjust if needed)
NIC=${NIC:-eth0}

# Input variables (can be set via environment)
HOST_IP=${HOST_IP:-}
PUBLIC_IP=${PUBLIC_IP:-}
NAT_IPV4=${NAT_IPV4:-}
DOMAIN=${DOMAIN:-}

# -----------------------------------------------------------------------------
# Detect Operating System
# -----------------------------------------------------------------------------
detect_os() {
    log_info "Detecting operating system..."
    
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS_ID=$ID
        OS_VERSION=$VERSION_ID
        log_info "Detected: $ID $VERSION_ID"
    else
        log_error "Cannot determine operating system"
    fi
}

# -----------------------------------------------------------------------------
# Install Docker
# -----------------------------------------------------------------------------
install_docker() {
    if command -v docker &>/dev/null; then
        log_info "Docker already installed: $(docker --version)"
        return
    fi
    
    log_info "Installing Docker..."
    
    if [[ "$OS_ID" =~ (debian|ubuntu) ]]; then
        # Debian/Ubuntu
        apt-get update -y
        apt-get install -y ca-certificates curl gnupg lsb-release
        
        # Add Docker's official GPG key
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/$OS_ID/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        chmod a+r /etc/apt/keyrings/docker.gpg
        
        # Set up repository
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS_ID \
          $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Install Docker Engine
        apt-get update -y
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
    elif [[ "$OS_ID" =~ (rhel|centos|almalinux|rocky) ]]; then
        # RHEL/CentOS/AlmaLinux/Rocky
        dnf -y check-update || true
        dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
        systemctl enable docker
        systemctl start docker
        
    else
        log_error "Unsupported OS: $OS_ID"
    fi
    
    # Verify installation
    docker --version || log_error "Docker installation failed"
    
    # Enable and start
    systemctl enable docker 2>/dev/null || true
    systemctl start docker
    
    log_info "Docker installed successfully"
}

# -----------------------------------------------------------------------------
# Install Dependencies
# -----------------------------------------------------------------------------
install_dependencies() {
    log_info "Installing dependencies..."
    
    if [[ "$OS_ID" =~ (debian|ubuntu) ]]; then
        apt-get install -y git curl jq openssl net-tools
    elif [[ "$OS_ID" =~ (rhel|centos|almalinux|rocky) ]]; then
        dnf install -y git curl jq openssl net-tools
    fi
    
    log_info "Dependencies installed"
}

# -----------------------------------------------------------------------------
# Disable Firewalls (UFW/firewalld)
# -----------------------------------------------------------------------------
disable_firewalls() {
    log_info "Checking and disabling OS firewalls..."
    
    # UFW (Debian/Ubuntu)
    if command -v ufw &>/dev/null; then
        systemctl stop ufw 2>/dev/null || true
        systemctl disable ufw 2>/dev/null || true
        ufw disable 2>/dev/null || true
        log_info "UFW disabled"
    fi
    
    # FirewallD (RHEL/CentOS)
    if command -v firewall-cmd &>/dev/null; then
        systemctl stop firewalld 2>/dev/null || true
        systemctl disable firewalld 2>/dev/null || true
        log_info "FirewallD disabled"
    fi
    
    log_warn "OS firewall disabled. Use cloud firewall or configure manually."
}

# -----------------------------------------------------------------------------
# Get Network Configuration
# -----------------------------------------------------------------------------
setup_networking() {
    log_info "Configuring network settings..."
    
    # Get host IP
    if [[ -z "${HOST_IP:-}" ]]; then
        HOST_IP=$(ip -4 addr show "$NIC" 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -1 || true)
        
        # Fallback: get first non-localhost IP
        if [[ -z "$HOST_IP" ]]; then
            HOST_IP=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -1 || true)
        fi
    fi
    
    [[ -z "$HOST_IP" ]] && log_error "Could not determine host IP address"
    
    # Get public IP
    if [[ -z "${PUBLIC_IP:-}" ]]; then
        PUBLIC_IP=$(curl -fsS --max-time 5 https://api.ipify.org 2>/dev/null || true)
        [[ -z "$PUBLIC_IP" ]] && PUBLIC_IP=$(curl -fsS --max-time 5 https://ifconfig.me 2>/dev/null || true)
        [[ -z "$PUBLIC_IP" ]] && PUBLIC_IP=$(curl -fsS --max-time 5 https://ipinfo.io/ip 2>/dev/null || true)
        [[ -z "$PUBLIC_IP" ]] && PUBLIC_IP="$HOST_IP"
    fi
    
    # Prompt for domain if not set
    if [[ -z "${DOMAIN:-}" ]]; then
        # Check if running interactively
        if [[ -t 0 ]]; then
            # Interactive mode - can read from user
            echo ""
            echo "=========================================="
            echo "  Domain Configuration"
            echo "=========================================="
            echo ""
            echo "Enter your domain name (e.g., omnivoip.example.com)"
            echo "Press ENTER to use IP address: $PUBLIC_IP"
            echo ""
            read -p "Domain [default: $PUBLIC_IP]: " DOMAIN || true
            
            # Use public IP if no domain provided
            if [[ -z "$DOMAIN" ]]; then
                DOMAIN="$PUBLIC_IP"
                log_warn "No domain provided, using IP: $DOMAIN"
            fi
        else
            # Non-interactive mode (piped from curl) - use default
            DOMAIN="$PUBLIC_IP"
            log_info "Non-interactive mode detected, using IP: $DOMAIN"
            log_info "To set custom domain, use: export DOMAIN=your-domain.com before running"
        fi
    fi
    
    log_info "Host IP: $HOST_IP"
    log_info "Public IP: $PUBLIC_IP"
    [[ -n "${NAT_IPV4:-}" ]] && log_info "NAT IP: $NAT_IPV4"
    log_info "Domain/Access URL: $DOMAIN"
}

# -----------------------------------------------------------------------------
# Clone or Update Repository
# -----------------------------------------------------------------------------
clone_repository() {
    log_info "Setting up repository..."
    
    if [[ -d "$INSTALL_DIR/.git" ]]; then
        log_info "Repository exists, updating..."
        cd "$INSTALL_DIR"
        git fetch --all --prune
        git reset --hard origin/main
    else
        log_info "Cloning repository..."
        git clone --depth=1 "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi
    
    # Initialize submodules if they exist
    if [[ -f .gitmodules ]]; then
        log_info "Initializing submodules..."
        git submodule update --init --depth=1 --recursive
    fi
}

# -----------------------------------------------------------------------------
# Configure Environment
# -----------------------------------------------------------------------------
setup_environment() {
    log_info "Configuring environment..."
    
    cd "$INSTALL_DIR/docker-compose/prod-env"
    
    # Copy manage script
    if [[ -f ../scripts/manage.sh ]]; then
        cp ../scripts/manage.sh ./
        chmod +x manage.sh
    fi
    
    # Setup .env file
    if [[ ! -f .env ]]; then
        log_info "Creating .env file from template..."
        if [[ -f ../env.template ]]; then
            cp ../env.template .env
        else
            log_error "Template file ../env.template not found!"
        fi
    else
        log_warn ".env already exists, backing up to .env.backup"
        cp .env .env.backup
    fi
    
    # Verify .env exists
    if [[ ! -f .env ]]; then
        log_error ".env file could not be created"
    fi
    
    # Configure IPs (use || true to avoid errors if pattern not found)
    sed -i "s|^OML_HOSTNAME=.*|OML_HOSTNAME=${HOST_IP}|" .env || echo "OML_HOSTNAME=${HOST_IP}" >> .env
    sed -i "s|^PUBLIC_IP=.*|PUBLIC_IP=${PUBLIC_IP}|" .env || echo "PUBLIC_IP=${PUBLIC_IP}" >> .env
    
    # Configure domain if provided
    if [[ -n "${DOMAIN:-}" ]]; then
        sed -i "s|^FQDN=.*|FQDN=${DOMAIN}|" .env || echo "FQDN=${DOMAIN}" >> .env
    fi
    
    # Configure NAT if provided
    if [[ -n "${NAT_IPV4:-}" ]]; then
        sed -i "s|^VOIP_NAT=.*|VOIP_NAT=true|" .env || echo "VOIP_NAT=true" >> .env
        sed -i "s|^#\?SIP_NAT_IPADDR=.*|SIP_NAT_IPADDR=${NAT_IPV4}|" .env || echo "SIP_NAT_IPADDR=${NAT_IPV4}" >> .env
        sed -i "s|^#\?RTP_NAT_IPADDR=.*|RTP_NAT_IPADDR=${NAT_IPV4}|" .env || echo "RTP_NAT_IPADDR=${NAT_IPV4}" >> .env
    fi
    
    # Generate secure passwords
    log_info "Generating secure passwords..."
    
    POSTGRES_PASS=$(openssl rand -hex 16)
    REDIS_PASS=$(openssl rand -hex 16)
    MINIO_PASS=$(openssl rand -hex 16)
    DJANGO_SECRET=$(openssl rand -hex 32)
    
    # Use grep and append to safely update .env
    grep -q "^POSTGRES_PASSWORD=" .env && sed -i "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${POSTGRES_PASS}|" .env || echo "POSTGRES_PASSWORD=${POSTGRES_PASS}" >> .env
    grep -q "^REDIS_PASSWORD=" .env && sed -i "s|^REDIS_PASSWORD=.*|REDIS_PASSWORD=${REDIS_PASS}|" .env || echo "REDIS_PASSWORD=${REDIS_PASS}" >> .env
    grep -q "^MINIO_HTTP_ADMIN_PASS=" .env && sed -i "s|^MINIO_HTTP_ADMIN_PASS=.*|MINIO_HTTP_ADMIN_PASS=${MINIO_PASS}|" .env || echo "MINIO_HTTP_ADMIN_PASS=${MINIO_PASS}" >> .env
    grep -q "^DJANGO_SECRET_KEY=" .env && sed -i "s|^DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=${DJANGO_SECRET}|" .env || echo "DJANGO_SECRET_KEY=${DJANGO_SECRET}" >> .env
    
    log_info "Environment configured"
}

# -----------------------------------------------------------------------------
# Generate SSL Certificates
# -----------------------------------------------------------------------------
generate_certificates() {
    log_info "Generating SSL certificates..."
    
    local CERT_DIR="$INSTALL_DIR/docker-compose/certs"
    mkdir -p "$CERT_DIR"
    
    if [[ ! -f "$CERT_DIR/certificate.pem" ]]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$CERT_DIR/private.key" \
            -out "$CERT_DIR/certificate.pem" \
            -subj "/C=US/ST=State/L=City/O=OmniVoIP/CN=${DOMAIN:-$HOST_IP}"
        
        log_warn "Self-signed certificate generated. Replace with proper SSL cert for production!"
    else
        log_info "SSL certificates already exist"
    fi
}

# -----------------------------------------------------------------------------
# Deploy Services
# -----------------------------------------------------------------------------
deploy_services() {
    log_info "Deploying OmniVoIP services..."
    
    cd "$INSTALL_DIR/docker-compose/prod-env"
    
    # Validate docker-compose.yml for problematic configurations
    log_info "Validating docker-compose.yml..."
    
    local validation_failed=0
    
    # Check for userns_mode: "host"
    if grep -q '^[[:space:]]*userns_mode:[[:space:]]*"host"' docker-compose.yml 2>/dev/null; then
        log_error "Found active 'userns_mode: \"host\"' in docker-compose.yml. This causes deployment failures."
        validation_failed=1
    fi
    
    # Check for network_mode: host on asterisk with cap_add
    if grep -A20 "container_name:.*asterisk" docker-compose.yml | grep -q '^[[:space:]]*network_mode:[[:space:]]*host'; then
        log_error "Found 'network_mode: host' on asterisk service. This causes sysctl permission errors."
        validation_failed=1
    fi
    
    if [[ $validation_failed -eq 1 ]]; then
        log_error "Docker compose validation failed. Please run './fix-userns-mode.sh' to fix these issues."
        exit 1
    fi
    
    log_info "Validation passed!"
    
    # Configure system sysctls for Docker networking
    log_info "Configuring system networking parameters..."
    
    # Try to set sysctl parameters (may fail in some environments)
    if sysctl -w net.ipv4.ip_forward=1 2>/dev/null; then
        log_info "IP forwarding enabled"
    else
        log_warn "Could not enable IP forwarding (may not be needed)"
    fi
    
    # Create sysctl config file for persistence
    cat > /etc/sysctl.d/99-omnivoip-docker.conf <<EOF || true
# OmniVoIP Docker networking configuration
net.ipv4.ip_forward=1
net.bridge.bridge-nf-call-iptables=1
net.bridge.bridge-nf-call-ip6tables=1
EOF
    
    # Apply settings (non-blocking)
    sysctl -p /etc/sysctl.d/99-omnivoip-docker.conf 2>/dev/null || log_warn "Some sysctl settings could not be applied (continuing anyway)"
    
    # Clean Docker cache to ensure fresh builds
    log_info "Cleaning Docker cache..."
    docker system prune -af --volumes || log_warn "Failed to clean Docker cache"
    
    # Build custom images first (don't pull non-existent images)
    log_info "Building Docker images (this may take 10-15 minutes)..."
    docker compose build --no-cache || log_error "Docker build failed"
    
    # Start services (will pull missing base images automatically)
    log_info "Starting services..."
    docker compose up -d || log_error "Failed to start services"
    
    # Wait for services to be ready
    log_info "Waiting for services to initialize (60s)..."
    sleep 60
    
    # Run migrations
    log_info "Running database migrations..."
    docker compose exec -T django-app python manage.py migrate || log_warn "Migrations failed, may need manual intervention"
    
    # Create superuser
    log_info "Setting up admin user..."
    ./manage.sh reset-pass
}

# -----------------------------------------------------------------------------
# Display Completion Info
# -----------------------------------------------------------------------------
show_completion() {
    log_info "===================================================================="
    log_info "              OmniVoIP Deployment Completed!                       "
    log_info "===================================================================="
    echo
    log_info "Access your Contact Center at:"
    log_info "  https://${DOMAIN:-$HOST_IP}"
    echo
    log_info "Default login credentials:"
    log_info "  Username: admin"
    log_info "  Password: admin"
    echo
    log_warn "IMPORTANT: Change the admin password immediately!"
    echo
    log_info "Management commands:"
    log_info "  cd $INSTALL_DIR/docker-compose/prod-env"
    log_info "  ./manage.sh status    # View service status"
    log_info "  ./manage.sh logs -f   # Follow logs"
    log_info "  ./manage.sh help      # See all commands"
    echo
    log_info "Services configuration saved in:"
    log_info "  $INSTALL_DIR/docker-compose/prod-env/.env"
    log_info "===================================================================="
}

# -----------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------
main() {
    log_info "Starting OmniVoIP deployment..."
    
    detect_os
    install_dependencies
    install_docker
    disable_firewalls
    setup_networking
    clone_repository
    setup_environment
    generate_certificates
    deploy_services
    show_completion
}

# Execute
main "$@"

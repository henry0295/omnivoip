#!/bin/bash
# =============================================================================
# OmniVoIP One-Command Deployment
# =============================================================================
# Description: Deploy or update OmniVoIP with automatic validation and fixes
# Usage:       sudo ./quick-deploy.sh
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root (use sudo)"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "========================================"
echo "  OmniVoIP Quick Deployment"
echo "========================================"
echo ""

# Step 1: Validate docker-compose.yml
log_step "1/6 Validating docker-compose.yml"
if [[ -f "./validate-config.sh" ]]; then
    chmod +x validate-config.sh
    if ./validate-config.sh 2>&1 | grep -q "CRITICAL ISSUES"; then
        log_warn "Configuration issues detected, attempting auto-fix..."
        
        if [[ -f "./fix-userns-mode.sh" ]]; then
            chmod +x fix-userns-mode.sh
            ./fix-userns-mode.sh || log_error "Auto-fix failed"
            log_info "Configuration fixed successfully"
        else
            log_error "fix-userns-mode.sh not found"
        fi
    fi
else
    log_warn "validate-config.sh not found, skipping validation"
fi

# Step 2: Check .env file
log_step "2/6 Checking environment configuration"
if [[ ! -f ".env" ]]; then
    log_warn ".env not found, creating from template"
    if [[ -f "../env.template" ]]; then
        cp ../env.template .env
        log_info "Created .env from template"
        log_warn "IMPORTANT: Edit .env and configure your passwords!"
        log_warn "Run: nano .env"
        read -p "Press ENTER after configuring .env (or Ctrl+C to abort)..." 
    else
        log_error "../env.template not found"
    fi
else
    log_info ".env file exists"
fi

# Step 3: Check Docker
log_step "3/6 Checking Docker installation"
if ! command -v docker &> /dev/null; then
    log_error "Docker not installed. Run: curl -fsSL https://get.docker.com | sh"
fi

if ! command -v docker compose &> /dev/null; then
    log_error "Docker Compose not installed"
fi

log_info "Docker $(docker --version | awk '{print $3}') detected"
log_info "Docker Compose $(docker compose version --short) detected"

# Step 4: Pull/Build images
log_step "4/6 Building Docker images"
log_info "This may take 10-15 minutes on first run..."

docker compose build --no-cache 2>&1 | tee build.log || {
    log_error "Docker build failed. Check build.log for details"
}

log_info "Build completed successfully"

# Step 5: Start services
log_step "5/6 Starting services"

# Stop any running services first
docker compose down 2>/dev/null || true

# Start services
docker compose up -d || log_error "Failed to start services"

log_info "Services started"

# Step 6: Wait and verify
log_step "6/6 Verifying deployment"

log_info "Waiting 30 seconds for services to initialize..."
sleep 30

# Check service status
FAILED_SERVICES=$(docker compose ps --format json | jq -r 'select(.State != "running") | .Service' 2>/dev/null || echo "")

if [[ -z "$FAILED_SERVICES" ]]; then
    log_info "All services are running!"
else
    log_warn "Some services are not running:"
    echo "$FAILED_SERVICES"
    log_warn "Check logs: docker compose logs"
fi

# Get access URL
if [[ -f ".env" ]]; then
    FQDN=$(grep "^FQDN=" .env | cut -d'=' -f2)
    PUBLIC_IP=$(grep "^PUBLIC_IP=" .env | cut -d'=' -f2)
    ACCESS_URL="${FQDN:-$PUBLIC_IP}"
else
    ACCESS_URL="your-server-ip"
fi

echo ""
echo "========================================"
echo "  Deployment Complete!"
echo "========================================"
echo ""
log_info "Access OmniVoIP at:"
echo ""
echo "  🌐 https://${ACCESS_URL}"
echo ""
log_info "Default credentials:"
echo "  👤 Username: admin"
echo "  🔑 Password: admin"
echo ""
log_warn "IMPORTANT: Change the admin password immediately!"
echo ""
log_info "Useful commands:"
echo "  View status:  docker compose ps"
echo "  View logs:    docker compose logs -f"
echo "  Restart all:  docker compose restart"
echo "  Stop all:     docker compose down"
echo ""
log_info "Full documentation: ../../DEPLOYMENT.md"
echo ""

# Show running services
echo "Running services:"
docker compose ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}"
echo ""

log_info "Deployment completed successfully! 🎉"

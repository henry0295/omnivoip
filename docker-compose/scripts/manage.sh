#!/usr/bin/env bash
# =============================================================================
# OmniVoIP Stack Management Script
# =============================================================================
# Description: Manage the entire OmniVoIP Docker-based stack
# Usage:       ./manage.sh <command> [arguments]
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Color Configuration
# -----------------------------------------------------------------------------
RED=''; GREEN=''; YELLOW=''; BLUE=''; PURPLE=''; CYAN=''; BOLD=''; NC=''

setup_colors() {
    if [[ -t 1 ]] && command -v tput &>/dev/null && [[ "$(tput colors)" -ge 8 ]]; then
        RED="$(tput setaf 1)";   GREEN="$(tput setaf 2)";  YELLOW="$(tput setaf 3)"
        BLUE="$(tput setaf 4)";  PURPLE="$(tput setaf 5)"; CYAN="$(tput setaf 6)"
        BOLD="$(tput bold)";     NC="$(tput sgr0)"
    fi
}

# -----------------------------------------------------------------------------
# Logging Helpers
# -----------------------------------------------------------------------------
log()     { echo -e "${BOLD}[$(date +'%H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}✔ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
error()   { echo -e "${RED}✖ $1${NC}" >&2; }
info()    { echo -e "${CYAN}ℹ $1${NC}"; }

# -----------------------------------------------------------------------------
# Global Variables
# -----------------------------------------------------------------------------
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
PROJECT_NAME=$(grep -E '^PROJECT_NAME=' "$ENV_FILE" 2>/dev/null | cut -d= -f2 || echo "omnivoip")

DC_CMD=()
DEPENDENCIES=(docker jq)

# -----------------------------------------------------------------------------
# Dependency and File Checks
# -----------------------------------------------------------------------------
check_dependencies() {
    local missing=()
    for dep in "${DEPENDENCIES[@]}"; do
        if ! command -v "$dep" &>/dev/null; then
            missing+=("$dep")
        fi
    done
    if (( ${#missing[@]} )); then
        error "Missing dependencies: ${missing[*]}"
        exit 1
    fi

    # Choose compose command
    if docker compose version &>/dev/null 2>&1; then
        DC_CMD=(docker compose)
    elif command -v docker-compose &>/dev/null; then
        DC_CMD=(docker-compose)
    else
        error "Neither 'docker compose' nor 'docker-compose' found"
        exit 1
    fi
}

check_required_files() {
    [[ -f "$COMPOSE_FILE" ]] || { error "Cannot find $COMPOSE_FILE"; exit 1; }
    [[ -f "$ENV_FILE" ]] || { warning "$ENV_FILE not found — copying from template"; cp ../env.template .env; }
}

docker_compose() {
    "${DC_CMD[@]}" --project-name "$PROJECT_NAME" "$@"
}

# -----------------------------------------------------------------------------
# Enhanced Health Check
# -----------------------------------------------------------------------------
check_health() {
    info "Checking health of critical services..."
    local critical=(postgresql redis minio django-app asterisk nginx)
    local unhealthy=()

    for svc in "${critical[@]}"; do
        local cid status health
        cid=$(docker_compose ps -q "$svc" 2>/dev/null || echo "")
        if [[ -n "$cid" ]]; then
            status=$(docker inspect --format '{{.State.Status}}' "$cid" 2>/dev/null || echo "unknown")
            health=$(docker inspect --format '{{.State.Health.Status}}' "$cid" 2>/dev/null || echo "none")
            printf "  %-15s " "$svc:"
            case "$status/$health" in
                running/healthy)   echo -e "${GREEN}✔ healthy${NC}" ;;
                running/unhealthy) echo -e "${RED}✖ unhealthy${NC}"; unhealthy+=("$svc") ;;
                running/*)         echo -e "${YELLOW}● running${NC}" ;;
                exited/*)          echo -e "${PURPLE}◯ stopped${NC}"; unhealthy+=("$svc") ;;
                *)                 echo -e "${RED}? $status${NC}"; unhealthy+=("$svc") ;;
            esac
        else
            printf "  %-15s ${RED}✖ not found${NC}\n" "$svc"
            unhealthy+=("$svc")
        fi
    done

    if (( ${#unhealthy[@]} )); then
        error "Issues detected in: ${unhealthy[*]}"
        return 1
    else
        success "All critical services are healthy"
    fi
}

# -----------------------------------------------------------------------------
# Show Stack Status
# -----------------------------------------------------------------------------
show_status() {
    echo
    info "Container Status:"
    docker_compose ps --format table || docker_compose ps

    echo
    info "Resource Usage:"
    local containers
    mapfile -t containers < <(
        docker ps --filter "label=com.docker.compose.project=$PROJECT_NAME" --format "{{.Names}}"
    )
    if (( ${#containers[@]} )); then
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" "${containers[@]}"
    else
        warning "No running containers for project '$PROJECT_NAME'"
    fi
}

# -----------------------------------------------------------------------------
# Database Operations
# -----------------------------------------------------------------------------
db_migrate() {
    log "Running database migrations..."
    docker_compose exec -T django-app python manage.py migrate --noinput
    success "Migrations completed"
}

db_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="backup_${timestamp}.sql"
    
    log "Backing up database to $backup_file..."
    docker_compose exec -T postgresql pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$backup_file"
    success "Backup saved: $backup_file"
}

db_restore() {
    [[ -z "${1:-}" ]] && { error "Usage: $0 restore <backup_file>"; exit 1; }
    [[ ! -f "$1" ]] && { error "Backup file not found: $1"; exit 1; }
    
    log "Restoring database from $1..."
    docker_compose exec -T postgresql psql -U "$POSTGRES_USER" "$POSTGRES_DB" < "$1"
    success "Database restored"
}

# -----------------------------------------------------------------------------
# Admin Operations
# -----------------------------------------------------------------------------
reset_admin_password() {
    log "Resetting admin password to 'admin'..."
    docker_compose exec -T django-app python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin')
    admin.save()
    print("Admin password reset successfully")
except User.DoesNotExist:
    admin = User.objects.create_superuser('admin', 'admin@omnivoip.com', 'admin')
    print("Admin user created")
EOF
    success "Admin password is now 'admin'"
}

create_superuser() {
    log "Creating superuser..."
    docker_compose exec django-app python manage.py createsuperuser
}

# -----------------------------------------------------------------------------
# Data Generation
# -----------------------------------------------------------------------------
generate_data() {
    log "Generating test data..."
    docker_compose exec -T django-app python manage.py loaddata initial_data
    success "Test data generated"
}

# -----------------------------------------------------------------------------
# Cleanup Routines
# -----------------------------------------------------------------------------
clean_system() {
    log "Pruning stopped containers..."; docker container prune -f
    log "Pruning unused images...";     docker image prune -f
    log "Pruning unused volumes...";    docker volume prune -f
    log "Pruning unused networks...";   docker network prune -f
    success "Basic cleanup completed"
}

clean_all() {
    warning "This will remove ALL containers, images, volumes, and networks."
    read -rp "Continue? (y/N): " ans
    if [[ "$ans" =~ ^[Yy]$ ]]; then
        docker system prune -a -f --volumes
        success "Full system cleanup done"
    else
        info "Cleanup canceled"
    fi
}

# -----------------------------------------------------------------------------
# Service Operations
# -----------------------------------------------------------------------------
rebuild_services() {
    if [[ -n "${1:-}" ]]; then
        log "Rebuilding image for $1..."
        docker_compose build "$1"
        docker_compose up -d "$1"
        success "Service '$1' rebuilt and restarted"
    else
        log "Rebuilding all images..."
        docker_compose build
        success "All images rebuilt"
    fi
}

shell_service() {
    local service=${1:-django-app}
    log "Opening shell in $service..."
    docker_compose exec "$service" /bin/bash || docker_compose exec "$service" /bin/sh
}

# -----------------------------------------------------------------------------
# Display Help
# -----------------------------------------------------------------------------
show_help() {
    cat <<-EOF

    OmniVoIP Stack Management Script

    Usage: ./manage.sh <command> [arguments]

    Service Management:
      start [svc]         Start all or specific service
      stop [svc]          Stop all or specific service
      restart [svc]       Restart all or specific service
      down [-v]           Stop and remove containers (use -v to remove volumes)
      pull [svc]          Pull images (all or specific service)
      build [svc]         Build images
      rebuild [svc]       Rebuild and restart service
      
    Monitoring:
      status              Show container status and resource usage
      health              Perform health check of critical services
      logs [-f] [svc]     Show or follow logs
      
    Database:
      db-migrate          Run database migrations
      db-backup           Backup PostgreSQL database
      db-restore <file>   Restore database from backup
      
    Admin:
      reset-pass          Reset admin password to 'admin'
      create-superuser    Create new superuser interactively
      data-generate       Generate test data
      
    Utilities:
      shell [svc]         Open bash shell in service (default: django-app)
      exec <svc> <cmd>    Execute command in service
      clean               Prune stopped containers, unused images/volumes/networks
      clean-all           Full system prune (including volumes)
      
    Information:
      env                 Display environment variables from .env
      version             Show Docker & Compose versions
      help                Display this help message

    Examples:
      ./manage.sh start
      ./manage.sh logs -f django-app
      ./manage.sh db-backup
      ./manage.sh shell asterisk
      ./manage.sh exec django-app python manage.py shell

EOF
}

# -----------------------------------------------------------------------------
# Main Control Flow
# -----------------------------------------------------------------------------
main() {
    setup_colors
    check_dependencies
    check_required_files

    case "${1:-}" in
        start)            shift; log "Starting services..."; docker_compose up -d "$@" ;;
        stop)             shift; log "Stopping services..."; docker_compose stop "$@" ;;
        restart)          shift; log "Restarting services..."; docker_compose restart "$@" ;;
        down)             shift; log "Stopping stack..."; docker_compose down "$@" ;;
        pull)             shift; log "Pulling images..."; docker_compose pull "$@" ;;
        build)            shift; log "Building images..."; docker_compose build "$@" ;;
        rebuild)          shift; rebuild_services "${1:-}" ;;
        logs)             shift; docker_compose logs "$@" ;;
        status)           show_status ;;
        health)           check_health ;;
        db-migrate)       db_migrate ;;
        db-backup)        db_backup ;;
        db-restore)       shift; db_restore "$1" ;;
        reset-pass)       reset_admin_password ;;
        create-superuser) create_superuser ;;
        data-generate)    generate_data ;;
        shell)            shift; shell_service "${1:-}" ;;
        exec)             shift; docker_compose exec "$@" ;;
        clean)            clean_system ;;
        clean-all)        clean_all ;;
        env)              [[ -f "$ENV_FILE" ]] && cat "$ENV_FILE" || warning ".env not found" ;;
        version)          echo "Docker: $(docker --version)"; echo "Compose: $(${DC_CMD[@]} version)" ;;
        help|--help|"")   show_help ;;
        *)                error "Unknown command: $1"; show_help; exit 1 ;;
    esac
}

# -----------------------------------------------------------------------------
# Trap for Interrupt
# -----------------------------------------------------------------------------
trap 'echo; warning "Operation interrupted"; exit 130' INT

# Execute Main
main "$@"

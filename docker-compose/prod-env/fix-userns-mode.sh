#!/bin/bash
# =============================================================================
# Fix Docker Privilege Issues - OmniVoIP
# =============================================================================
# Description: Automatically fixes ALL privilege-related issues in docker-compose.yml
# Usage:       ./fix-userns-mode.sh
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

echo "========================================"
echo "  OmniVoIP Docker Fix Utility"
echo "========================================"
echo ""

# Check if docker-compose.yml exists
if [[ ! -f "$COMPOSE_FILE" ]]; then
    echo "ERROR: docker-compose.yml not found at: $COMPOSE_FILE"
    exit 1
fi

# Create backup
BACKUP_FILE="${COMPOSE_FILE}.backup-$(date +%Y%m%d-%H%M%S)"
echo "[INFO] Creating backup: $(basename $BACKUP_FILE)"
cp "$COMPOSE_FILE" "$BACKUP_FILE"

ISSUES_FOUND=0

# Check 1: userns_mode: "host"
USERNS_COUNT=$(grep -c '^[[:space:]]*userns_mode:[[:space:]]*"host"' "$COMPOSE_FILE" 2>/dev/null || true)
if [[ $USERNS_COUNT -gt 0 ]]; then
    echo "[WARN] Found $USERNS_COUNT instance(s) of 'userns_mode: \"host\"'"
    ISSUES_FOUND=1
fi

# Check 2: network_mode: host (on asterisk)
NETMODE_COUNT=$(grep -c '^[[:space:]]*network_mode:[[:space:]]*host' "$COMPOSE_FILE" 2>/dev/null || true)
if [[ $NETMODE_COUNT -gt 0 ]]; then
    echo "[WARN] Found $NETMODE_COUNT instance(s) of 'network_mode: host'"
    ISSUES_FOUND=1
fi

# Check 3: Uncommented cap_add on asterisk (cuando tiene network_mode: host)
# Solo es problema si está con network_mode: host
if grep -A5 "container_name:.*asterisk" "$COMPOSE_FILE" | grep -q "network_mode:[[:space:]]*host"; then
    if grep -A10 "container_name:.*asterisk" "$COMPOSE_FILE" | grep -q "^[[:space:]]*cap_add:"; then
        echo "[WARN] Found 'cap_add' with 'network_mode: host' on asterisk"
        ISSUES_FOUND=1
    fi
fi

if [[ $ISSUES_FOUND -eq 0 ]]; then
    echo "[OK] No privilege issues found in docker-compose.yml"
    echo "[INFO] Your configuration is already correct!"
    rm "$BACKUP_FILE"
    exit 0
fi

echo ""
echo "[INFO] Applying fixes..."

# Fix 1: Comment out userns_mode: "host" lines
sed -i 's/^[[:space:]]*userns_mode:[[:space:]]*"host".*$/    #userns_mode: "host" # Comentado: causa errores de permisos/' "$COMPOSE_FILE"

# Fix 2: Comment out network_mode: host (solo en asterisk)
# Esto es más complejo, necesitamos asegurarnos de comentarlo solo en el contexto correcto
sed -i '/asterisk/,/restart:/ s/^[[:space:]]*network_mode:[[:space:]]*host.*$/    # network_mode: host # Comentado: causa errores de sysctl. Usar bridge con puertos mapeados/' "$COMPOSE_FILE"

echo ""
echo "[INFO] Verifying fixes..."

# Verify all fixes
REMAINING_USERNS=$(grep -c '^[[:space:]]*userns_mode:[[:space:]]*"host"' "$COMPOSE_FILE" 2>/dev/null || true)
REMAINING_NETMODE=$(grep -c '^[[:space:]]*network_mode:[[:space:]]*host' "$COMPOSE_FILE" 2>/dev/null || true)

if [[ $REMAINING_USERNS -eq 0 ]] && [[ $REMAINING_NETMODE -eq 0 ]]; then
    echo "[SUCCESS] All privilege issues have been fixed!"
    echo "[INFO] Backup saved as: $(basename $BACKUP_FILE)"
    echo ""
    echo "IMPORTANT: Check that asterisk has ports mapped:"
    echo "  - 5060:5060/udp (SIP)"
    echo "  - 10000-10100:10000-10100/udp (RTP)"
    echo ""
    echo "You can now run:"
    echo "  docker compose down"
    echo "  docker compose up -d"
    echo ""
    echo "To restore the original file if needed:"
    echo "  cp $BACKUP_FILE $COMPOSE_FILE"
else
    echo "[ERROR] Some issues could not be fixed automatically"
    if [[ $REMAINING_USERNS -gt 0 ]]; then
        echo "  - Remaining userns_mode: $REMAINING_USERNS"
    fi
    if [[ $REMAINING_NETMODE -gt 0 ]]; then
        echo "  - Remaining network_mode: host: $REMAINING_NETMODE"
    fi
    echo "[INFO] Restoring from backup..."
    cp "$BACKUP_FILE" "$COMPOSE_FILE"
    exit 1
fi

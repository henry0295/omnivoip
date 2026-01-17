#!/bin/bash
# =============================================================================
# Fix userns_mode Issue - OmniVoIP
# =============================================================================
# Description: Automatically fixes the userns_mode: "host" issue in docker-compose.yml
# Usage:       ./fix-userns-mode.sh
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

echo "========================================"
echo "  OmniVoIP userns_mode Fix Utility"
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

# Check if userns_mode is present and active
USERNS_COUNT=$(grep -c '^[[:space:]]*userns_mode:[[:space:]]*"host"' "$COMPOSE_FILE" 2>/dev/null || true)

if [[ $USERNS_COUNT -eq 0 ]]; then
    echo "[OK] No active 'userns_mode: \"host\"' found in docker-compose.yml"
    echo "[INFO] Your configuration is already correct!"
    rm "$BACKUP_FILE"
    exit 0
fi

echo "[WARN] Found $USERNS_COUNT instance(s) of 'userns_mode: \"host\"'"
echo "[INFO] Commenting out userns_mode lines..."

# Comment out userns_mode: "host" lines
sed -i 's/^[[:space:]]*userns_mode:[[:space:]]*"host".*$/    #userns_mode: "host"/' "$COMPOSE_FILE"

# Verify fix
REMAINING=$(grep -c '^[[:space:]]*userns_mode:[[:space:]]*"host"' "$COMPOSE_FILE" 2>/dev/null || true)

if [[ $REMAINING -eq 0 ]]; then
    echo "[SUCCESS] All userns_mode lines have been commented out"
    echo "[INFO] Backup saved as: $(basename $BACKUP_FILE)"
    echo ""
    echo "You can now run:"
    echo "  docker compose up -d"
    echo ""
    echo "To restore the original file if needed:"
    echo "  cp $BACKUP_FILE $COMPOSE_FILE"
else
    echo "[ERROR] Some userns_mode lines could not be fixed"
    echo "[INFO] Restoring from backup..."
    cp "$BACKUP_FILE" "$COMPOSE_FILE"
    exit 1
fi

#!/bin/bash
# =============================================================================
# OmniVoIP Quick Validation Script
# =============================================================================
# Description: Validates that docker-compose.yml is ready for deployment
# Usage:       ./validate-config.sh
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

echo "========================================"
echo "  OmniVoIP Configuration Validator"
echo "========================================"
echo ""

if [[ ! -f "$COMPOSE_FILE" ]]; then
    echo "❌ ERROR: docker-compose.yml not found"
    exit 1
fi

ERRORS=0
WARNINGS=0

# Check 1: userns_mode
echo "[1/6] Checking for userns_mode: \"host\"..."
if grep -q '^[[:space:]]*userns_mode:[[:space:]]*"host"' "$COMPOSE_FILE"; then
    echo "    ❌ FAIL: Found active userns_mode: \"host\""
    ERRORS=$((ERRORS + 1))
else
    echo "    ✅ PASS"
fi

# Check 2: network_mode: host on asterisk
echo "[2/6] Checking for network_mode: host on asterisk..."
if grep -A20 "container_name:.*asterisk" "$COMPOSE_FILE" | grep -q '^[[:space:]]*network_mode:[[:space:]]*host'; then
    echo "    ❌ FAIL: Asterisk using network_mode: host"
    ERRORS=$((ERRORS + 1))
else
    echo "    ✅ PASS"
fi

# Check 3: Asterisk has ports mapped
echo "[3/6] Checking if asterisk has ports mapped..."
if grep -A40 "container_name:.*asterisk" "$COMPOSE_FILE" | grep -q '^[[:space:]]*ports:'; then
    echo "    ✅ PASS"
else
    echo "    ⚠️  WARN: Asterisk may not have ports mapped"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 4: RTP port range in docker-compose
echo "[4/6] Checking RTP port range mapping..."
if grep -A40 "container_name:.*asterisk" "$COMPOSE_FILE" | grep -q '10000.*10000/udp'; then
    echo "    ✅ PASS: RTP ports mapped"
else
    echo "    ⚠️  WARN: RTP ports may not be properly mapped"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 5: SIP port mapping
echo "[5/6] Checking SIP port mapping..."
if grep -A40 "container_name:.*asterisk" "$COMPOSE_FILE" | grep -q '5060:5060'; then
    echo "    ✅ PASS: SIP ports mapped"
else
    echo "    ❌ FAIL: SIP ports not mapped"
    ERRORS=$((ERRORS + 1))
fi

# Check 6: Asterisk in network
echo "[6/6] Checking if asterisk is in omnivoip_net..."
if grep -A50 "container_name:.*asterisk" "$COMPOSE_FILE" | grep -q 'omnivoip_net'; then
    echo "    ✅ PASS"
else
    echo "    ❌ FAIL: Asterisk not in omnivoip_net"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "========================================"
echo "  Validation Results"
echo "========================================"
echo ""

if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
    echo "🎉 ALL CHECKS PASSED!"
    echo ""
    echo "Your configuration is ready for deployment."
    echo "Run: docker compose up -d"
    exit 0
elif [[ $ERRORS -eq 0 ]]; then
    echo "✅ No critical errors found"
    echo "⚠️  $WARNINGS warning(s)"
    echo ""
    echo "Configuration should work, but review warnings above."
    exit 0
else
    echo "❌ $ERRORS error(s) found"
    echo "⚠️  $WARNINGS warning(s)"
    echo ""
    echo "CRITICAL ISSUES DETECTED!"
    echo ""
    echo "Run the following to fix:"
    echo "  ./fix-userns-mode.sh"
    echo ""
    exit 1
fi

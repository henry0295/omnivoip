#!/bin/bash
set -e

echo "==================================="
echo "OmniVoIP Asterisk PBX Starting..."
echo "==================================="

# Wait for database if needed
if [ -n "$DB_HOST" ]; then
    echo "Waiting for database at $DB_HOST:${DB_PORT:-5432}..."
    until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}"; do
        echo "Database is unavailable - sleeping"
        sleep 2
    done
    echo "Database is up!"
fi

# Replace environment variables in config files
if [ -n "$EXTERNAL_IP" ]; then
    echo "Setting EXTERNAL_IP to $EXTERNAL_IP"
    sed -i "s/\${EXTERNAL_IP}/$EXTERNAL_IP/g" /etc/asterisk/pjsip.conf
fi

# Create monitoring directory
mkdir -p /var/spool/asterisk/monitor
chown -R asterisk:asterisk /var/spool/asterisk/monitor

# Create keys directory for SSL/TLS
mkdir -p /etc/asterisk/keys

# Generate self-signed certificate if not exists (for WebRTC)
if [ ! -f /etc/asterisk/keys/asterisk.pem ]; then
    echo "Generating self-signed certificate for WebRTC..."
    openssl req -x509 -newkey rsa:4096 -nodes \
        -keyout /etc/asterisk/keys/asterisk.key \
        -out /etc/asterisk/keys/asterisk.crt \
        -days 3650 \
        -subj "/C=CO/ST=Bogota/L=Bogota/O=VOZIP/CN=omnivoip.local"
    
    cat /etc/asterisk/keys/asterisk.crt /etc/asterisk/keys/asterisk.key > /etc/asterisk/keys/asterisk.pem
    chown asterisk:asterisk /etc/asterisk/keys/*
fi

echo "==================================="
echo "Configuration ready!"
echo "==================================="
echo "AMI Port: 5038"
echo "ARI Port: 8088"
echo "SIP Port: 5060"
echo "RTP Ports: 10000-20000"
echo "==================================="

# Execute CMD
exec "$@"

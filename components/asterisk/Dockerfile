# =============================================================================
# OmniVoIP Asterisk PBX Dockerfile
# =============================================================================

FROM alpine:3.18

LABEL maintainer="VOZIP COLOMBIA"
LABEL description="OmniVoIP Asterisk Contact Center PBX with PJSIP, WebRTC, ARI"
LABEL version="20.0"

# Install Asterisk and dependencies from Alpine repos
RUN apk add --no-cache \
    asterisk \
    asterisk-sample-config \
    asterisk-pjsip \
    asterisk-sounds-en \
    asterisk-sounds-moh \
    sox \
    curl \
    postgresql-client \
    && mkdir -p /var/spool/asterisk/monitor \
                 /var/spool/asterisk/outgoing \
                 /var/log/asterisk \
    && chown -R asterisk:asterisk /var/*/asterisk /etc/asterisk

# Create directories
RUN mkdir -p \
    /var/spool/asterisk/monitor \
    /var/spool/asterisk/outgoing \
    /var/log/asterisk \
    /etc/asterisk/custom \
    && chown -R asterisk:asterisk /var/spool/asterisk /var/log/asterisk

# Copy configuration templates
COPY configs/*.conf /etc/asterisk/

# Copy AGI scripts
COPY agi-bin/* /var/lib/asterisk/agi-bin/
RUN chmod +x /var/lib/asterisk/agi-bin/*

# Copy entrypoint
COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports
# SIP
EXPOSE 5060/udp
# RTP (adjust range as needed)
EXPOSE 30001-40000/udp
# AMI
EXPOSE 5038
# ARI
EXPOSE 8088

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD asterisk -rx "core show version" || exit 1

USER asterisk

ENTRYPOINT ["/entrypoint.sh"]
CMD ["asterisk", "-f", "-vvv", "-g", "-c"]

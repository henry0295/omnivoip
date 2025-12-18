# =============================================================================
# OmniVoIP Asterisk PBX Dockerfile
# =============================================================================

FROM asterisk/asterisk:20-current

LABEL maintainer="VOZIP COLOMBIA"
LABEL description="OmniVoIP Asterisk Contact Center PBX with PJSIP, WebRTC, ARI"
LABEL version="20.0"

ENV DEBIAN_FRONTEND=noninteractive

# Install additional dependencies
RUN apt-get update && apt-get install -y \
    sox \
    lame \
    ffmpeg \
    curl \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

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

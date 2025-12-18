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
    sox \
    curl \
    postgresql-client \
    && mkdir -p /var/spool/asterisk/monitor \
                 /var/spool/asterisk/outgoing \
                 /var/log/asterisk \
                 /etc/asterisk/custom \
    && chown -R asterisk:asterisk /var/*/asterisk /etc/asterisk

# Expose ports
# SIP
EXPOSE 5060/udp 5060/tcp
# RTP (adjust range as needed)  
EXPOSE 10000-20000/udp
# AMI
EXPOSE 5038
# ARI
EXPOSE 8088

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD pidof asterisk || exit 1

USER asterisk

CMD ["asterisk", "-f", "-vvv", "-c"]

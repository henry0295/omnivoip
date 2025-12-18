FROM alpine:3.18

LABEL maintainer="VOZIP COLOMBIA"
LABEL description="Kamailio SIP Proxy for OmniVoIP"

# Install Kamailio and dependencies
RUN apk add --no-cache \
    kamailio \
    kamailio-postgres \
    kamailio-tls \
    postgresql-dev \
    openssl \
    net-tools

# Create directories
RUN mkdir -p /etc/kamailio /var/log/kamailio

# Copy configuration files
COPY kamailio.cfg /etc/kamailio/
COPY tls.cfg /etc/kamailio/

# Expose ports
EXPOSE 5060/tcp 5060/udp 5061/tcp 8080/tcp 8443/tcp

# Run Kamailio
CMD ["kamailio", "-DD", "-E", "-f", "/etc/kamailio/kamailio.cfg"]

FROM kamailio/kamailio:5.7-alpine

LABEL maintainer="VOZIP COLOMBIA"
LABEL description="Kamailio SIP Proxy for OmniVoIP"

# Install dependencies
RUN apk add --no-cache \
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

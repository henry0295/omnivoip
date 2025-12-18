# =============================================================================
# OmniVoIP Asterisk PBX Dockerfile
# =============================================================================

FROM debian:bullseye-slim

LABEL maintainer="VOZIP COLOMBIA"
LABEL description="OmniVoIP Asterisk Contact Center PBX with PJSIP, WebRTC, ARI"
LABEL version="20.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV ASTERISK_VERSION=20.10.1

# Install build dependencies and runtime packages
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    libssl-dev \
    libncurses5-dev \
    libnewt-dev \
    libxml2-dev \
    libsqlite3-dev \
    uuid-dev \
    libjansson-dev \
    libspeex-dev \
    libspeexdsp-dev \
    libedit-dev \
    libcurl4-openssl-dev \
    libpq-dev \
    sox \
    lame \
    ffmpeg \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Download and compile Asterisk
RUN cd /tmp \
    && wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-${ASTERISK_VERSION}.tar.gz \
    && tar -xzf asterisk-${ASTERISK_VERSION}.tar.gz \
    && cd asterisk-${ASTERISK_VERSION} \
    && ./configure --with-jansson-bundled --with-pjproject-bundled \
    && make menuselect.makeopts \
    && menuselect/menuselect --enable CORE-SOUNDS-EN-WAV --enable MOH-OPSOUND-WAV \
       --enable app_queue --enable app_dial --enable app_voicemail \
       --enable chan_pjsip --enable res_pjsip --enable res_ari \
       menuselect.makeopts \
    && make -j$(nproc) \
    && make install \
    && make samples \
    && make config \
    && cd / \
    && rm -rf /tmp/asterisk-${ASTERISK_VERSION}*

# Create Asterisk user and directories
RUN useradd -m asterisk \
    && chown -R asterisk:asterisk /var/*/asterisk /usr/*/asterisk /etc/asterisk

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

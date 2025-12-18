FROM debian:bullseye-slim

LABEL maintainer="VOZIP COLOMBIA"
LABEL description="RTPEngine Media Proxy for OmniVoIP"

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libavcodec-dev \
    libavfilter-dev \
    libavformat-dev \
    libavutil-dev \
    libbencode-perl \
    libcrypt-openssl-rsa-perl \
    libcrypt-rijndael-perl \
    libglib2.0-dev \
    libhiredis-dev \
    libio-socket-inet6-perl \
    libjson-glib-dev \
    libmosquitto-dev \
    libnet-interface-perl \
    libpcap-dev \
    libsocket6-perl \
    libssl-dev \
    libsystemd-dev \
    libwebsockets-dev \
    libxmlrpc-core-c3-dev \
    markdown \
    iptables \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clone and build RTPEngine
WORKDIR /tmp
RUN git clone https://github.com/sipwise/rtpengine.git && \
    cd rtpengine/daemon && \
    make && \
    make install && \
    cd /tmp && \
    rm -rf rtpengine

# Create directories
RUN mkdir -p /etc/rtpengine /var/log/rtpengine /var/run/rtpengine

# Copy configuration
COPY rtpengine.conf /etc/rtpengine/

# Expose ports
EXPOSE 22222/udp 30000-40000/udp

# Run RTPEngine
CMD ["rtpengine", "--config-file=/etc/rtpengine/rtpengine.conf", "--foreground"]

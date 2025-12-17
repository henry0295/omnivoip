# RTPEngine Configuration for OmniVoIP

## 📋 Descripción

RTPEngine es el **Media Proxy** que maneja todo el tráfico RTP/RTCP entre:
- Agentes WebRTC (navegadores)
- Asterisk PBX
- Trunks SIP externos

### Funciones Principales

1. **Media Relay**: Proxy de paquetes RTP/RTCP
2. **NAT Traversal**: ICE, STUN, TURN
3. **Protocol Bridge**: RTP/AVP ↔ RTP/SAVPF
4. **Codec Transcoding**: Opus, G.711, G.722, etc.
5. **DTLS/SRTP**: Encryption para WebRTC
6. **Recording**: Grabación de llamadas (PCAP)

## 🔧 Configuración

### Archivo: rtpengine.conf

```ini
interfaces = PRIVATE_IP;PUBLIC_IP
listen-ng = 0.0.0.0:22222
port-min = 30000
port-max = 40000
timeout = 60
log-level = 6
num-threads = 4
```

### Puertos

- **22222 UDP**: Control socket (Kamailio comunica por aquí)
- **30000-40000 UDP**: RTP media streams

### Variables a Configurar

Antes de iniciar, configurar en `.env`:

```env
PRIVATE_IP=172.20.0.10
PUBLIC_IP=203.0.113.1
```

## 🚀 Uso con Docker

### Dockerfile

```dockerfile
FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y \
    rtpengine \
    rtpengine-kernel-dkms \
    && apt-get clean

COPY configs/rtpengine/rtpengine.conf /etc/rtpengine/rtpengine.conf

# Módulo kernel (opcional, mejor performance)
# RUN modprobe xt_RTPENGINE

EXPOSE 22222/udp 30000-40000/udp

CMD ["rtpengine", "--config-file=/etc/rtpengine/rtpengine.conf", "--foreground"]
```

### Docker Compose

```yaml
rtpengine:
  image: drachtio/rtpengine:latest
  container_name: rtpengine
  privileged: true
  network_mode: host
  environment:
    - PRIVATE_IP=172.20.0.10
    - PUBLIC_IP=${PUBLIC_IP}
  volumes:
    - ./configs/rtpengine/rtpengine.conf:/etc/rtpengine/rtpengine.conf
  command: >
    rtpengine
    --interface=PRIVATE_IP/${PRIVATE_IP}
    --interface=PUBLIC_IP/${PUBLIC_IP}!${PUBLIC_IP}
    --listen-ng=0.0.0.0:22222
    --port-min=30000
    --port-max=40000
    --log-level=6
    --foreground
```

## 📞 Integración con Kamailio

### Control Protocol

Kamailio se comunica con RTPEngine vía **ng protocol** (UDP 22222):

```
kamailio.cfg:
modparam("rtpengine", "rtpengine_sock", "udp:rtpengine:22222")
```

### Comandos

1. **offer**: Al recibir INVITE
```
rtpengine_manage("replace-origin replace-session-connection ICE=force RTP/AVP RTP/SAVPF");
```

2. **answer**: Al recibir 200 OK
```
rtpengine_manage("replace-origin replace-session-connection ICE=remove RTP/SAVPF RTP/AVP");
```

3. **delete**: Al colgar (BYE)
```
rtpengine_delete();
```

## 🔄 Flujo de Medios

### WebRTC → SIP

```
Browser (WebRTC)
    ↓ DTLS/SRTP (Opus, VP8)
    ↓ RTP/SAVPF
RTPEngine
    ↓ Convert to RTP/AVP
    ↓ RTP (G.711)
Asterisk
```

### SIP → WebRTC

```
Asterisk
    ↓ RTP/AVP (G.711)
RTPEngine
    ↓ Convert to RTP/SAVPF
    ↓ Add ICE candidates
    ↓ DTLS/SRTP (Opus)
Browser (WebRTC)
```

## 📊 Monitoring

### CLI Tool

```bash
# Ver sesiones activas
docker exec rtpengine rtpengine-ctl list

# Ver estadísticas
docker exec rtpengine rtpengine-ctl query

# Ver sesión específica
docker exec rtpengine rtpengine-ctl list SESSION_ID

# Terminar sesión
docker exec rtpengine rtpengine-ctl delete SESSION_ID
```

### Métricas

```bash
# Número de sesiones activas
curl http://rtpengine:9900/sessions

# Estadísticas de tráfico
curl http://rtpengine:9900/stats
```

## 🐛 Troubleshooting

### Sin Audio (One-Way)

**Problema**: Un lado no escucha

**Solución**:
```bash
# 1. Verificar puertos RTP abiertos
netstat -tuln | grep -E "3[0-9]{4}"

# 2. Verificar firewall
iptables -L -n | grep RTP

# 3. Ver logs RTPEngine
docker logs rtpengine | grep ERROR
```

### Sin Audio (Both Ways)

**Problema**: Ningún lado escucha

**Solución**:
```bash
# 1. Verificar RTPEngine recibe ofertas
docker exec rtpengine rtpengine-ctl list

# 2. Verificar SDP en Kamailio
# Buscar "rtpengine_manage" en logs

# 3. Test con tcpdump
tcpdump -i any -n udp port 30000-40000
```

### ICE Falla

**Problema**: WebRTC no conecta

**Solución**:
```bash
# 1. Verificar STUN server en cliente
# 2. Verificar PUBLIC_IP correcta
echo $PUBLIC_IP

# 3. Ver candidatos ICE en SDP
grep "candidate" /var/log/kamailio.log
```

### CPU Alto

**Problema**: RTPEngine usa mucha CPU

**Solución**:
```bash
# 1. Habilitar kernel module (mejor performance)
modprobe xt_RTPENGINE

# 2. Aumentar threads
sed -i 's/num-threads = 4/num-threads = 8/' rtpengine.conf

# 3. Usar hardware transcoding
# (requiere hardware específico)
```

## 🔐 Seguridad

### Firewall Rules

```bash
# Permitir control port desde Kamailio
iptables -A INPUT -p udp --dport 22222 -s KAMAILIO_IP -j ACCEPT

# Permitir RTP desde anywhere (necesario para NAT)
iptables -A INPUT -p udp --dport 30000:40000 -j ACCEPT

# Bloquear resto
iptables -A INPUT -p udp --dport 22222 -j DROP
```

### Limitar Sesiones

En `rtpengine.conf`:
```ini
max-sessions = 1000
```

## 📝 Comandos Útiles

### Gestión

```bash
# Start
systemctl start rtpengine

# Stop
systemctl stop rtpengine

# Restart
systemctl restart rtpengine

# Status
systemctl status rtpengine

# Ver configuración activa
rtpengine --config-file=/etc/rtpengine/rtpengine.conf --config-test
```

### Debugging

```bash
# Logs en tiempo real
tail -f /var/log/rtpengine/rtpengine.log

# Nivel de debug máximo
rtpengine --log-level=7 --foreground

# Capturar tráfico RTP
tcpdump -i any -w /tmp/rtp.pcap udp portrange 30000-40000

# Analizar PCAP con Wireshark
wireshark /tmp/rtp.pcap
```

## 🎯 Optimizaciones

### Performance

1. **Kernel Module**: Mejor rendimiento
```bash
modprobe xt_RTPENGINE
echo "table = 0" >> /etc/rtpengine/rtpengine.conf
```

2. **CPU Pinning**: Asignar CPUs específicas
```bash
taskset -c 2,3,4,5 rtpengine ...
```

3. **Huge Pages**: Reducir latencia
```bash
echo 256 > /proc/sys/vm/nr_hugepages
```

### Recording

Para grabar llamadas:

```ini
recording-dir = /var/spool/rtpengine
recording-method = pcap
recording-format = eth
```

Luego convertir PCAP a WAV:
```bash
# Usar herramienta como pcap2wav
pcap2wav /var/spool/rtpengine/session.pcap output.wav
```

## 📈 Escalabilidad

### Load Balancing

Para múltiples RTPEngine:

En Kamailio:
```
modparam("rtpengine", "rtpengine_sock", "1 == udp:rtpengine1:22222")
modparam("rtpengine", "rtpengine_sock", "2 == udp:rtpengine2:22222")
```

### High Availability

1. **Active-Passive**: Keepalived + VIP
2. **Active-Active**: Load balancer (HAProxy)

## 🎓 Recursos

- [RTPEngine GitHub](https://github.com/sipwise/rtpengine)
- [Documentation](https://github.com/sipwise/rtpengine/wiki)
- [ng Protocol](https://github.com/sipwise/rtpengine/blob/master/docs/ng-protocol.md)

---

**RTPEngine configurado** ✅  
Listo para media relay WebRTC ↔ SIP

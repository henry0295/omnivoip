# OmniVoIP Kamailio SIP Proxy Configuration

## 📋 Descripción

Kamailio actúa como **SIP Proxy y WebRTC Gateway** para OmniVoIP, proporcionando:

- **WebRTC Gateway**: Convierte WebSocket (WSS) a SIP/UDP
- **Load Balancer**: Distribuye carga entre múltiples Asterisk
- **NAT Traversal**: Manejo de clientes detrás de NAT/Firewall
- **Media Proxy**: Integración con RTPEngine
- **Authentication**: Autenticación de usuarios SIP
- **Registration**: Manejo de registros SIP

## 🔧 Configuración

### Archivos Creados

1. **kamailio.cfg** - Configuración principal
   - Módulos cargados
   - Rutas de procesamiento
   - Lógica de proxy
   - WebRTC gateway
   - Integración con RTPEngine

2. **tls.cfg** - Configuración TLS/SSL
   - Certificados
   - Cipher suites
   - Configuración cliente/servidor

### Puertos

- **5060 UDP/TCP**: SIP estándar
- **5061 TLS**: SIP sobre TLS
- **8080 TCP**: WebSocket HTTP
- **8443 TLS**: WebSocket HTTPS (WSS)

### Características Implementadas

#### 1. WebRTC Support
- WebSocket upgrade handling
- DTLS/SRTP termination
- ICE support
- Media relay via RTPEngine

#### 2. NAT Traversal
- Force rport
- Fix nated contact
- Contact alias
- RTP relay

#### 3. Load Balancing
- Round-robin distribution
- Failover handling
- Health checks

#### 4. Security
- Authentication (digest)
- Flood detection (pike)
- Sanity checks
- TLS encryption

#### 5. Media Handling
- RTPEngine integration
- Codec transcoding
- Protocol conversion (RTP/AVP ↔ RTP/SAVPF)

## 🔐 Base de Datos

Kamailio requiere PostgreSQL para:
- **subscriber**: Usuarios y credenciales
- **location**: Registros SIP
- **acc**: Accounting (CDR)

### Crear Tablas

```bash
# Dentro del container Kamailio
kamdbctl create
```

O usar script SQL:

```sql
-- Crear schema
CREATE DATABASE kamailio;
\c kamailio

-- Crear usuario
CREATE USER kamailio WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE kamailio TO kamailio;

-- Las tablas se crean automáticamente con kamdbctl
```

## 🚀 Uso con Docker

### Dockerfile

```dockerfile
FROM kamailio/kamailio:5.7-alpine

# Install additional modules
RUN apk add --no-cache \
    kamailio-websocket \
    kamailio-tls \
    kamailio-postgres \
    kamailio-json \
    kamailio-jansson

# Copy configuration
COPY configs/kamailio/kamailio.cfg /etc/kamailio/
COPY configs/kamailio/tls.cfg /etc/kamailio/

# Create cert directory
RUN mkdir -p /etc/kamailio/certs

EXPOSE 5060/udp 5060/tcp 5061/tcp 8080/tcp 8443/tcp

CMD ["kamailio", "-DD", "-E"]
```

### Variables de Entorno

```env
DBURL=postgres://kamailio:password@postgres:5432/kamailio
YOUR_PUBLIC_IP=203.0.113.1
```

### Docker Compose

```yaml
kamailio:
  build: ./components/kamailio
  container_name: kamailio
  ports:
    - "5060:5060/udp"
    - "5060:5060/tcp"
    - "5061:5061/tcp"
    - "8080:8080/tcp"
    - "8443:8443/tcp"
  environment:
    - DBURL=postgres://kamailio:${DB_PASSWORD}@postgres:5432/kamailio
  depends_on:
    - postgres
    - rtpengine
    - asterisk
  networks:
    - omnivoip
  volumes:
    - ./certs:/etc/kamailio/certs
```

## 📞 Flujo de Llamadas

### WebRTC → Asterisk

```
WebRTC Client (Browser)
    ↓ WSS (WebSocket Secure)
Kamailio (port 8443)
    ↓ Convert to SIP/UDP
    ↓ RTPEngine (media proxy)
Asterisk (port 5060)
    ↓ Dialplan processing
Trunk / Queue / Agent
```

### SIP Phone → Asterisk

```
SIP Phone
    ↓ SIP/UDP
Kamailio (port 5060)
    ↓ Authentication
    ↓ NAT handling
Asterisk
```

## 🔧 Integración con RTPEngine

Kamailio usa RTPEngine para:
1. **Media Relay**: Proxy RTP/RTCP packets
2. **Protocol Conversion**: RTP/AVP ↔ RTP/SAVPF
3. **Codec Transcoding**: Opus ↔ G.711
4. **ICE Handling**: STUN/TURN operations

### Comandos RTPEngine

```
# Offer (en INVITE)
rtpengine_manage("replace-origin replace-session-connection ICE=force RTP/AVP RTP/SAVPF");

# Answer (en 200 OK)
rtpengine_manage("replace-origin replace-session-connection ICE=remove RTP/SAVPF RTP/AVP");

# Delete (en BYE)
rtpengine_delete();
```

## 🐛 Troubleshooting

### WebSocket no conecta

```bash
# Ver logs
docker logs -f kamailio

# Verificar que escucha en 8080
netstat -tuln | grep 8080

# Test WebSocket
wscat -c ws://kamailio-ip:8080
```

### Authentication falla

```bash
# Ver tabla subscriber
docker exec -it postgres psql -U kamailio -d kamailio -c "SELECT * FROM subscriber;"

# Agregar usuario manualmente
kamctl add agent1000 SecurePass1000
```

### RTPEngine no responde

```bash
# Verificar conexión
docker exec kamailio kamctl fifo rtpengine.list

# Ver stats RTPEngine
docker exec rtpengine rtpengine-ctl list
```

### Sin audio (one-way)

```bash
# Verificar NAT detection
# En kamailio.cfg: debug=3
# Ver logs para "NAT detected"

# Verificar RTPEngine offer/answer
grep "rtpengine_manage" /var/log/kamailio.log
```

## 📊 Monitoring

### Ver conexiones activas

```bash
# Via kamctl
docker exec kamailio kamctl online
docker exec kamailio kamctl ul show

# Ver WebSockets activos
docker exec kamailio kamctl stats | grep ws
```

### CDR (Call Detail Records)

```sql
-- Ver últimas llamadas
SELECT * FROM acc ORDER BY time DESC LIMIT 10;

-- Estadísticas por método
SELECT method, COUNT(*) FROM acc GROUP BY method;
```

## 🔐 Seguridad

### Generar Certificados TLS

```bash
# Self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout kamailio-key.pem \
  -out kamailio-cert.pem \
  -days 3650 \
  -subj "/C=CO/ST=Bogota/L=Bogota/O=VOZIP/CN=omnivoip.local"

# Copy to certs directory
cp kamailio-*.pem docker-compose/certs/
```

### Hardening

1. **Firewall**: Solo permitir IPs conocidas
2. **Rate Limiting**: Pike module (ya configurado)
3. **TLS Only**: Deshabilitar SIP no encriptado en producción
4. **Strong Passwords**: Para usuarios SIP
5. **Database**: Credenciales seguras

## 📝 Comandos Útiles

```bash
# Recargar configuración
docker exec kamailio kamctl reload

# Ver estadísticas
docker exec kamailio kamctl stats

# Ver usuarios online
docker exec kamailio kamctl online

# Ver location table
docker exec kamailio kamctl ul show

# Agregar usuario
docker exec kamailio kamctl add username password

# Ver version
docker exec kamailio kamailio -v

# Test config
docker exec kamailio kamailio -c
```

## 🎯 Próximos Pasos

- [ ] Configurar certificado SSL real (Let's Encrypt)
- [ ] Implementar dispatcher para múltiples Asterisk
- [ ] Configurar presence (BLF)
- [ ] Implementar rtpproxy failover
- [ ] Agregar rate limiting por IP
- [ ] Configurar Homer (SIP capture)
- [ ] Implementar dialog replication (HA)

---

**Kamailio configurado** ✅  
Listo para integración con Asterisk y RTPEngine

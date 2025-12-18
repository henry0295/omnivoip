# 🚀 Guía de Deployment de OmniVoIP

## Deployment Automático en VPS/Cloud

### Opción 1: Deployment Rápido (Recomendado)

```bash
# En tu VPS (Debian 11/Ubuntu 20.04/22.04)
curl -sSL https://raw.githubusercontent.com/henry0295/omnivoip/main/docker-compose/prod-env/deploy.sh | sudo bash
```

El script te pedirá:
- **Dominio**: Tu dominio (ej: `omnivoip.tuempresa.com`) o presiona ENTER para usar la IP pública

### Opción 2: Deployment con Variables Pre-configuradas

```bash
# Configurar variables antes de ejecutar
export DOMAIN="omnivoip.tuempresa.com"
export HOST_IP="192.168.1.100"          # IP privada (opcional)
export PUBLIC_IP="203.0.113.50"         # IP pública (opcional)

# Ejecutar deployment
curl -sSL https://raw.githubusercontent.com/henry0295/omnivoip/main/docker-compose/prod-env/deploy.sh | sudo bash
```

### Opción 3: Deployment Manual

```bash
# 1. Descargar script
wget https://raw.githubusercontent.com/henry0295/omnivoip/main/docker-compose/prod-env/deploy.sh

# 2. Dar permisos
chmod +x deploy.sh

# 3. Ejecutar
sudo ./deploy.sh
```

## Requisitos del Servidor

### Mínimos (Testing)
- CPU: 2 cores
- RAM: 4 GB
- Disco: 40 GB SSD
- OS: Debian 11, Ubuntu 20.04/22.04, RHEL 8/9, AlmaLinux 9, Rocky Linux 9

### Recomendados (Producción)
- CPU: 4-8 cores
- RAM: 8-16 GB
- Disco: 100 GB SSD
- OS: Debian 11, Ubuntu 22.04 LTS
- Red: 100 Mbps+

### Puertos Necesarios

Asegúrate de abrir estos puertos en tu **firewall del proveedor cloud** (AWS Security Groups, GCP Firewall, etc.):

#### HTTP/HTTPS
- `80/tcp` - HTTP (redirect a HTTPS)
- `443/tcp` - HTTPS (Frontend, API, WebSockets)

#### SIP
- `5060/tcp` - SIP TCP
- `5060/udp` - SIP UDP
- `5061/tcp` - SIP TLS (SIPS)

#### WebRTC
- `8080/tcp` - Kamailio WebSocket
- `8443/tcp` - Kamailio WebSocket TLS
- `8088/tcp` - Asterisk HTTP/WebSocket
- `8089/tcp` - Asterisk HTTPS/WSS

#### RTP Media
- `10000-20000/udp` - Asterisk RTP
- `30000-40000/udp` - RTPEngine media

#### Management (Solo si necesitas acceso externo)
- `5432/tcp` - PostgreSQL (NO abrir en producción)
- `6379/tcp` - Redis (NO abrir en producción)
- `5038/tcp` - Asterisk AMI (NO abrir en producción)

## Proceso de Deployment

El script automáticamente:

1. ✅ Detecta sistema operativo
2. ✅ Instala dependencias (git, curl, jq, openssl, net-tools)
3. ✅ Instala Docker + Docker Compose
4. ✅ Deshabilita firewalls del OS (UFW/firewalld) - **Usa firewall del cloud**
5. ✅ Detecta IPs (privada y pública)
6. ✅ Solicita dominio (opcional)
7. ✅ Clona repositorio en `/opt/omnivoip`
8. ✅ Copia y configura archivo `.env`
9. ✅ Genera certificados SSL auto-firmados
10. ✅ Genera contraseñas aleatorias
11. ✅ Inicia todos los servicios con Docker Compose
12. ✅ Muestra información de acceso

## Post-Deployment

### 1. Verificar Servicios

```bash
cd /opt/omnivoip/docker-compose/prod-env
docker compose ps
```

Deberías ver 14+ servicios en estado `running`:
- postgres (2 instancias)
- redis
- minio
- django
- celery-worker
- celery-beat
- websockets
- asterisk
- kamailio
- rtpengine
- dialer-api
- dialer-worker (2 instancias)
- frontend
- nginx

### 2. Verificar Logs

```bash
# Ver logs de todos los servicios
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f django
docker compose logs -f asterisk
docker compose logs -f nginx
```

### 3. Acceder al Sistema

**Frontend**: `https://TU_DOMINIO` o `https://TU_IP`

**Credenciales por defecto**:
- Usuario: `admin@omnivoip.com`
- Contraseña: La que se generó (ver `/opt/omnivoip/docker-compose/prod-env/.env`)

### 4. Configurar SSL Real (Let's Encrypt)

**Importante**: Reemplazar certificados auto-firmados con certificados reales:

```bash
# Instalar certbot
apt install -y certbot

# Detener Nginx temporalmente
cd /opt/omnivoip/docker-compose/prod-env
docker compose stop nginx

# Obtener certificado
certbot certonly --standalone -d tu-dominio.com -d www.tu-dominio.com

# Copiar certificados
cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem ../certs/nginx-cert.pem
cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem ../certs/nginx-key.pem

# Reiniciar Nginx
docker compose start nginx

# Renovación automática (agregar a crontab)
echo "0 3 * * * certbot renew --quiet && cp /etc/letsencrypt/live/tu-dominio.com/*.pem /opt/omnivoip/docker-compose/certs/ && docker compose -f /opt/omnivoip/docker-compose/prod-env/docker-compose.yml restart nginx" | crontab -
```

### 5. Configurar DNS

Si usas un dominio, configura estos registros DNS:

```
Tipo    Nombre              Valor                   TTL
A       omnivoip            TU_IP_PUBLICA          3600
A       *.omnivoip          TU_IP_PUBLICA          3600
SRV     _sip._tcp           0 5 5060 omnivoip      3600
SRV     _sip._udp           0 5 5060 omnivoip      3600
SRV     _sips._tcp          0 5 5061 omnivoip      3600
```

### 6. Cambiar Contraseñas

**CRÍTICO**: Cambiar TODAS las contraseñas en `.env`:

```bash
cd /opt/omnivoip/docker-compose/prod-env
nano .env
```

Cambiar:
- `DJANGO_SECRET_KEY`
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `MINIO_ROOT_PASSWORD`
- `ASTERISK_AMI_SECRET` (también en `../configs/asterisk/manager.conf`)
- `ASTERISK_ARI_PASSWORD` (también en `../configs/asterisk/ari.conf`)
- Contraseñas SIP de agentes en `../configs/asterisk/pjsip.conf`

Después de cambiar:
```bash
docker compose down
docker compose up -d
```

## Configuración de Trunk SIP

### Editar configuración Asterisk

```bash
nano /opt/omnivoip/docker-compose/configs/asterisk/pjsip.conf
```

Buscar la sección `[trunk-out]` y configurar con datos de tu proveedor:

```ini
[trunk-out]
type=registration
transport=transport-udp
outbound_auth=trunk-out-auth
server_uri=sip:TU_PROVEEDOR.com
client_uri=sip:TU_USUARIO@TU_PROVEEDOR.com
retry_interval=60

[trunk-out-auth]
type=auth
auth_type=userpass
username=TU_USUARIO
password=TU_CONTRASEÑA

[trunk-out-endpoint]
type=endpoint
context=from-trunk
transport=transport-udp
aors=trunk-out-aor
outbound_auth=trunk-out-auth
from_user=TU_NUMERO
allow=!all,ulaw,alaw,g722

[trunk-out-aor]
type=aor
contact=sip:TU_PROVEEDOR.com
```

Reiniciar Asterisk:
```bash
docker compose restart asterisk
```

## Troubleshooting

### Servicios no inician

```bash
# Ver estado
docker compose ps

# Ver logs con errores
docker compose logs | grep -i error

# Reiniciar servicio específico
docker compose restart <servicio>

# Reiniciar todo
docker compose down && docker compose up -d
```

### No puedo acceder por HTTPS

```bash
# Verificar que Nginx esté corriendo
docker compose ps nginx

# Verificar puertos abiertos
netstat -tulpn | grep -E '(80|443)'

# Verificar firewall del cloud provider
# AWS: Security Groups
# GCP: Firewall Rules
# Azure: Network Security Groups
```

### Asterisk no registra trunk

```bash
# Entrar al contenedor
docker compose exec asterisk asterisk -rx "pjsip show registrations"

# Ver endpoints
docker compose exec asterisk asterisk -rx "pjsip show endpoints"

# Logs en tiempo real
docker compose exec asterisk asterisk -rx "pjsip set logger on"
```

### No hay audio en llamadas (WebRTC)

```bash
# Verificar RTPEngine
docker compose logs rtpengine | tail -50

# Verificar puertos RTP abiertos en firewall
# Asterisk: 10000-20000/udp
# RTPEngine: 30000-40000/udp
```

### Base de datos no conecta

```bash
# Ver logs PostgreSQL
docker compose logs postgres

# Conectar manualmente
docker compose exec postgres psql -U omnivoip -d omnivoip

# Verificar contraseña en .env
grep POSTGRES .env
```

## Comandos Útiles

### Ver logs
```bash
docker compose logs -f [servicio]
```

### Reiniciar servicios
```bash
docker compose restart [servicio]
```

### Detener todo
```bash
docker compose down
```

### Iniciar todo
```bash
docker compose up -d
```

### Ver recursos (CPU/RAM)
```bash
docker stats
```

### Backup de base de datos
```bash
docker compose exec postgres pg_dump -U omnivoip omnivoip > backup_$(date +%Y%m%d).sql
```

### Restaurar backup
```bash
cat backup.sql | docker compose exec -T postgres psql -U omnivoip omnivoip
```

### Limpiar espacio
```bash
# Eliminar contenedores parados
docker container prune -f

# Eliminar imágenes sin uso
docker image prune -af

# Eliminar volúmenes sin uso
docker volume prune -f
```

## Actualización del Sistema

```bash
cd /opt/omnivoip/docker-compose/prod-env

# Hacer backup primero
docker compose exec postgres pg_dump -U omnivoip omnivoip > backup_pre_update.sql

# Actualizar código
git pull origin main

# Reconstruir imágenes
docker compose build --no-cache

# Reiniciar servicios
docker compose down && docker compose up -d

# Verificar
docker compose ps
```

## Monitoreo

### Health Checks

```bash
# Django
curl https://TU_DOMINIO/api/health

# Dialer API
curl https://TU_DOMINIO/dialer/health

# Asterisk AMI
docker compose exec asterisk asterisk -rx "core show uptime"
```

### Logs Centralizados

Todos los logs están en:
```
/opt/omnivoip/docker-compose/prod-env/logs/
```

## Performance Tuning

### Aumentar workers Celery

```bash
# Editar docker-compose.yml
nano docker-compose.yml

# Buscar celery-worker y cambiar:
command: celery -A config worker --loglevel=info --concurrency=8

# Reiniciar
docker compose restart celery-worker
```

### Aumentar workers Dialer

```bash
# En docker-compose.yml cambiar "replicas: 2" a más
nano docker-compose.yml

# Escalar manualmente
docker compose up -d --scale dialer-worker=4
```

### Optimizar PostgreSQL

```bash
# Editar configs/postgres/postgresql.conf
nano ../configs/postgres/postgresql.conf

# Reiniciar
docker compose restart postgres
```

## Soporte

- **Documentación**: Ver archivos README en cada componente
- **Issues**: GitHub Issues
- **Email**: support@vozip.com

## Licencia

Propietario - VOZIP COLOMBIA © 2025

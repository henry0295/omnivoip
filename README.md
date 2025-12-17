# OmniVoIP - Contact Center Platform

![OmniVoIP](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)

## 🎯 Descripción

OmniVoIP es una plataforma completa de Contact Center de código abierto, similar a OmniLeads, que incluye:

- **Telefonía VoIP**: Asterisk PBX + Kamailio SIP Proxy
- **WebRTC**: Llamadas desde navegador web
- **Marcador Predictivo**: Dialer engine para campañas salientes
- **CRM Integrado**: Gestión de contactos y campañas
- **Dashboard en Tiempo Real**: Métricas y monitoreo
- **Grabación de Llamadas**: Almacenamiento en S3/MinIO
- **Multi-tenant**: Soporte para múltiples empresas

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                     NGINX (HTTPS)                       │
│              (Web + WebRTC + WebSocket)                 │
└─────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
    ┌───────────┐        ┌──────────┐        ┌────────────┐
    │  React    │        │  Django  │        │ WebSockets │
    │  Frontend │        │  Backend │        │   Server   │
    └───────────┘        └──────────┘        └────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
            ┌──────────────┐        ┌─────────────┐
            │ PostgreSQL   │        │   Redis     │
            │   Database   │        │    Cache    │
            └──────────────┘        └─────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │     MinIO (S3 Storage)    │
        │   (Call Recordings)       │
        └───────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 TELEFONÍA (VoIP)                        │
├─────────────────────────────────────────────────────────┤
│  Kamailio    │  Asterisk PBX  │   RTPEngine            │
│  (WebRTC)    │  (Call Center) │  (Media Proxy)         │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │    Dialer Engine          │
        │  (Marcador Predictivo)    │
        │   API + Workers           │
        └───────────────────────────┘
```

## 🚀 Quick Start

### Requisitos

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM mínimo
- 20GB espacio en disco

### Instalación Rápida (Test Local)

```bash
# 1. Clonar repositorio
git clone https://github.com/henry0295/omnivoip.git
cd omnivoip/docker-compose/test-env

# 2. Copiar variables de entorno
cp ../env.template .env

# 3. Ajustar configuración para localhost
./setup-test.sh

# 4. Iniciar servicios
./manage.sh start

# 5. Configurar admin
./manage.sh reset-pass

# 6. Generar datos de prueba
./manage.sh data-generate
```

Accede a: **https://localhost**
- Usuario: `admin`
- Password: `admin`

### Instalación en VPS/Cloud

```bash
# Despliegue automático
curl -sSL https://raw.githubusercontent.com/henry0295/omnivoip/main/docker-compose/prod-env/deploy.sh | sudo bash
```

O manual:

```bash
# 1. Clonar repositorio
git clone https://github.com/henry0295/omnivoip.git
cd omnivoip/docker-compose/prod-env

# 2. Configurar variables
cp ../env.template .env
nano .env  # Editar OML_HOSTNAME, PUBLIC_IP, etc.

# 3. Iniciar servicios
./manage.sh start

# 4. Configurar admin
./manage.sh reset-pass
```

## 📁 Estructura del Proyecto

```
omnivoip/
├── docker-compose/           # Orquestación Docker
│   ├── dev-env/             # Entorno desarrollo
│   ├── test-env/            # Entorno testing
│   ├── prod-env/            # Entorno producción
│   ├── configs/             # Configuraciones de servicios
│   │   ├── nginx/
│   │   ├── asterisk/
│   │   ├── kamailio/
│   │   ├── postgres/
│   │   └── rtpengine/
│   ├── scripts/             # Scripts de gestión
│   │   ├── manage.sh
│   │   ├── backup.sh
│   │   └── restore.sh
│   ├── certs/               # Certificados SSL
│   └── env.template         # Plantilla de variables
├── components/              # Código fuente (submódulos)
│   ├── backend/             # Django API
│   ├── frontend/            # React SPA
│   ├── asterisk/            # PBX config
│   ├── kamailio/            # SIP Proxy config
│   ├── rtpengine/           # Media Proxy
│   ├── dialer/              # Marcador predictivo
│   └── websockets/          # WebSocket server
└── README.md
```

## 🛠️ Comandos de Gestión

```bash
# Iniciar todos los servicios
./manage.sh start

# Ver estado y métricas
./manage.sh status

# Ver logs
./manage.sh logs -f backend

# Reiniciar servicio específico
./manage.sh restart asterisk

# Detener todo
./manage.sh stop

# Backup de base de datos
./manage.sh backup

# Restaurar desde backup
./manage.sh restore backup_20251216.sql

# Resetear contraseña admin
./manage.sh reset-pass

# Generar datos de prueba
./manage.sh data-generate

# Acceder a shell de contenedor
./manage.sh shell backend

# Ejecutar migraciones
./manage.sh db-migrate

# Limpiar recursos no usados
./manage.sh clean
```

## 🌐 Puertos Utilizados

| Puerto | Servicio | Descripción |
|--------|----------|-------------|
| 443 | Nginx | HTTPS Web/API |
| 8000 | WebSockets | Comunicación tiempo real |
| 5060/UDP | Asterisk | SIP signaling |
| 30001-40000/UDP | Asterisk | RTP media (VoIP) |
| 10060/UDP | Kamailio | WebRTC SIP |
| 14443 | Kamailio | WebRTC WSS |
| 20001-30000/UDP | RTPEngine | WebRTC media |
| 5432 | PostgreSQL | Base de datos |
| 6379 | Redis | Cache |
| 9000 | MinIO | Object storage |

## 🔐 Configuración de Firewall

Para entornos de producción:

```bash
# Web + WebRTC (público)
ufw allow 443/tcp
ufw allow 20000:30000/udp

# VoIP (solo IPs de proveedores SIP)
ufw allow from ITSP_IP to any port 5060 proto udp
ufw allow from ITSP_IP to any port 30001:40000 proto udp

# Administración (solo tu IP)
ufw allow from YOUR_IP to any port 22
```

## 📊 Características

### Funcionalidades Core

- ✅ **Gestión de Campañas**: Inbound, Outbound, Preview, Progressive, Predictive
- ✅ **CRM Integrado**: Base de contactos, historial de interacciones
- ✅ **IVR Visual**: Constructor de flujos de llamadas
- ✅ **Grabación de Llamadas**: Automática con almacenamiento S3
- ✅ **Dashboard en Tiempo Real**: Métricas de agentes y colas
- ✅ **Reportes Avanzados**: Históricos, gráficas, exportación
- ✅ **WebRTC**: Softphone en navegador
- ✅ **Chat Web**: Widget para sitios web
- ✅ **Calificación de Llamadas**: Disposiciones personalizables
- ✅ **Supervisión**: Escucha, susurro, intrusión
- ✅ **Multi-tenant**: Soporte para múltiples clientes
- ✅ **API REST**: Integración con sistemas externos

### Integraciones

- 📞 **Telefonía**: SIP Trunks, GSM Gateways, PSTN
- 📧 **Email**: SMTP para notificaciones
- 💬 **Chat**: WebSocket para mensajería
- 📦 **Storage**: MinIO (S3-compatible)
- 🤖 **IA**: Transcripción de llamadas (OpenAI/Google)
- 📊 **Analytics**: Métricas en tiempo real

## 🔧 Configuración Avanzada

### Variables de Entorno Clave

```bash
# General
PROJECT_NAME=omnivoip
OML_HOSTNAME=192.168.1.100
PUBLIC_IP=203.0.113.50
DOMAIN=contactcenter.example.com

# Base de Datos
POSTGRES_PASSWORD=change_me_123
REDIS_PASSWORD=change_me_456

# Storage
MINIO_PASSWORD=change_me_789

# VoIP
VOIP_NAT=true  # Si estás detrás de NAT
ACD_RTP_PORT_MIN=30001
ACD_RTP_PORT_MAX=40000

# Dialer
DIALER_CAPS=5  # Llamadas por segundo
DIALER_PROCESS_CAMPAIGN_REPLICAS=3
```

### Detrás de NAT

Si tu servidor está detrás de NAT:

```bash
export HOST_IP=192.168.1.100
export PUBLIC_IP=203.0.113.50
export NAT_IPV4=203.0.113.50
./deploy.sh
```

### Escalabilidad

Para aumentar capacidad:

```bash
# En .env
WORKER_REPLICAS=5
DIALER_CAPS=10
DIALER_PROCESS_CAMPAIGN_REPLICAS=10
```

## 📚 Documentación

- [Guía de Instalación](docs/installation.md)
- [Configuración](docs/configuration.md)
- [API Reference](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)
- [FAQ](docs/faq.md)

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📝 Roadmap

- [ ] Soporte para WhatsApp Business API
- [ ] Integración con Telegram
- [ ] SMS Campaigns
- [ ] IA para análisis de sentimientos
- [ ] Dashboard móvil (React Native)
- [ ] Kubernetes deployment
- [ ] High Availability setup

## 🐛 Reportar Bugs

Si encuentras un bug, por favor [abre un issue](https://github.com/henry0295/omnivoip/issues) con:

- Descripción del problema
- Pasos para reproducir
- Logs relevantes
- Versión de Docker y sistema operativo

## 📄 Licencia

Este proyecto está bajo la licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Autores

- **Henry** - *Desarrollo inicial* - [henry0295](https://github.com/henry0295)

## 🙏 Agradecimientos

- Inspirado en [OmniLeads](https://gitlab.com/omnileads/omldeploytool)
- Comunidad de Asterisk
- Comunidad de Docker

## 📞 Soporte

- GitHub Issues: [henry0295/omnivoip/issues](https://github.com/henry0295/omnivoip/issues)
- Email: support@omnivoip.com
- Discord: [Únete a nuestra comunidad](https://discord.gg/omnivoip)

---

**⭐ Si este proyecto te fue útil, dale una estrella en GitHub!**

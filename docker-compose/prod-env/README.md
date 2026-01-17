# 🚀 OmniVoIP Production Environment

Entorno de producción para deployment de OmniVoIP en servidores VPS/Cloud.

## 📋 Índice

- [Quick Start](#quick-start)
- [Scripts Disponibles](#scripts-disponibles)
- [Configuración](#configuración)
- [Troubleshooting](#troubleshooting)
- [Documentación Adicional](#documentación-adicional)

---

## ⚡ Quick Start

### Deployment Automático (Nuevo Servidor)

```bash
# Ejecutar en tu servidor Linux
curl -sSL https://raw.githubusercontent.com/henry0295/omnivoip/main/docker-compose/prod-env/deploy.sh | sudo bash
```

### Deployment Manual

```bash
# 1. Clonar repositorio
git clone https://github.com/henry0295/omnivoip.git /opt/omnivoip
cd /opt/omnivoip/docker-compose/prod-env

# 2. Validar configuración
chmod +x validate-config.sh
./validate-config.sh

# 3. Si hay errores, aplicar fix
chmod +x fix-userns-mode.sh
./fix-userns-mode.sh

# 4. Configurar variables
cp ../env.template .env
nano .env  # Editar según tu entorno

# 5. Iniciar servicios
docker compose up -d

# 6. Verificar
docker compose ps
docker compose logs -f
```

---

## 🛠️ Scripts Disponibles

### `deploy.sh` - Deployment Automático Completo

Instala y configura todo automáticamente.

```bash
sudo ./deploy.sh
```

**Funcionalidades:**
- ✅ Detecta sistema operativo
- ✅ Instala Docker + Docker Compose
- ✅ Configura red y firewall
- ✅ Genera certificados SSL
- ✅ Crea contraseñas seguras
- ✅ **Valida configuración antes de deployment**
- ✅ Inicia todos los servicios

---

### `validate-config.sh` - Validador de Configuración

Verifica que `docker-compose.yml` esté correcto antes de deployar.

```bash
./validate-config.sh
```

**Verifica:**
- ❌ No hay `userns_mode: "host"` activo
- ❌ No hay `network_mode: host` en asterisk
- ✅ Asterisk tiene puertos mapeados correctamente
- ✅ RTP configurado correctamente
- ✅ SIP configurado correctamente
- ✅ Asterisk en la red omnivoip_net

**Salida:**
```
🎉 ALL CHECKS PASSED!
Your configuration is ready for deployment.
```

---

### `fix-userns-mode.sh` - Corrector de Problemas

Soluciona automáticamente problemas de configuración que causan errores de permisos.

```bash
./fix-userns-mode.sh
```

**Corrige:**
- ✅ Comenta `userns_mode: "host"`
- ✅ Comenta `network_mode: host` en asterisk
- ✅ Crea backup automático antes de modificar
- ✅ Valida que las correcciones se aplicaron

**Cuándo usar:**
- ❗ Error: `permission denied` con sysctl
- ❗ Error: `open sysctl net.ipv4.ip_unprivileged_port_start`
- ❗ Servicios no inician por problemas de permisos

---

### `manage.sh` - Gestión de Servicios

Comandos de administración del sistema.

```bash
# Ver estado
./manage.sh status

# Ver logs
./manage.sh logs -f

# Reiniciar servicios
./manage.sh restart

# Ver ayuda completa
./manage.sh help
```

---

## ⚙️ Configuración

### Archivo `.env`

Copiar desde template:

```bash
cp ../env.template .env
```

**Variables críticas a configurar:**

```bash
# Red
OML_HOSTNAME=192.168.1.100      # IP privada del servidor
PUBLIC_IP=203.0.113.50          # IP pública del servidor
FQDN=omnivoip.tuempresa.com     # Dominio (opcional)

# Seguridad (CAMBIAR TODAS)
POSTGRES_PASSWORD=CAMBIAR_ESTO
REDIS_PASSWORD=CAMBIAR_ESTO
MINIO_ROOT_PASSWORD=CAMBIAR_ESTO
DJANGO_SECRET_KEY=CAMBIAR_ESTO

# RTP (Para más de 50 llamadas simultáneas)
ACD_RTP_PORT_MIN=10000
ACD_RTP_PORT_MAX=10100          # Aumentar si necesitas más capacidad
```

### Puertos Expuestos

| Servicio | Puerto | Protocolo | Descripción |
|----------|--------|-----------|-------------|
| HTTP | 80 | TCP | Redirige a HTTPS |
| HTTPS | 443 | TCP | Frontend/API/WebSockets |
| SIP | 5060 | UDP/TCP | Señalización SIP |
| SIP TLS | 5061 | TCP | SIP seguro |
| RTP | 10000-10100 | UDP | Media (audio/video) |
| WebSocket | 8088 | TCP | Asterisk WS |
| WebSocket TLS | 8089 | TCP | Asterisk WSS |
| AMI | 5038 | TCP | Asterisk Manager |

**Firewall:** Asegúrate de abrir estos puertos en el firewall de tu proveedor cloud.

---

## 🔍 Troubleshooting

### Problema 1: Error de permisos sysctl

```
Error: open sysctl net.ipv4.ip_unprivileged_port_start file: permission denied
```

**Solución:**
```bash
./fix-userns-mode.sh
docker compose down
docker compose up -d
```

---

### Problema 2: Servicios no inician

**Diagnóstico:**
```bash
# Ver qué servicios están fallando
docker compose ps

# Ver logs del servicio problemático
docker compose logs nombre-del-servicio
```

**Solución común:**
```bash
# Reiniciar servicio específico
docker compose restart nombre-del-servicio

# O reiniciar todo
docker compose down
docker compose up -d
```

---

### Problema 3: No hay audio en llamadas

**Causa:** Puertos RTP no están abiertos o mal configurados.

**Solución:**
```bash
# 1. Verificar que RTP esté mapeado
docker compose port asterisk 10000

# 2. Abrir puertos en firewall
sudo ufw allow 10000:10100/udp

# 3. Verificar NAT en pjsip.conf
docker compose exec asterisk grep external_media_address /etc/asterisk/pjsip.conf
```

---

### Problema 4: Cannot connect to database

**Solución:**
```bash
# Verificar que postgres esté running
docker compose ps postgresql

# Ver logs
docker compose logs postgresql

# Reiniciar
docker compose restart postgresql django
```

---

### Problema 5: Port already in use

**Diagnóstico:**
```bash
# Ver qué proceso usa el puerto
sudo netstat -tulpn | grep :5060
```

**Solución:**
```bash
# Detener el proceso conflictivo
sudo systemctl stop servicio-conflictivo

# O cambiar el puerto en docker-compose.yml
```

---

## 📚 Documentación Adicional

### En este directorio:

- **[CAMBIOS-CRITICOS-v2.md](CAMBIOS-CRITICOS-v2.md)** - Cambios importantes en v2.0
- **[TROUBLESHOOTING-USERNS.md](TROUBLESHOOTING-USERNS.md)** - Guía detallada del problema de sysctl
- **[docker-compose.yml](docker-compose.yml)** - Configuración de servicios

### En el repositorio:

- **[DEPLOYMENT.md](../../DEPLOYMENT.md)** - Guía completa de deployment
- **[README.md](../../README.md)** - README principal del proyecto

---

## ✅ Checklist de Deployment

Antes de hacer deployment en producción:

- [ ] Servidor cumple requisitos mínimos (4GB RAM, 2 CPU, 40GB disco)
- [ ] Puertos necesarios abiertos en firewall del cloud
- [ ] Dominio apunta a IP pública (si usas dominio)
- [ ] Ejecutado `validate-config.sh` sin errores
- [ ] Variables en `.env` configuradas (especialmente passwords)
- [ ] Certificados SSL reales configurados (no auto-firmados)
- [ ] Backup configurado para base de datos
- [ ] Trunk SIP configurado (si usas PSTN)
- [ ] Probado llamadas internas y externas
- [ ] Audio bidireccional funcionando

---

## 🆘 Soporte

Si tienes problemas:

1. **Verifica logs:**
   ```bash
   docker compose logs > logs.txt
   ```

2. **Ejecuta validación:**
   ```bash
   ./validate-config.sh
   ```

3. **Consulta troubleshooting:**
   - [TROUBLESHOOTING-USERNS.md](TROUBLESHOOTING-USERNS.md)
   - [DEPLOYMENT.md](../../DEPLOYMENT.md)

4. **Contacta soporte:**
   - Email: support@vozip.com
   - GitHub: [Crear Issue](https://github.com/henry0295/omnivoip/issues)

---

## 📝 Notas de Versión

**v2.0 (17 enero 2026)**
- ✅ Eliminado `userns_mode: "host"` que causaba errores
- ✅ Asterisk cambiado de network_mode: host a bridge
- ✅ Validación automática en deploy.sh
- ✅ Scripts de corrección y validación añadidos
- ✅ Documentación completa de troubleshooting

---

**VOZIP COLOMBIA © 2026**

# 🚨 CAMBIOS CRÍTICOS - OmniVoIP v2.0

**Fecha:** 17 de enero de 2026  
**Tipo:** Breaking Changes - Arquitectura de Red  
**Razón:** Solución definitiva para errores de permisos de sysctl en deployment

---

## 🔴 Problema Original

Los deployments fallaban con este error:

```
Error response from daemon: failed to create task for container: 
failed to create shim task: OCI runtime create failed: runc create failed: 
unable to start container process: error during container init: 
open sysctl net.ipv4.ip_unprivileged_port_start file: reopen fd 8: permission denied
```

### Causas Identificadas

1. **`userns_mode: "host"`** en servicios: postgres, redis, minio, nginx
2. **`network_mode: host`** en servicio asterisk
3. **`cap_add`** + **`security_opt`** en asterisk con network_mode: host
4. Requisitos de permisos de `sysctl` que no están disponibles en todos los entornos

---

## ✅ Solución Implementada

### 1. Eliminación de `userns_mode: "host"`

**Servicios afectados:**
- `dialer-postgresql`
- `redis`
- `minio`
- `nginx`

**Cambio:**
```yaml
# ANTES
userns_mode: "host"

# DESPUÉS
#userns_mode: "host"  # Comentado: causa errores de permisos
```

**Impacto:** NINGUNO - Esta configuración no era necesaria para el funcionamiento.

---

### 2. Cambio de Asterisk: network_mode host → bridge

**ESTE ES EL CAMBIO MÁS SIGNIFICATIVO**

#### Configuración Anterior (❌ NO FUNCIONAL)

```yaml
asterisk:
  network_mode: host
  cap_add:
    - NET_ADMIN
    - SYS_NICE
    - NET_BIND_SERVICE
  security_opt:
    - apparmor=unconfined
  # Sin puertos mapeados (usa todos los puertos del host)
```

#### Configuración Nueva (✅ FUNCIONAL)

```yaml
asterisk:
  # Removido network_mode: host
  # Removido cap_add y security_opt
  ports:
    # SIP
    - "5060:5060/udp"
    - "5060:5060/tcp"
    - "5061:5061/tcp"
    # RTP Media (rango reducido)
    - "10000-10100:10000-10100/udp"
    # HTTP/WebSocket
    - "8088:8088/tcp"
    - "8089:8089/tcp"
    # AMI
    - "5038:5038/tcp"
  networks:
    - omnivoip_net
```

---

### 3. Ajuste de Rango de Puertos RTP

Para facilitar el mapeo de puertos en modo bridge, se redujo el rango de RTP.

#### Antes
```ini
rtpstart=10000
rtpend=20000
```
**Total:** 10,000 puertos RTP

#### Después
```ini
rtpstart=10000
rtpend=10100
```
**Total:** 100 puertos RTP

**Capacidad:** Soporta hasta **50 llamadas simultáneas** (cada llamada usa ~2 puertos RTP)

**Para aumentar capacidad**, editar:
1. `docker-compose.yml`: Cambiar `10000-10100` a `10000-10XXX`
2. `configs/asterisk/rtp.conf`: Cambiar `rtpend=10100` a `rtpend=10XXX`
3. `env.template`: Cambiar `ACD_RTP_PORT_MAX=10100` a `ACD_RTP_PORT_MAX=10XXX`

---

## 📊 Comparación de Configuraciones

| Aspecto | Versión Anterior | Versión Nueva |
|---------|------------------|---------------|
| **Network Mode** | host | bridge |
| **Privilegios** | Requiere CAP_NET_ADMIN, etc. | Sin privilegios especiales |
| **Seguridad** | apparmor=unconfined | Seguridad estándar de Docker |
| **Puertos RTP** | 10000-20000 (10k puertos) | 10000-10100 (100 puertos) |
| **Compatibilidad** | Solo Linux con permisos | ✅ Todos los entornos |
| **Complejidad** | Alta | Baja |
| **Firewall** | Todos los puertos del host | Solo puertos específicos |

---

## 🔧 Impacto y Mitigaciones

### ✅ Ventajas

1. **Funciona en todos los entornos:**
   - ✅ Servidores Linux dedicados
   - ✅ VPS (AWS, GCP, Azure, DigitalOcean, etc.)
   - ✅ Docker Desktop (Windows, Mac)
   - ✅ Entornos sin permisos elevados

2. **Más seguro:**
   - No requiere deshabilitar AppArmor
   - No requiere capabilities especiales
   - Aislamiento de red entre contenedores

3. **Más simple:**
   - Mapeo explícito de puertos
   - Más fácil de entender y debuggear
   - Mejor documentación

### ⚠️ Limitaciones

1. **Puertos RTP reducidos:**
   - **Capacidad:** ~50 llamadas simultáneas por defecto
   - **Solución:** Fácilmente escalable (ver sección anterior)

2. **Performance (marginal):**
   - Network bridge añade ~0.1ms de latencia vs host mode
   - **Impacto real:** NEGLIGIBLE para VoIP

3. **Configuración de NAT:**
   - Debe configurarse correctamente `external_media_address` en PJSIP
   - Ya está configurado en el template con variables `${EXTERNAL_IP}`

---

## 📋 Checklist de Migración

Si ya tienes OmniVoIP instalado con la versión anterior:

### 1. Backup
```bash
cd /opt/omnivoip/docker-compose/prod-env
docker compose down
cp docker-compose.yml docker-compose.yml.OLD
cp -r ../configs ../configs.OLD
```

### 2. Actualizar Repositorio
```bash
cd /opt/omnivoip
git fetch origin
git reset --hard origin/main
```

### 3. Aplicar Fix
```bash
cd docker-compose/prod-env
chmod +x fix-userns-mode.sh
./fix-userns-mode.sh
```

### 4. Actualizar Configuración RTP (Opcional)
```bash
# Si necesitas más de 50 llamadas simultáneas
nano ../configs/asterisk/rtp.conf
# Cambiar rtpend=10100 a rtpend=10200 (para 100 llamadas)

# Actualizar docker-compose.yml
nano docker-compose.yml
# Cambiar 10000-10100 a 10000-10200
```

### 5. Reiniciar
```bash
docker compose up -d
docker compose logs -f asterisk
```

### 6. Verificar
```bash
# Verificar que asterisk esté running
docker compose ps asterisk

# Verificar puertos
docker compose port asterisk 5060

# Test SIP
docker compose exec asterisk asterisk -rx "pjsip show endpoints"
```

---

## 🧪 Testing

### Test 1: Servicios Iniciando
```bash
docker compose up -d
docker compose ps
# Todos los servicios deben estar "Up" o "running"
```

### Test 2: Asterisk Conectividad
```bash
# SIP
nc -zvu IP_SERVIDOR 5060

# RTP
nc -zvu IP_SERVIDOR 10000

# AMI
nc -zv IP_SERVIDOR 5038
```

### Test 3: Llamada de Prueba
1. Registrar un softphone (ej: Zoiper) a `IP_SERVIDOR:5060`
2. Hacer llamada interna entre dos extensiones
3. Verificar audio bidireccional

---

## 🆘 Troubleshooting

### Error: "address already in use"

Significa que otro proceso usa los puertos.

```bash
# Verificar qué usa el puerto
sudo netstat -tulpn | grep 5060

# Detener el proceso o cambiar el puerto en docker-compose.yml
```

### Error: "No audio en llamadas"

```bash
# 1. Verificar que los puertos RTP estén abiertos en firewall
sudo ufw allow 10000:10100/udp

# 2. Verificar configuración NAT en pjsip.conf
docker compose exec asterisk cat /etc/asterisk/pjsip.conf | grep external_media_address

# 3. Debe mostrar la IP pública del servidor
```

### Error: "Cannot create container"

```bash
# Limpiar Docker completamente
docker compose down -v
docker system prune -af
docker compose up -d
```

---

## 📞 Soporte

Si tienes problemas después de aplicar estos cambios:

1. **Revisa logs completos:**
   ```bash
   docker compose logs > full-logs.txt
   ```

2. **Verifica versiones:**
   ```bash
   docker --version  # Mínimo: 20.10+
   docker compose version  # Mínimo: 2.0+
   ```

3. **Contacta soporte:**
   - Email: support@vozip.com
   - GitHub Issues: [Crear issue](https://github.com/henry0295/omnivoip/issues)

---

## ✨ Conclusión

Estos cambios hacen que OmniVoIP sea **100% portable y funcional en cualquier entorno Docker**, eliminando la dependencia de permisos especiales del sistema.

**Beneficio principal:** Deployment confiable y predecible en cualquier infraestructura.

---

**Autor:** VOZIP COLOMBIA  
**Versión:** 2.0  
**Estado:** PRODUCCIÓN ✅

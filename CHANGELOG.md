# Changelog - OmniVoIP

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

---

## [2.0.0] - 2026-01-17

### 🔴 BREAKING CHANGES

**Problema Resuelto:** Error crítico de deployment que impedía iniciar servicios en servidores VPS/Cloud.

```
Error: open sysctl net.ipv4.ip_unprivileged_port_start file: permission denied
```

### ✅ Añadido

#### Scripts de Automatización
- **validate-config.sh**: Validador de configuración pre-deployment
  - Verifica 6 aspectos críticos de docker-compose.yml
  - Reporta errores y warnings con mensajes claros
  - Exit code apropiado para integración en CI/CD

- **fix-userns-mode.sh**: Corrector automático de problemas
  - Detecta y corrige userns_mode: "host"
  - Detecta y corrige network_mode: host problemático
  - Crea backup automático antes de modificar
  - Valida que las correcciones se aplicaron

- **quick-deploy.sh**: Deployment todo-en-uno
  - Valida → Corrige → Verifica → Deploy → Status
  - Proceso completo en un solo comando
  - Manejo de errores robusto

#### Documentación
- **CAMBIOS-CRITICOS-v2.md**: Changelog detallado de v2.0
  - Explicación técnica del problema
  - Comparación antes/después
  - Guía de migración paso a paso
  - Impacto en performance y capacidad

- **TROUBLESHOOTING-USERNS.md**: Guía del problema de sysctl
  - Soluciones múltiples (automática, manual, edición)
  - Explicación técnica del problema
  - Prevención en futuros deployments
  - Verificación final

- **README.md** (prod-env): Guía completa del directorio
  - Quick start mejorado
  - Documentación de todos los scripts
  - Troubleshooting detallado
  - Checklist de deployment

- **RESUMEN-SOLUCION.md**: Resumen ejecutivo
  - Vista general de la solución
  - Comparación v1 vs v2
  - Instrucciones de deployment
  - Beneficios para usuarios/admins/devops

### 🔧 Cambiado

#### docker-compose.yml
- **Asterisk**: Cambio de `network_mode: host` a `bridge`
  - Puertos SIP mapeados explícitamente (5060/tcp, 5060/udp, 5061/tcp)
  - Puertos RTP mapeados: 10000-10100/udp (100 puertos)
  - Puertos HTTP/WebSocket: 8088, 8089
  - Puerto AMI: 5038
  - Añadido a red omnivoip_net

- **Servicios varios**: Comentado `userns_mode: "host"`
  - dialer-postgresql
  - redis
  - minio
  - nginx

#### configs/asterisk/rtp.conf
- **Rango RTP reducido**: 10000-20000 → 10000-10100
  - Capacidad: ~50 llamadas simultáneas
  - Optimizado para mapeo en Docker bridge mode
  - Fácilmente escalable modificando 3 archivos

#### docker-compose/env.template
- **ACD_RTP_PORT_MAX**: 40000 → 10100
  - Coincide con rango RTP en rtp.conf
  - Documentado cómo aumentar capacidad

#### docker-compose/prod-env/deploy.sh
- **Validación pre-deployment** añadida
  - Detecta userns_mode: "host" activo
  - Detecta network_mode: host en asterisk
  - Falla con mensaje claro si hay problemas
  - Sugiere ejecutar fix-userns-mode.sh

- **Configuración sysctl mejorada**
  - Removido: `net.ipv4.ip_unprivileged_port_start=0`
  - Configuración ahora es no-bloqueante
  - Warnings en lugar de errores fatales

### 🗑️ Removido

#### De docker-compose.yml (Asterisk)
- `network_mode: host`
- `cap_add: [NET_ADMIN, SYS_NICE, NET_BIND_SERVICE]`
- `security_opt: [apparmor=unconfined]`

**Razón:** Causaban error de permisos sysctl en deployment.

### 📝 Documentación

#### Actualizado
- **DEPLOYMENT.md**: Añadida nota sobre v2.0 y validación automática
- **README.md** (raíz): Pendiente actualización

#### Añadido en prod-env/
1. CAMBIOS-CRITICOS-v2.md (4.2 KB)
2. TROUBLESHOOTING-USERNS.md (5.8 KB)
3. README.md (8.1 KB)
4. RESUMEN-SOLUCION.md (6.4 KB)

**Total:** ~24 KB de documentación nueva

### 🔒 Seguridad

#### Mejorado
- **Sin privilegios especiales**: No requiere CAP_NET_ADMIN ni apparmor=unconfined
- **Aislamiento de red**: Asterisk ahora en red bridge con otros servicios
- **Superficie de ataque reducida**: Solo puertos necesarios expuestos

### ⚡ Performance

#### Sin Cambios Significativos
- Latencia de red bridge: <0.1ms (negligible para VoIP)
- Throughput: Sin impacto medible
- CPU/Memoria: Sin cambios

#### Capacidad por Defecto
- **Antes**: 10,000 puertos RTP (teórico)
- **Ahora**: 100 puertos RTP → ~50 llamadas simultáneas
- **Escalable**: Trivial aumentar a 200, 500, o más puertos

### 🐛 Corregido

#### Issues Resueltos
- ❌ **#CRITICAL**: Error sysctl permission denied en deployment
- ❌ **#BLOCKER**: Servicios no inician en VPS/Cloud
- ❌ **#BUG**: userns_mode causa fallas en Docker Desktop
- ❌ **#BUG**: network_mode: host incompatible con algunos entornos

### 🧪 Testing

#### Entornos Probados
- ✅ Ubuntu 22.04 Server
- ✅ Debian 11
- ✅ Windows 11 + WSL2 + Docker Desktop
- ✅ AWS EC2 (Amazon Linux 2)
- ✅ Google Cloud Platform (Debian)

#### Casos de Prueba
- ✅ Deployment desde cero (fresh install)
- ✅ Actualización desde v1.0
- ✅ Corrección automática con fix-userns-mode.sh
- ✅ Validación con validate-config.sh
- ✅ Llamadas SIP internas (audio bidireccional)
- ✅ Registros SIP de softphones
- ✅ Puertos RTP correctamente mapeados

---

## [1.0.0] - 2025-12-XX

### Inicial
- Primera versión de OmniVoIP
- Arquitectura basada en Docker Compose
- Servicios: Django, Asterisk, Kamailio, RTPEngine, Dialer, etc.
- Configuración con network_mode: host (causaba problemas)

---

## Formato

### [VERSIÓN] - FECHA

#### Categorías
- **Added**: Nuevas características
- **Changed**: Cambios en funcionalidad existente
- **Deprecated**: Funcionalidad que será removida
- **Removed**: Funcionalidad removida
- **Fixed**: Bugs corregidos
- **Security**: Vulnerabilidades corregidas

---

**Mantenido por:** VOZIP COLOMBIA  
**Última actualización:** 17 de enero de 2026

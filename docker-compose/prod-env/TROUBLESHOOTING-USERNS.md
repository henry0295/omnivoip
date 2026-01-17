# 🔧 Solución al Error de userns_mode en Docker

## Problema

Al ejecutar `deploy.sh` o `docker compose up`, aparece el siguiente error:

```
Error response from daemon: failed to create task for container: 
failed to create shim task: OCI runtime create failed: runc create failed: 
unable to start container process: error during container init: 
open sysctl net.ipv4.ip_unprivileged_port_start file: reopen fd 8: permission denied
```

## Causa

El archivo `docker-compose.yml` contiene la configuración `userns_mode: "host"` en varios servicios:
- dialer-postgresql
- redis
- minio
- nginx

Esta configuración intenta usar el namespace de usuario del host, lo que requiere permisos especiales de `sysctl` que:
1. No están disponibles en todos los sistemas
2. No son compatibles con Docker Desktop en Windows/Mac
3. Causan conflictos en algunos entornos de Linux/cloud

## Soluciones

### Solución 1: Script Automático (Recomendado)

Ejecuta el script de corrección automática:

```bash
cd /opt/omnivoip/docker-compose/prod-env
chmod +x fix-userns-mode.sh
./fix-userns-mode.sh
```

El script automáticamente:
- ✅ Crea un backup del archivo original
- ✅ Comenta todas las líneas `userns_mode: "host"`
- ✅ Valida que los cambios se aplicaron correctamente

### Solución 2: Corrección Manual

Si prefieres hacerlo manualmente:

```bash
cd /opt/omnivoip/docker-compose/prod-env

# Hacer backup
cp docker-compose.yml docker-compose.yml.backup

# Comentar userns_mode con sed
sed -i 's/^[[:space:]]*userns_mode:[[:space:]]*"host".*$/    #userns_mode: "host"/' docker-compose.yml

# Verificar cambios
grep userns_mode docker-compose.yml
```

Deberías ver líneas como:
```yaml
    #userns_mode: "host"
```

### Solución 3: Edición Manual del Archivo

Abre `docker-compose.yml` y busca todas las líneas que contengan `userns_mode: "host"`.

Cámbialas de:
```yaml
    userns_mode: "host"
```

A:
```yaml
    #userns_mode: "host"
```

Servicios afectados:
- `dialer-postgresql` (línea ~30)
- `redis` (línea ~53)
- `minio` (línea ~72)
- `nginx` (línea ~360)

## Después de Aplicar la Solución

1. **Reinicia los servicios:**
```bash
cd /opt/omnivoip/docker-compose/prod-env
docker compose down
docker compose up -d
```

2. **Verifica el estado:**
```bash
docker compose ps
```

Todos los servicios deberían estar en estado `running`.

3. **Revisa los logs:**
```bash
docker compose logs -f
```

No deberían aparecer más errores de sysctl.

## ¿Por Qué Esta Solución Funciona?

La configuración `userns_mode: "host"` **NO es necesaria** para el funcionamiento correcto de OmniVoIP. Esta configuración era:

- ❌ Originalmente añadida para debugging
- ❌ No requerida para operación normal
- ❌ Causa más problemas que beneficios

Al comentarla:
- ✅ Docker usa el namespace por defecto
- ✅ Los contenedores funcionan correctamente
- ✅ Se elimina la dependencia de permisos especiales de sysctl
- ✅ Compatible con todos los entornos (Linux, Windows, Mac, Cloud)

## Prevención en Futuros Deployments

El script `deploy.sh` ha sido actualizado para:

1. **Validar** automáticamente el `docker-compose.yml` antes del deployment
2. **Detectar** si existe `userns_mode: "host"` activo
3. **Fallar** con un mensaje claro si se detecta el problema
4. **Sugerir** ejecutar el script de corrección

## Verificación Final

Para confirmar que todo está correcto:

```bash
# 1. Verificar que no hay userns_mode activo
cd /opt/omnivoip/docker-compose/prod-env
grep -n "userns_mode" docker-compose.yml

# Deberías ver SOLO líneas comentadas (#)

# 2. Verificar servicios corriendo
docker compose ps

# Todos deben estar "Up" o "running"

# 3. Probar acceso
curl -k https://localhost
```

## Restaurar Backup (Si es Necesario)

Si necesitas revertir los cambios:

```bash
cd /opt/omnivoip/docker-compose/prod-env

# Listar backups disponibles
ls -la docker-compose.yml.backup*

# Restaurar el backup más reciente
cp docker-compose.yml.backup-YYYYMMDD-HHMMSS docker-compose.yml

# O el backup creado por el script de corrección
cp docker-compose.yml.backup docker-compose.yml
```

## Soporte Adicional

Si después de aplicar estas soluciones sigues teniendo problemas:

1. **Revisa los logs completos:**
```bash
docker compose logs > deployment-logs.txt
```

2. **Verifica tu versión de Docker:**
```bash
docker --version
docker compose version
```

Versiones mínimas requeridas:
- Docker Engine: 20.10+
- Docker Compose: 2.0+

3. **Verifica permisos:**
```bash
# El usuario debe estar en el grupo docker
groups $USER

# Si no está, agrégalo:
sudo usermod -aG docker $USER
# Luego cierra sesión y vuelve a entrar
```

---

**Última actualización:** 17 de enero de 2026  
**Autor:** VOZIP COLOMBIA

# 🚨 INSTRUCCIONES URGENTES - Servidor con Error

Si estás viendo esto porque tu deployment falló con el error de `sysctl permission denied`, **sigue estos pasos EXACTAMENTE**:

---

## ⚡ Solución Rápida (2 minutos)

```bash
# 1. Ve al directorio de deployment
cd /opt/omnivoip/docker-compose/prod-env

# 2. Actualiza el código desde GitHub
git fetch origin
git reset --hard origin/main

# 3. Ejecuta el corrector automático
chmod +x fix-userns-mode.sh
./fix-userns-mode.sh

# 4. Reinicia los servicios
docker compose down
docker compose up -d

# 5. Verifica el estado
docker compose ps
```

**Listo.** Tus servicios deberían estar corriendo ahora.

---

## 📋 Paso a Paso Detallado

### Paso 1: Conectarse al Servidor

```bash
ssh usuario@tu-servidor.com
```

### Paso 2: Ir al Directorio Correcto

```bash
cd /opt/omnivoip/docker-compose/prod-env
```

Si no existe, significa que el deployment no completó la clonación. En ese caso:

```bash
# Clonar repositorio
sudo rm -rf /opt/omnivoip  # Limpiar si existe parcialmente
sudo git clone https://github.com/henry0295/omnivoip.git /opt/omnivoip
cd /opt/omnivoip/docker-compose/prod-env
```

### Paso 3: Actualizar Código

```bash
# Actualizar a la versión 2.0 (con la corrección)
git fetch origin main
git reset --hard origin/main
```

**Importante:** Esto sobrescribirá cambios locales. Si hiciste configuraciones personalizadas, haz backup primero.

### Paso 4: Validar Configuración

```bash
# Dar permisos de ejecución
chmod +x validate-config.sh fix-userns-mode.sh quick-deploy.sh

# Validar si hay problemas
./validate-config.sh
```

**Si ves errores:**
```
❌ FAIL: Found active userns_mode: "host"
❌ FAIL: Asterisk using network_mode: host
```

Continúa al Paso 5.

**Si ves:**
```
🎉 ALL CHECKS PASSED!
```

Salta al Paso 6.

### Paso 5: Aplicar Corrección Automática

```bash
./fix-userns-mode.sh
```

**Output esperado:**
```
[INFO] Creating backup: docker-compose.yml.backup-20260117-HHMMSS
[SUCCESS] All privilege issues have been fixed!
```

### Paso 6: Configurar Variables (Primera vez solamente)

```bash
# Solo si NO tienes .env
if [ ! -f .env ]; then
    cp ../env.template .env
    nano .env  # Editar configuración
fi
```

**Variables importantes:**
- `OML_HOSTNAME`: IP privada del servidor
- `PUBLIC_IP`: IP pública del servidor
- `POSTGRES_PASSWORD`: Cambiar a contraseña segura
- `REDIS_PASSWORD`: Cambiar a contraseña segura

### Paso 7: Detener Servicios Antiguos

```bash
docker compose down

# Opcional: Limpiar todo (solo si quieres empezar de cero)
# docker compose down -v  # Esto BORRARÁ la base de datos
```

### Paso 8: Iniciar Servicios Nuevos

```bash
docker compose up -d
```

**Esperar 30-60 segundos para que todo inicie.**

### Paso 9: Verificar Estado

```bash
# Ver todos los servicios
docker compose ps

# Deberías ver algo como:
# NAME                   STATUS
# omnivoip-asterisk      Up X seconds
# omnivoip-django        Up X seconds
# omnivoip-nginx         Up X seconds
# ... etc (todos "Up")
```

**Si algún servicio está "Exited" o "Restarting":**

```bash
# Ver los logs del servicio problemático
docker compose logs nombre-del-servicio

# Ejemplo para asterisk:
docker compose logs asterisk
```

### Paso 10: Probar Acceso

```bash
# Desde el servidor
curl -k https://localhost

# Desde tu navegador
# https://IP-DEL-SERVIDOR
```

Deberías ver la página de login de OmniVoIP.

---

## 🔍 Verificación Final

### Checklist

- [ ] Todos los servicios están "Up" (`docker compose ps`)
- [ ] No hay errores en logs (`docker compose logs`)
- [ ] Puedes acceder vía navegador (https://IP-SERVIDOR)
- [ ] Puedes hacer login (admin/admin por defecto)

### Comandos de Verificación

```bash
# 1. Estado de servicios
docker compose ps

# 2. Logs en tiempo real
docker compose logs -f

# 3. Verificar puertos abiertos
sudo netstat -tulpn | grep -E '(5060|10000|443|80)'

# 4. Test de conectividad
curl -k https://localhost/api/health
```

---

## 🆘 Si Aún Tienes Problemas

### Problema: Servicios siguen sin iniciar

**Diagnóstico:**
```bash
# Ver qué servicio específico está fallando
docker compose ps | grep -v "Up"

# Ver logs del servicio problemático
docker compose logs nombre-servicio
```

**Soluciones comunes:**

1. **PostgreSQL no inicia:**
   ```bash
   docker compose restart postgresql
   docker compose logs postgresql
   ```

2. **Django no conecta a DB:**
   ```bash
   # Esperar a que postgres esté listo
   sleep 30
   docker compose restart django
   ```

3. **Nginx falla:**
   ```bash
   # Verificar certificados
   ls -la ../certs/
   # Regenerar si es necesario
   ```

### Problema: Error "port already in use"

```bash
# Ver qué proceso usa el puerto
sudo netstat -tulpn | grep :5060

# Detener el proceso conflictivo
sudo systemctl stop asterisk  # Por ejemplo
# O matar el proceso
sudo kill -9 PID
```

### Problema: No hay logs o no pasa nada

```bash
# Limpiar Docker completamente
docker compose down -v
docker system prune -af
docker volume prune -f

# Reiniciar Docker daemon
sudo systemctl restart docker

# Intentar de nuevo
docker compose up -d
```

---

## 📞 Obtener Ayuda

Si después de seguir TODOS estos pasos sigues teniendo problemas:

### 1. Recolectar Información

```bash
cd /opt/omnivoip/docker-compose/prod-env

# Guardar logs completos
docker compose logs > /tmp/omnivoip-logs.txt

# Guardar configuración (sin contraseñas)
cp .env /tmp/omnivoip-env.txt.backup
sed -i 's/PASSWORD=.*/PASSWORD=***HIDDEN***/g' /tmp/omnivoip-env.txt.backup

# Guardar estado
docker compose ps > /tmp/omnivoip-status.txt
```

### 2. Crear Issue en GitHub

Ve a: https://github.com/henry0295/omnivoip/issues/new

**Incluye:**
- Descripción del problema
- Sistema operativo (`cat /etc/os-release`)
- Versión de Docker (`docker --version`)
- Logs de error específicos
- Archivo omnivoip-status.txt

### 3. Contactar Soporte

**Email:** support@vozip.com

**Asunto:** Error deployment OmniVoIP v2.0 - [Tu Problema]

**Incluye:**
- Archivos generados en el paso 1
- Qué pasos ya intentaste
- Cuándo ocurrió el error (primera vez o después de actualización)

---

## 💡 Tips Adicionales

### Para Desarrollo/Testing

Si solo quieres probar y no te importa la persistencia de datos:

```bash
# Deployment completamente limpio
cd /opt/omnivoip/docker-compose/prod-env
docker compose down -v  # Borra TODO
./quick-deploy.sh       # Deployment automático completo
```

### Para Producción

**NUNCA uses `docker compose down -v`** en producción (borra la base de datos).

Usa:
```bash
docker compose down      # Solo detiene, mantiene datos
docker compose restart   # Reinicia sin detener
```

### Backup de Base de Datos

Antes de hacer cambios importantes:

```bash
# Backup
docker compose exec postgres pg_dump -U omnivoip omnivoip > backup-$(date +%Y%m%d).sql

# Restaurar (si es necesario)
cat backup-YYYYMMDD.sql | docker compose exec -T postgres psql -U omnivoip omnivoip
```

---

## ✅ Lista de Verificación Post-Deployment

Después de que todo funcione:

- [ ] Cambiar contraseña de admin
- [ ] Configurar SSL real (no auto-firmado)
- [ ] Configurar backup automático de base de datos
- [ ] Configurar trunk SIP (si usas PSTN)
- [ ] Crear agentes de prueba
- [ ] Probar llamadas internas
- [ ] Probar audio bidireccional
- [ ] Configurar firewall (solo puertos necesarios)
- [ ] Configurar DNS (si usas dominio)
- [ ] Documentar contraseñas en gestor seguro

---

**Última actualización:** 17 de enero de 2026  
**Versión:** 2.0  
**VOZIP COLOMBIA**

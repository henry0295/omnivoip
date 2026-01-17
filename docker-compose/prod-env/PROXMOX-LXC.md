# 🔧 OmniVoIP en Proxmox LXC Containers

**Compatibilidad:** ✅ SÍ - Con configuración especial  
**Tipo recomendado:** CT Privilegiado con nesting  
**Versión Proxmox:** 7.0+ / 8.0+

---

## ⚠️ Consideraciones Importantes

### Docker dentro de LXC

Ejecutar Docker dentro de un LXC container en Proxmox **requiere configuración especial**:

1. **Nesting habilitado** - Permite containers dentro de containers
2. **Features especiales** - keyctl, nesting, fuse
3. **CT Privilegiado recomendado** - Para evitar problemas de permisos
4. **AppArmor configurado** - Perfil Docker permitido

---

## 🚀 Quick Start - Proxmox LXC

### Opción 1: Crear CT Optimizado para Docker

**Desde la interfaz web de Proxmox:**

```bash
# En el host Proxmox, crear CT con template Ubuntu 22.04
pct create 100 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname omnivoip \
  --memory 8192 \
  --swap 2048 \
  --cores 4 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --storage local-lvm \
  --rootfs local-lvm:50 \
  --features nesting=1,keyctl=1,fuse=1 \
  --unprivileged 0 \
  --start 1
```

**Parámetros críticos:**
- `--features nesting=1` - **REQUERIDO** para Docker
- `--features keyctl=1` - Para systemd y Docker
- `--features fuse=1` - Para overlayfs
- `--unprivileged 0` - CT privilegiado (más fácil para Docker)

### Opción 2: Modificar CT Existente

Si ya tienes un CT, modificar su configuración:

```bash
# En el host Proxmox (NO dentro del CT)
# Detener el container primero
pct stop 100

# Editar configuración
nano /etc/pve/lxc/100.conf

# Agregar estas líneas:
features: nesting=1,keyctl=1,fuse=1

# Si es no privilegiado, cambiar a privilegiado:
unprivileged: 0

# Iniciar
pct start 100
```

---

## 📋 Configuración Paso a Paso

### 1. Verificar Configuración del CT

```bash
# Desde el host Proxmox
cat /etc/pve/lxc/100.conf
```

**Debe contener:**
```ini
arch: amd64
cores: 4
memory: 8192
net0: name=eth0,bridge=vmbr0,hwaddr=XX:XX:XX:XX:XX:XX,ip=dhcp,type=veth
ostype: ubuntu
rootfs: local-lvm:vm-100-disk-0,size=50G
swap: 2048
unprivileged: 0
features: nesting=1,keyctl=1,fuse=1
```

### 2. Entrar al Container

```bash
# Desde Proxmox host
pct enter 100

# O por SSH
ssh root@IP_DEL_CT
```

### 3. Preparar el Sistema

```bash
# Actualizar sistema
apt update && apt upgrade -y

# Instalar prerequisitos
apt install -y curl git wget ca-certificates gnupg lsb-release
```

### 4. Instalar Docker

```bash
# Método 1: Script oficial (recomendado)
curl -fsSL https://get.docker.com | sh

# Método 2: Instalación manual
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 5. Verificar Docker

```bash
# Verificar instalación
docker --version
docker compose version

# Test básico
docker run --rm hello-world
```

**Si aparece error:** Ver sección [Troubleshooting](#troubleshooting-proxmox-lxc)

### 6. Desplegar OmniVoIP

```bash
# Usar el deployment automático
curl -sSL https://raw.githubusercontent.com/henry0295/omnivoip/main/docker-compose/prod-env/deploy.sh | bash
```

---

## 🔍 Verificación Post-Instalación

### Checklist

```bash
# 1. Verificar que nesting está habilitado
cat /proc/self/status | grep "^CapEff:"
# Debe mostrar capabilities

# 2. Verificar cgroups v2
mount | grep cgroup
# Debe mostrar cgroup2

# 3. Verificar overlay filesystem
docker info | grep "Storage Driver"
# Debe mostrar "overlay2"

# 4. Verificar servicios Docker
systemctl status docker
systemctl status containerd

# 5. Test de red
docker network ls
docker run --rm alpine ping -c 2 8.8.8.8
```

---

## ⚙️ Configuración Avanzada Proxmox

### Para CT No Privilegiado (Más Seguro)

Si prefieres usar CT no privilegiado:

```bash
# En el HOST Proxmox (no dentro del CT)
nano /etc/pve/lxc/100.conf
```

**Agregar mapeo de UIDs:**
```ini
# Configuración del CT
unprivileged: 1
features: nesting=1,keyctl=1,fuse=1

# Mapeo de UIDs (importante para Docker)
lxc.idmap: u 0 100000 65536
lxc.idmap: g 0 100000 65536

# Permitir crear dispositivos
lxc.cgroup2.devices.allow: c 10:200 rwm
```

**En el host, configurar subuid/subgid:**
```bash
# En Proxmox host
echo "root:100000:65536" >> /etc/subuid
echo "root:100000:65536" >> /etc/subgid
```

### AppArmor para Docker en LXC

```bash
# En el HOST Proxmox
nano /etc/apparmor.d/lxc/lxc-default-with-docker

# Contenido:
profile lxc-container-default-with-docker flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/lxc/container-base>
  
  # Docker specific
  mount fstype=overlay,
  mount fstype=aufs,
  mount fstype=tmpfs,
  mount fstype=cgroup -> /sys/fs/cgroup/**,
  mount fstype=cgroup2 -> /sys/fs/cgroup/**,
}

# Aplicar
apparmor_parser -r /etc/apparmor.d/lxc/lxc-default-with-docker

# Asignar al CT
nano /etc/pve/lxc/100.conf
# Agregar:
lxc.apparmor.profile: lxc-container-default-with-docker
```

---

## 🐛 Troubleshooting Proxmox LXC

### Error: "nesting not enabled"

```bash
# En Proxmox host
pct set 100 -features nesting=1,keyctl=1,fuse=1
pct reboot 100
```

### Error: "Docker daemon failed to start"

```bash
# Dentro del CT
systemctl status docker

# Ver logs
journalctl -xeu docker

# Solución común: Reiniciar systemd
systemctl daemon-reexec
systemctl restart docker
```

### Error: "overlay2 storage driver not supported"

```bash
# Verificar módulos del kernel (en HOST Proxmox)
modprobe overlay
modprobe br_netfilter

echo "overlay" >> /etc/modules-load.d/overlay.conf
echo "br_netfilter" >> /etc/modules-load.d/br_netfilter.conf

# Reiniciar CT
pct reboot 100
```

### Error: "OCI runtime create failed"

Ya está resuelto con OmniVoIP v2.0, pero si persiste:

```bash
# Dentro del CT
cd /opt/omnivoip/docker-compose/prod-env
./validate-config.sh
./fix-userns-mode.sh
docker compose down
docker compose up -d
```

### Puertos RTP no funcionan

En Proxmox LXC, asegúrate de que el firewall del host permite los puertos:

```bash
# En Proxmox host
iptables -I FORWARD -o vmbr0 -p udp --dport 10000:10100 -j ACCEPT
iptables -I FORWARD -i vmbr0 -p udp --sport 10000:10100 -j ACCEPT

# Hacer persistente
apt install iptables-persistent
netfilter-persistent save
```

---

## 📊 Comparación: VM vs CT para OmniVoIP

| Aspecto | Proxmox VM (KVM) | Proxmox CT (LXC) |
|---------|------------------|------------------|
| **Instalación OmniVoIP** | ✅ Directa | ⚠️ Requiere config |
| **Performance** | Buena | ✅ Excelente |
| **Overhead** | ~500MB RAM | ✅ ~50MB RAM |
| **Docker** | ✅ Sin problemas | ⚠️ Nesting requerido |
| **Complejidad** | Baja | Media |
| **Seguridad** | Alta (aislamiento) | Media (compartido) |
| **Recomendado para** | Producción crítica | Desarrollo/Testing |

---

## 🎯 Configuración Recomendada para Producción

### Template Optimizado

```bash
# En Proxmox host, crear CT optimizado
pct create 100 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname omnivoip-prod \
  --memory 16384 \
  --swap 4096 \
  --cores 8 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.1.100/24,gw=192.168.1.1 \
  --nameserver 8.8.8.8 \
  --nameserver 8.8.4.4 \
  --storage local-lvm \
  --rootfs local-lvm:100 \
  --features nesting=1,keyctl=1,fuse=1 \
  --unprivileged 0 \
  --onboot 1 \
  --startup order=1,up=30 \
  --description "OmniVoIP Production - v2.0"
```

### Recursos Mínimos

**Para Testing:**
- CPU: 2 cores
- RAM: 4GB
- Disco: 40GB
- Features: nesting=1

**Para Producción:**
- CPU: 4-8 cores
- RAM: 8-16GB
- Disco: 100GB SSD
- Features: nesting=1,keyctl=1,fuse=1

---

## 🔒 Seguridad en Proxmox LXC

### CT Privilegiado (menos seguro, más simple)

```ini
unprivileged: 0
features: nesting=1,keyctl=1,fuse=1
```

**Pros:**
- ✅ Docker funciona sin problemas
- ✅ No requiere mapeo de UIDs
- ✅ Configuración simple

**Contras:**
- ❌ Menor aislamiento de seguridad
- ❌ Root en CT = Root en host (riesgo)

### CT No Privilegiado (más seguro, más complejo)

```ini
unprivileged: 1
features: nesting=1,keyctl=1,fuse=1
lxc.idmap: u 0 100000 65536
lxc.idmap: g 0 100000 65536
```

**Pros:**
- ✅ Mayor seguridad
- ✅ Aislamiento de usuarios
- ✅ Root en CT ≠ Root en host

**Contras:**
- ❌ Configuración más compleja
- ⚠️ Posibles problemas con permisos

**Recomendación:** CT privilegiado para producción en Proxmox dedicado.

---

## 📝 Script de Deployment Automatizado para Proxmox

```bash
#!/bin/bash
# deployment-proxmox-lxc.sh

# Variables
CT_ID=100
CT_HOSTNAME="omnivoip"
CT_MEMORY=8192
CT_CORES=4
CT_DISK=50

# Crear CT
pct create $CT_ID local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname $CT_HOSTNAME \
  --memory $CT_MEMORY \
  --cores $CT_CORES \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --rootfs local-lvm:$CT_DISK \
  --features nesting=1,keyctl=1,fuse=1 \
  --unprivileged 0 \
  --onboot 1

# Iniciar CT
pct start $CT_ID

# Esperar inicio
sleep 10

# Instalar Docker y OmniVoIP
pct exec $CT_ID -- bash -c "
  apt update
  apt install -y curl git
  curl -fsSL https://get.docker.com | sh
  curl -sSL https://raw.githubusercontent.com/henry0295/omnivoip/main/docker-compose/prod-env/deploy.sh | bash
"

echo "Deployment completado!"
echo "Accede al CT: pct enter $CT_ID"
```

---

## ✅ Checklist Pre-Deployment en Proxmox

- [ ] Proxmox versión 7.0+ o 8.0+
- [ ] CT con nesting=1 habilitado
- [ ] Recursos suficientes (4GB+ RAM, 4+ cores)
- [ ] Features: nesting, keyctl, fuse activados
- [ ] Módulos kernel: overlay, br_netfilter cargados
- [ ] Firewall Proxmox configurado para puertos VoIP
- [ ] AppArmor configurado (si CT no privilegiado)
- [ ] Red bridge vmbr0 funcional
- [ ] Acceso a internet desde el CT

---

## 🎉 Conclusión

**OmniVoIP v2.0 es COMPATIBLE con Proxmox LXC Containers** con la configuración correcta:

✅ **Funciona perfectamente** con CT privilegiado + nesting  
✅ **Sin errores de sysctl** gracias a la arquitectura v2.0  
✅ **Performance excelente** aprovechando LXC  
✅ **Menos overhead** que VM tradicional  

**Recomendación final:** Usar CT privilegiado con nesting para producción en Proxmox.

---

**Última actualización:** 17 de enero de 2026  
**Autor:** VOZIP COLOMBIA  
**Versión OmniVoIP:** 2.0

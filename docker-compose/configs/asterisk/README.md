# Asterisk PBX Configuration for OmniVoIP

## 📋 Configuraciones Creadas

### 1. **pjsip.conf** - Endpoints y Transports SIP
- **Transports**: UDP (5060), TCP (5060), WS (8088), WSS (8089)
- **Templates**: endpoint-internal, endpoint-webrtc, auth-userpass, aor-single
- **Agents WebRTC**: agent1000, agent1001, agent1002 (ejemplo)
- **Trunk**: Configuración para proveedor SIP externo
- **Kamailio**: Integración con proxy SIP

### 2. **extensions.conf** - Dialplan
- **from-agents**: Contexto para agentes
  - `*10` - Login a cola
  - `*11` - Logout de cola
  - `*20` - Pausa de agente
  - `*21` - Despausa de agente
  - `_X.` - Llamadas salientes
  - `_1XXX` - Extensión a extensión
  - `2000` - Cola de ventas
  - `2001` - Cola de soporte
  - `*98` - Buzón de voz
  - `*43` - Echo test
  
- **ivr-main**: Menú IVR principal
  - Opción 1: Ventas
  - Opción 2: Soporte
  - Opción 3: Directorio
  - Opción 0: Operador
  
- **outbound-campaign**: Contexto para marcador predictivo
- **from-trunk**: Llamadas entrantes

### 3. **queues.conf** - Colas de Llamadas
- **sales**: Cola de ventas (Round Robin)
- **support**: Cola de soporte (Least Recent)
- **vip**: Cola VIP (Ring All)
- **callbacks**: Cola de callbacks
- **outbound**: Cola para salientes

### 4. **manager.conf** - AMI (Asterisk Manager Interface)
- **Puerto**: 5038
- **Usuarios**:
  - `admin` - Acceso completo (¡cambiar password!)
  - `omnivoip` - Para backend Django
  - `dialer` - Para marcador predictivo
  - `monitoring` - Solo lectura

### 5. **ari.conf** - ARI (Asterisk REST Interface)
- **Usuarios**:
  - `omnivoip` - Para backend
  - `dialer` - Para marcador

### 6. **http.conf** - Servidor HTTP/WebSocket
- **Puerto HTTP**: 8088
- **Puerto HTTPS**: 8089 (opcional)
- **WebSocket**: Habilitado para WebRTC

### 7. **rtp.conf** - RTP/WebRTC
- **Rango de puertos**: 10000-20000
- **STUN**: stun.l.google.com:19302
- **ICE**: Habilitado
- **DTLS**: Habilitado para WebRTC

### 8. **voicemail.conf** - Buzones de Voz
- **Formato**: WAV
- **Email**: Notificaciones configuradas
- **Buzones**:
  - 2000 - Cola ventas
  - 2001 - Cola soporte
  - 1000-1002 - Agentes

### 9. **musiconhold.conf** - Música en Espera
- **default**: Música estándar
- **vip**: Música para clientes VIP

### 10. **asterisk.conf** - Configuración General
- **Directorios**: Paths de sistema
- **Opciones**: Logging, seguridad, performance

### 11. **modules.conf** - Módulos
- **PJSIP**: Stack SIP moderno
- **WebRTC**: Soporte completo
- **ARI**: REST API
- **Aplicaciones**: Queue, Dial, Voicemail, MixMonitor, ConfBridge
- **Codecs**: ulaw, alaw, gsm, g722, opus
- **Deshabilitado**: chan_sip (legacy)

### 12. **logger.conf** - Logs
- **Console**: notice, warning, error
- **Full log**: Todos los niveles
- **Queue log**: Métricas de colas

## 🔑 Credenciales (¡CAMBIAR EN PRODUCCIÓN!)

### Agentes SIP
```
agent1000 / SecurePass1000
agent1001 / SecurePass1001
agent1002 / SecurePass1002
```

### AMI (Asterisk Manager Interface)
```
admin / OmniVoIP2024!Admin
omnivoip / OmniVoIPBackend2024!
dialer / OmniVoIPDialer2024!
monitoring / OmniVoIPMonitor2024!
```

### ARI (Asterisk REST Interface)
```
omnivoip / OmniVoIPARI2024!
dialer / OmniVoIPDialerARI2024!
```

## 🚀 Uso con Docker

### Dockerfile Asterisk
```dockerfile
FROM asterisk:20

# Copiar configuraciones
COPY configs/asterisk/*.conf /etc/asterisk/

# Crear directorios
RUN mkdir -p /var/spool/asterisk/monitor \
    /var/lib/asterisk/moh \
    /var/lib/asterisk/sounds \
    /etc/asterisk/keys

# Permisos
RUN chown -R asterisk:asterisk /var/spool/asterisk \
    /var/lib/asterisk \
    /etc/asterisk

EXPOSE 5060/udp 5060/tcp 8088 8089 10000-20000/udp 5038

CMD ["asterisk", "-f", "-vvv"]
```

### Variables de Entorno
```env
EXTERNAL_IP=your-public-ip
```

## 📞 Flujo de Llamadas

### Inbound (Entrante)
1. Llamada llega por trunk → `from-trunk`
2. IVR menu → Opción seleccionada
3. Queue → Agente disponible
4. Llamada conectada + grabación (MixMonitor)

### Outbound (Saliente)
1. Agente marca número → `from-agents`
2. Sale por trunk → Llamada externa
3. Grabación automática

### Interno
1. Agente marca 1XXX → Extensión directa
2. Ring → Voicemail si no contesta

### Predictivo (Dialer)
1. Sistema marca número → `outbound-campaign`
2. Cliente contesta → AGI conecta agente
3. Grabación + estadísticas

## 🔧 Comandos Útiles

### CLI Asterisk
```bash
docker exec -it asterisk asterisk -rx "COMMAND"

# Ver extensiones registradas
asterisk -rx "pjsip show endpoints"

# Ver colas
asterisk -rx "queue show"

# Ver llamadas activas
asterisk -rx "core show channels"

# Recargar configuración
asterisk -rx "core reload"

# Ver logs
docker logs -f asterisk
```

### Testing
```bash
# Test desde agente
# Registrar softphone con:
# - SIP Server: asterisk-ip:5060
# - Username: agent1000
# - Password: SecurePass1000

# Marcar:
*10  # Login a cola
*43  # Echo test
1001 # Llamar a otro agente
2000 # Entrar a cola de ventas
```

## 📊 Integración con Backend

El backend Django se conecta vía:

### AMI (manager.conf)
```python
import asterisk.manager

ami = asterisk.manager.Manager()
ami.connect('asterisk', 5038)
ami.login('omnivoip', 'OmniVoIPBackend2024!')

# Originar llamada
ami.originate(
    channel='PJSIP/agent1000',
    exten='2000',
    context='from-agents',
    priority='1'
)
```

### ARI (ari.conf)
```python
import requests

response = requests.get(
    'http://asterisk:8088/ari/channels',
    auth=('omnivoip', 'OmniVoIPARI2024!')
)
```

## 🔐 Seguridad

**IMPORTANTE**: Antes de producción:

1. Cambiar TODAS las contraseñas en:
   - manager.conf
   - ari.conf
   - pjsip.conf (agentes)

2. Configurar firewall:
   ```bash
   # Permitir solo desde IPs conocidas
   iptables -A INPUT -p udp --dport 5060 -s KAMAILIO_IP -j ACCEPT
   iptables -A INPUT -p tcp --dport 5038 -s BACKEND_IP -j ACCEPT
   ```

3. Habilitar TLS/SSL:
   - Generar certificados
   - Configurar transport-wss
   - Actualizar http.conf

4. Rate limiting en firewall

## 📝 Próximos Pasos

- [ ] Generar certificados SSL para WebRTC
- [ ] Configurar trunk con proveedor real
- [ ] Agregar más prompts de audio (IVR)
- [ ] Configurar email para voicemail
- [ ] Ajustar timeouts y estrategias de colas
- [ ] Implementar callbacks automáticos
- [ ] Configurar reportes CDR

## 🐛 Troubleshooting

### No registra agentes
- Verificar credenciales en pjsip.conf
- Ver logs: `asterisk -rx "pjsip show endpoints"`

### No enrutan llamadas
- Verificar dialplan: `asterisk -rx "dialplan show"`
- Ver llamadas: `asterisk -rx "core show channels verbose"`

### Sin audio
- Verificar puertos RTP abiertos (10000-20000)
- Revisar NAT configuration
- Verificar codecs compatibles

### Colas no funcionan
- Verificar agentes logueados: `asterisk -rx "queue show sales"`
- Ver estrategia en queues.conf

---

**Configuración Asterisk completada** ✅  
Listo para integración con Kamailio y backend Django.

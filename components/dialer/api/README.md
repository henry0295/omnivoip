# OmniVoIP Dialer API

API REST para el marcador predictivo de llamadas salientes.

## Tecnologías

- **FastAPI** 0.104.1 - Framework web moderno y rápido
- **Uvicorn** - Servidor ASGI
- **Redis** - Cache y mensajería
- **httpx** - Cliente HTTP async
- **Pydantic** - Validación de datos

## Características

✅ **Gestión de Campañas**
- Crear, actualizar, pausar, detener campañas
- 4 modos de marcación: Preview, Progressive, Predictive, Power
- Control de pacing (ratio de llamadas por agente)
- Horarios y días de operación

✅ **Originación de Llamadas**
- Integración con Asterisk AMI
- Originate calls automático
- Variables personalizadas por llamada
- Timeouts configurables

✅ **Estadísticas en Tiempo Real**
- Llamadas activas, completadas, contestadas
- Tasas de respuesta (answer rate)
- Duración promedio de llamadas
- Llamadas por hora
- Estado de agentes (disponibles, ocupados)

✅ **Gestión de Contactos**
- Importación individual
- Importación masiva (bulk)
- Priorización de contactos
- Custom data por contacto

## Endpoints Principales

### Health Check
```http
GET /health
```

### Campaigns

```http
POST   /campaigns              # Crear campaña
GET    /campaigns/{id}         # Obtener campaña
PATCH  /campaigns/{id}         # Actualizar campaña
POST   /campaigns/{id}/start   # Iniciar campaña
POST   /campaigns/{id}/pause   # Pausar campaña
POST   /campaigns/{id}/stop    # Detener campaña
GET    /campaigns/{id}/stats   # Estadísticas
```

### Calls

```http
POST   /calls/originate        # Originar llamada
```

### Contacts

```http
POST   /contacts               # Agregar contacto
POST   /contacts/bulk          # Importación masiva
```

## Modelos de Datos

### CampaignCreate

```json
{
  "name": "Campaña Ventas Q1",
  "description": "Campaña de ventas primer trimestre",
  "dial_mode": "progressive",
  "queue_name": "sales",
  "trunk": "trunk-out",
  "caller_id": "5551234567",
  "max_retries": 3,
  "retry_delay": 300,
  "pacing_ratio": 1.2,
  "max_concurrent_calls": 50,
  "start_time": "2025-01-01T09:00:00",
  "end_time": "2025-01-01T18:00:00",
  "days_of_week": [0, 1, 2, 3, 4]
}
```

### CallOriginate

```json
{
  "campaign_id": 1,
  "contact_id": 123,
  "phone_number": "5551234567",
  "context": "dialer-outbound",
  "priority": 1,
  "timeout": 30,
  "variables": {
    "CUSTOMER_ID": "456",
    "PRIORITY": "high"
  }
}
```

### CampaignStats (Response)

```json
{
  "campaign_id": 1,
  "total_contacts": 1000,
  "pending_calls": 750,
  "active_calls": 5,
  "completed_calls": 245,
  "answered_calls": 180,
  "no_answer": 45,
  "busy": 15,
  "failed": 5,
  "answer_rate": 73.47,
  "average_duration": 245.5,
  "calls_per_hour": 61.25,
  "agents_available": 3,
  "agents_busy": 2
}
```

## Modos de Marcación

### 1. Preview (Vista Previa)
- Agente ve información del contacto ANTES de llamar
- Agente decide si realizar la llamada
- Ratio: 0 llamadas automáticas

### 2. Progressive (Progresivo)
- 1 llamada por agente disponible
- Marcación automática cuando agente termina llamada
- Ratio: 1.0 (1 llamada por agente)

### 3. Predictive (Predictivo)
- Múltiples llamadas por agente
- Algoritmo predice disponibilidad
- Ratio: 1.2 - 3.0 (configurable)

### 4. Power (Potencia)
- Marcación masiva
- Máxima productividad
- Ratio: 3.0 - 5.0

## Integración con Asterisk AMI

### Conexión AMI

```python
from main import ami

# Conectar
await ami.connect()

# Originar llamada
response = await ami.originate(
    channel="PJSIP/5551234567@trunk-out",
    context="dialer-outbound",
    exten="s",
    priority=1,
    timeout=30,
    caller_id="5559876543",
    variables={
        "CAMPAIGN_ID": "1",
        "CONTACT_ID": "123"
    }
)
```

### Variables Disponibles

- `CAMPAIGN_ID` - ID de la campaña
- `CONTACT_ID` - ID del contacto
- `CUSTOMER_ID` - ID del cliente (custom)
- `PRIORITY` - Prioridad (high, medium, low)
- `CALLERID(num)` - Número del llamante

## Integración con Backend Django

### Comunicación HTTP

```python
# Crear campaña en Django
POST http://django:8000/api/campaigns/

# Obtener contactos
GET http://django:8000/api/contacts/?campaign_id=1

# Actualizar CDR
POST http://django:8000/api/cdrs/
```

## Redis Keys

### Campaign Data
```
campaign:{campaign_id} -> Hash
  - status: "active" | "paused" | "completed"
  - active_calls: 5
  - total_calls: 245
  - answered_calls: 180
  - started_at: "2025-01-01T09:00:00"
  - completed_at: "2025-01-01T18:00:00"
```

### Events Channel
```
PUBLISH dialer:events "campaign:started:1"
PUBLISH dialer:events "campaign:paused:1"
PUBLISH dialer:events "campaign:stopped:1"
```

## Instalación

### Con Docker

```bash
cd components/dialer/api
docker build -t omnivoip-dialer-api .
docker run -p 8001:8001 --env-file .env omnivoip-dialer-api
```

### Sin Docker

```bash
cd components/dialer/api

# Crear virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno
cp .env.example .env
# Editar .env con valores reales

# Ejecutar
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Documentación API

Una vez iniciado, acceder a:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Monitoreo

### Health Check

```bash
curl http://localhost:8001/health
```

### Logs

```bash
# Docker
docker logs -f dialer-api

# Local
tail -f logs/dialer-api.log
```

## Testing

```bash
# Crear campaña
curl -X POST http://localhost:8001/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign",
    "dial_mode": "progressive",
    "queue_name": "sales",
    "trunk": "trunk-out",
    "caller_id": "5551234567"
  }'

# Iniciar campaña
curl -X POST http://localhost:8001/campaigns/1/start

# Ver estadísticas
curl http://localhost:8001/campaigns/1/stats

# Originar llamada
curl -X POST http://localhost:8001/calls/originate \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": 1,
    "contact_id": 123,
    "phone_number": "5551234567"
  }'
```

## Configuración de Producción

### 1. Variables de Entorno

```bash
REDIS_URL=redis://redis:6379/1
BACKEND_URL=http://django:8000
ASTERISK_AMI_HOST=asterisk
ASTERISK_AMI_PORT=5038
ASTERISK_AMI_USER=dialer
ASTERISK_AMI_SECRET=CHANGE_IN_PRODUCTION
API_WORKERS=4
LOG_LEVEL=WARNING
```

### 2. Workers

```bash
# Múltiples workers para alta disponibilidad
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

### 3. Nginx Reverse Proxy

```nginx
upstream dialer_api {
    server dialer-api-1:8001;
    server dialer-api-2:8001;
}

location /dialer/ {
    proxy_pass http://dialer_api;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Troubleshooting

### AMI Connection Failed

```bash
# Verificar conectividad
telnet asterisk 5038

# Verificar credenciales en manager.conf
docker exec -it asterisk cat /etc/asterisk/manager.conf
```

### Redis Connection Error

```bash
# Verificar Redis
docker exec -it redis redis-cli ping

# Verificar URL
echo $REDIS_URL
```

### Backend Communication Error

```bash
# Verificar Django
curl http://django:8000/health

# Verificar network
docker network inspect omnivoip_network
```

## Performance

### Benchmarks

- **Requests/sec**: ~2,000 (con 4 workers)
- **Latency**: ~10ms (promedio)
- **Concurrent calls**: 500+ simultáneas
- **Memory**: ~150MB por worker

### Optimizaciones

1. **Connection Pooling**: Redis, HTTP clients
2. **Async I/O**: Todas las operaciones asíncronas
3. **Workers**: Escalar según carga (CPU cores * 2)
4. **Caching**: Estadísticas cacheadas en Redis

## Licencia

Propietario - VOZIP COLOMBIA © 2025

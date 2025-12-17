# OmniVoIP Dialer Worker

Worker de Celery para marcación automática de llamadas salientes.

## Tecnologías

- **Celery** 5.3.4 - Task queue distribuida
- **Redis** - Message broker y backend
- **httpx** - Cliente HTTP async
- **asyncio** - Programación asíncrona

## Funcionalidades

✅ **Marcación Automática**
- Procesamiento continuo de campañas activas
- 4 modos de marcación: Preview, Progressive, Predictive, Power
- Control de pacing basado en agentes disponibles
- Límites de llamadas concurrentes

✅ **Gestión de Reintentos**
- Reintentos automáticos para llamadas no contestadas
- Reintentos programados con delays configurables
- Máximo de intentos por contacto
- Reset automático de contactos para retry

✅ **Actualización de Estadísticas**
- Actualización periódica de métricas
- Sincronización con Redis y backend
- Monitoreo de agentes disponibles/ocupados
- Tracking de llamadas activas

✅ **Manejo de Eventos**
- Eventos de llamadas (answered, completed, failed)
- Eventos de agentes (available, busy)
- Publicación/suscripción Redis
- Triggers automáticos

## Tareas Celery

### Tareas Principales

#### `process_campaign_task(campaign_id)`
Procesa marcación para una campaña específica.

**Frecuencia**: Cada 10 segundos (para campañas activas)

**Proceso**:
1. Verificar si campaña está activa
2. Obtener configuración de campaña
3. Contar agentes disponibles
4. Calcular llamadas a realizar (pacing)
5. Obtener contactos pendientes
6. Originar llamadas via Dialer API
7. Actualizar estados de contactos

**Ejemplo**:
```python
process_campaign_task.delay(campaign_id=1)
```

#### `retry_contacts_task(campaign_id)`
Reintenta contactos que fallaron anteriormente.

**Frecuencia**: Cada 5 minutos

**Proceso**:
1. Buscar contactos con status='no_answer' o 'busy'
2. Verificar que haya pasado el retry_delay
3. Verificar que no se haya excedido max_retries
4. Resetear contactos a status='pending'

**Ejemplo**:
```python
retry_contacts_task.delay(campaign_id=1)
```

#### `update_statistics_task(campaign_id)`
Actualiza estadísticas de campaña.

**Frecuencia**: Cada 1 minuto

**Proceso**:
1. Obtener stats del Dialer API
2. Actualizar en backend Django
3. Sincronizar Redis

**Ejemplo**:
```python
update_statistics_task.delay(campaign_id=1)
```

#### `handle_call_event(event_type, data)`
Maneja eventos de llamadas en tiempo real.

**Event Types**:
- `call_answered` - Llamada contestada
- `call_completed` - Llamada terminada
- `call_failed` - Llamada falló
- `agent_available` - Agente disponible
- `agent_busy` - Agente ocupado

**Ejemplo**:
```python
handle_call_event.delay(
    event_type='call_answered',
    data={
        'campaign_id': 1,
        'contact_id': 123,
        'call_id': 'abc123'
    }
)
```

### Tareas Periódicas

#### `process_active_campaigns()`
Procesa todas las campañas activas.

**Cron**: Cada 10 segundos

**Proceso**:
1. Buscar campañas con status='active' en Redis
2. Ejecutar `process_campaign_task` para cada una

#### `retry_all_campaigns()`
Reintenta contactos para todas las campañas.

**Cron**: Cada 5 minutos

#### `update_all_statistics()`
Actualiza estadísticas de todas las campañas.

**Cron**: Cada 1 minuto

## Lógica de Pacing

### Progressive Mode
```python
calls_to_make = available_agents - active_calls
```
- 1 llamada por agente disponible
- Ratio: 1.0

### Predictive Mode
```python
target_calls = available_agents * pacing_ratio
calls_to_make = target_calls - active_calls
```
- Múltiples llamadas por agente
- Ratio: 1.2 - 3.0 (configurable)

### Power Mode
```python
target_calls = available_agents * pacing_ratio
calls_to_make = min(target_calls - active_calls, max_concurrent - active_calls)
```
- Marcación masiva
- Ratio: 3.0 - 5.0

### Preview Mode
```python
# No automatic dialing
return False
```
- Agente debe confirmar antes de llamar
- Ratio: 0

## Flujo de Marcación

```
┌─────────────────────────────────────────────┐
│   process_campaign_task (every 10s)         │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Check if campaign is active                │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Get available agents in queue              │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Calculate calls to make (pacing)           │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Get pending contacts (ordered by priority) │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  FOR EACH contact:                          │
│    1. Update to status='dialing'            │
│    2. Originate call via Dialer API         │
│    3. Update counters in Redis              │
│    4. If failed, increment attempts         │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Return stats (dialed, failed)              │
└─────────────────────────────────────────────┘
```

## Integración con Componentes

### Dialer API
```python
# Originate call
POST http://dialer-api:8001/calls/originate
{
  "campaign_id": 1,
  "contact_id": 123,
  "phone_number": "5551234567"
}

# Get stats
GET http://dialer-api:8001/campaigns/1/stats
```

### Backend Django
```python
# Get campaign config
GET http://django:8000/api/campaigns/1/

# Get pending contacts
GET http://django:8000/api/contacts/?campaign_id=1&status=pending

# Update contact
PATCH http://django:8000/api/contacts/123/
{"status": "answered"}

# Get queue agents
GET http://django:8000/api/queues/sales/agents/
```

### Redis
```python
# Campaign status
HGET campaign:1 status  # "active", "paused", "completed"

# Active calls counter
HGET campaign:1 active_calls  # 5
HINCRBY campaign:1 active_calls 1

# Answered calls counter
HGET campaign:1 answered_calls  # 180
HINCRBY campaign:1 answered_calls 1

# Events
PUBLISH dialer:events "campaign:started:1"
```

## Instalación

### Con Docker

```bash
cd components/dialer/worker
docker build -t omnivoip-dialer-worker .
docker run --env-file .env omnivoip-dialer-worker
```

### Sin Docker

```bash
cd components/dialer/worker

# Crear virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno
cp .env.example .env
# Editar .env

# Ejecutar worker
celery -A tasks worker --loglevel=info --concurrency=4
```

## Ejecución

### Worker Principal

```bash
celery -A tasks worker --loglevel=info --concurrency=4
```

### Con Beat (para tareas periódicas)

```bash
# Terminal 1: Worker
celery -A tasks worker --loglevel=info --concurrency=4

# Terminal 2: Beat scheduler
celery -A tasks beat --loglevel=info
```

### Monitoreo con Flower

```bash
pip install flower
celery -A tasks flower --port=5555
```

Acceder a: http://localhost:5555

## Configuración

### Concurrency

```bash
# 4 workers (recomendado para CPU de 4 cores)
celery -A tasks worker --concurrency=4

# Auto-detect (cores * 2)
celery -A tasks worker --autoscale=10,3
```

### Prefetch Multiplier

```python
# En tasks.py
app.conf.worker_prefetch_multiplier = 1  # Sin prefetch (recomendado)
```

### Max Tasks Per Child

```python
# En tasks.py
app.conf.worker_max_tasks_per_child = 1000  # Restart after 1000 tasks
```

## Monitoreo

### Estado del Worker

```bash
celery -A tasks inspect active
celery -A tasks inspect stats
celery -A tasks inspect registered
```

### Logs

```bash
# Docker
docker logs -f dialer-worker

# Local
tail -f celery.log
```

### Redis

```bash
# Ver tareas pendientes
redis-cli LLEN celery

# Ver campaign keys
redis-cli KEYS "campaign:*"

# Ver campaign data
redis-cli HGETALL campaign:1
```

## Testing

### Ejecutar Tarea Manualmente

```python
from tasks import process_campaign_task

# Síncrono (blocking)
result = process_campaign_task(campaign_id=1)
print(result)

# Asíncrono (background)
task = process_campaign_task.delay(campaign_id=1)
print(task.id)

# Get result
result = task.get(timeout=10)
print(result)
```

### Publicar Evento

```python
from tasks import handle_call_event

handle_call_event.delay(
    event_type='call_answered',
    data={
        'campaign_id': 1,
        'contact_id': 123,
        'call_id': 'abc123',
        'duration': 245
    }
)
```

## Troubleshooting

### Worker no se conecta a Redis

```bash
# Verificar Redis
redis-cli ping

# Verificar URL
echo $REDIS_URL

# Test connection
python -c "import redis; r=redis.from_url('redis://redis:6379/0'); print(r.ping())"
```

### Tareas no se ejecutan

```bash
# Ver tareas registradas
celery -A tasks inspect registered

# Ver workers activos
celery -A tasks inspect active_queues

# Purge all tasks
celery -A tasks purge
```

### Memory leaks

```bash
# Reducir max_tasks_per_child
celery -A tasks worker --max-tasks-per-child=100

# Monitorear memoria
watch -n 1 'ps aux | grep celery'
```

## Performance

### Benchmarks

- **Tasks/sec**: ~100 campaigns/segundo
- **Calls/min**: 500+ (depende de Asterisk capacity)
- **Latency**: <100ms por task
- **Memory**: ~80MB por worker

### Optimizaciones

1. **Prefetch**: Desactivar para distribución uniforme
2. **Concurrency**: CPU cores * 1 (I/O bound tasks)
3. **Max Tasks**: Restart workers periódicamente
4. **Connection Pool**: Reusar conexiones HTTP

## Licencia

Propietario - VOZIP COLOMBIA © 2025

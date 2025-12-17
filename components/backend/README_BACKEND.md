# OmniVoIP Backend

Django backend para OmniVoIP Contact Center Platform.

## Estructura del Proyecto

```
backend/
├── omnivoip/              # Proyecto Django principal
│   ├── settings/          # Configuraciones (base, development, production)
│   ├── urls.py           # URLs principales
│   ├── wsgi.py           # WSGI entry point
│   ├── asgi.py           # ASGI entry point (WebSockets)
│   └── celery.py         # Configuración Celery
├── apps/                  # Aplicaciones Django
│   ├── users/            # Gestión de usuarios y autenticación
│   ├── campaigns/        # Campañas salientes/entrantes
│   ├── contacts/         # CRM y gestión de contactos
│   ├── calls/            # Historial de llamadas (CDR)
│   ├── agents/           # Gestión de agentes y estados
│   ├── queues/           # Colas de llamadas
│   ├── reports/          # Reportes y analytics
│   └── api/              # API central y WebSockets
├── manage.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Instalación Local

### 1. Requisitos Previos

- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### 2. Configuración

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones
```

### 3. Base de Datos

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

### 4. Ejecutar Servidor

```bash
# Servidor de desarrollo
python manage.py runserver

# Celery worker (en otra terminal)
celery -A omnivoip.celery worker --loglevel=info

# Celery beat (tareas programadas)
celery -A omnivoip.celery beat --loglevel=info
```

## APIs Disponibles

### Autenticación
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/register/` - Registro
- `POST /api/auth/token/refresh/` - Refresh token
- `GET /api/auth/users/me/` - Perfil actual

### Usuarios
- `GET /api/auth/users/` - Lista de usuarios
- `POST /api/auth/users/` - Crear usuario
- `GET /api/auth/users/{id}/` - Detalle de usuario
- `PUT /api/auth/users/{id}/` - Actualizar usuario
- `DELETE /api/auth/users/{id}/` - Eliminar usuario

### Organizaciones
- `GET /api/auth/organizations/` - Lista de organizaciones
- `POST /api/auth/organizations/` - Crear organización

## Documentación API

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Schema JSON: http://localhost:8000/api/schema/

## Modelos Principales

### Users App
- `User` - Usuario del sistema (custom user model)
- `Organization` - Organización/Tenant
- `UserProfile` - Perfil extendido del usuario

### Campaigns App
- `Campaign` - Campaña de llamadas
- `CampaignScript` - Scripts para campañas
- `DispositionCode` - Códigos de disposición

### Contacts App
- `Contact` - Contacto/Lead
- `ContactList` - Lista de contactos importados
- `ContactCampaign` - Relación contacto-campaña

### Calls App
- `Call` - Registro de llamada (CDR)

### Agents App
- `AgentStatus` - Estado en tiempo real del agente
- `AgentSession` - Sesión de trabajo del agente

### Queues App
- `Queue` - Cola de llamadas
- `QueueMember` - Asignación agente-cola
- `QueueStatistics` - Estadísticas históricas

### Reports App
- `Report` - Reportes configurados
- `ReportExport` - Exportaciones de reportes

## WebSockets

Endpoints disponibles:
- `ws://localhost:8000/ws/dashboard/` - Dashboard en tiempo real
- `ws://localhost:8000/ws/agent/{id}/` - Actualizaciones de agente
- `ws://localhost:8000/ws/queue/{id}/` - Actualizaciones de cola
- `ws://localhost:8000/ws/campaign/{id}/` - Actualizaciones de campaña

## Tareas Celery

### Programadas
- Limpieza de sesiones expiradas (diario a las 2 AM)
- Actualización de estadísticas de campañas (cada 5 minutos)
- Verificación de timeouts de agentes (cada minuto)
- Generación de reportes diarios (diario a las 00:30)

### On-demand
- Actualización de estadísticas de usuario
- Inicio/parada de campañas
- Exportación de reportes
- Importación de contactos

## Variables de Entorno

Ver `.env.example` para todas las variables disponibles.

## Testing

```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=apps
```

## Producción

Para despliegue en producción:

1. Configurar `DJANGO_SETTINGS_MODULE=omnivoip.settings.production`
2. Establecer `DEBUG=False`
3. Configurar `SECRET_KEY` segura
4. Configurar `ALLOWED_HOSTS`
5. Usar servidor WSGI (Gunicorn)
6. Configurar servidor ASGI (Daphne) para WebSockets
7. Configurar servidor web (Nginx)
8. Usar PostgreSQL en producción
9. Configurar SSL/TLS

## Licencia

MIT

# OmniVoIP Backend

Django-based backend for OmniVoIP Contact Center.

## Structure

```
backend/
├── omnivoip/              # Main Django project
│   ├── settings/          # Settings (dev, prod)
│   ├── wsgi.py
│   ├── asgi.py
│   └── urls.py
├── apps/                  # Django apps
│   ├── users/             # User management
│   ├── campaigns/         # Campaign management
│   ├── contacts/          # Contact/CRM
│   ├── calls/             # Call handling
│   ├── agents/            # Agent management
│   ├── queues/            # Queue management
│   ├── reports/           # Reporting
│   └── api/               # REST API
├── manage.py
├── requirements.txt
├── Dockerfile
└── docker-entrypoint.sh
```

## Features

- **REST API**: Full REST API with DRF
- **WebSockets**: Real-time updates via Channels
- **Authentication**: JWT + Session auth
- **Database**: PostgreSQL with migrations
- **Cache**: Redis for session and cache
- **Tasks**: Celery for async tasks
- **Storage**: S3/MinIO for media files

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run tests
pytest
```

## API Endpoints

- `/api/auth/` - Authentication
- `/api/users/` - User management
- `/api/campaigns/` - Campaigns
- `/api/contacts/` - Contacts
- `/api/calls/` - Call history
- `/api/agents/` - Agent status
- `/api/queues/` - Queue statistics
- `/api/reports/` - Reports

## Environment Variables

See `.env` file in docker-compose directory.

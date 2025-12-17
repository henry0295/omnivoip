"""
Celery configuration for OmniVoIP project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omnivoip.settings.development')

app = Celery('omnivoip')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule
app.conf.beat_schedule = {
    'cleanup-expired-sessions': {
        'task': 'apps.users.tasks.cleanup_expired_sessions',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
    'update-campaign-statistics': {
        'task': 'apps.campaigns.tasks.update_campaign_statistics',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'check-agent-timeouts': {
        'task': 'apps.agents.tasks.check_agent_timeouts',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
    'generate-daily-reports': {
        'task': 'apps.reports.tasks.generate_daily_reports',
        'schedule': crontab(hour=0, minute=30),  # Daily at 00:30
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

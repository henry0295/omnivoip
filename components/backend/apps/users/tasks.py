"""
Celery tasks for users app
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.contrib.sessions.models import Session


@shared_task
def cleanup_expired_sessions():
    """Clean up expired sessions"""
    Session.objects.filter(expire_date__lt=timezone.now()).delete()
    return f"Cleaned up expired sessions"


@shared_task
def update_user_statistics(user_id):
    """Update user statistics"""
    from .models import User
    from apps.calls.models import Call
    
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile
        
        # Calculate statistics from calls
        calls = Call.objects.filter(agent=user)
        profile.total_calls = calls.count()
        profile.successful_calls = calls.filter(status='COMPLETED').count()
        
        # Calculate average call duration
        completed_calls = calls.filter(status='COMPLETED', duration__isnull=False)
        if completed_calls.exists():
            total_duration = sum([call.duration.total_seconds() for call in completed_calls])
            avg_duration = total_duration / completed_calls.count()
            profile.average_call_duration = timedelta(seconds=avg_duration)
        
        profile.save()
        return f"Updated statistics for user {user.email}"
    
    except User.DoesNotExist:
        return f"User {user_id} not found"

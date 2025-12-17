"""Celery tasks for agents"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def check_agent_timeouts():
    """Check for agent timeouts and auto-logout"""
    from .models import AgentStatus
    
    timeout_threshold = timezone.now() - timedelta(hours=12)
    
    # Find agents that haven't updated in X hours
    stale_agents = AgentStatus.objects.filter(
        state__in=['AVAILABLE', 'BUSY', 'ON_CALL'],
        updated_at__lt=timeout_threshold
    )
    
    for agent_status in stale_agents:
        agent_status.state = AgentStatus.State.OFFLINE
        agent_status.logout_time = timezone.now()
        agent_status.save()
    
    return f"Checked {stale_agents.count()} stale agents"


@shared_task
def update_agent_statistics(agent_id):
    """Update agent session statistics"""
    from .models import AgentSession
    from apps.calls.models import Call
    
    try:
        # Get active session
        session = AgentSession.objects.filter(
            agent_id=agent_id,
            logout_time__isnull=True
        ).first()
        
        if not session:
            return f"No active session for agent {agent_id}"
        
        # Calculate statistics
        calls = Call.objects.filter(
            agent_id=agent_id,
            start_time__gte=session.login_time
        )
        
        session.total_calls = calls.count()
        session.inbound_calls = calls.filter(direction='INBOUND').count()
        session.outbound_calls = calls.filter(direction='OUTBOUND').count()
        session.successful_calls = calls.filter(
            disposition__is_successful=True
        ).count()
        
        # Calculate times
        completed_calls = calls.filter(talk_time__isnull=False)
        if completed_calls.exists():
            total_seconds = sum([c.talk_time.total_seconds() for c in completed_calls])
            session.total_talk_time = timedelta(seconds=total_seconds)
        
        session.save()
        
        return f"Updated statistics for agent {agent_id}"
    except Exception as e:
        return f"Error updating agent statistics: {str(e)}"

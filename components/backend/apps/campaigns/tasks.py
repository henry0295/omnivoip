"""Celery tasks for campaigns"""
from celery import shared_task
from django.utils import timezone


@shared_task
def update_campaign_statistics(campaign_id=None):
    """Update campaign statistics"""
    from .models import Campaign
    
    if campaign_id:
        campaigns = Campaign.objects.filter(id=campaign_id)
    else:
        campaigns = Campaign.objects.filter(status=Campaign.Status.ACTIVE)
    
    for campaign in campaigns:
        # Update statistics from calls
        from apps.calls.models import Call
        
        calls = Call.objects.filter(campaign=campaign)
        campaign.total_contacts = campaign.contacts.count()
        campaign.called_contacts = calls.values('contact').distinct().count()
        campaign.successful_calls = calls.filter(
            disposition__is_successful=True
        ).count()
        campaign.save()
    
    return f"Updated {campaigns.count()} campaigns"


@shared_task
def start_campaign(campaign_id):
    """Start a campaign"""
    from .models import Campaign
    
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        campaign.status = Campaign.Status.ACTIVE
        campaign.start_date = timezone.now()
        campaign.save()
        
        # Trigger dialer if enabled
        if campaign.dialer_enabled:
            # TODO: Integration with dialer
            pass
        
        return f"Campaign {campaign.name} started"
    except Campaign.DoesNotExist:
        return f"Campaign {campaign_id} not found"

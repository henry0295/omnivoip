"""
Call models
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Call(models.Model):
    """Call record (CDR)"""
    
    class Direction(models.TextChoices):
        INBOUND = 'INBOUND', _('Inbound')
        OUTBOUND = 'OUTBOUND', _('Outbound')
    
    class Status(models.TextChoices):
        INITIATED = 'INITIATED', _('Initiated')
        RINGING = 'RINGING', _('Ringing')
        ANSWERED = 'ANSWERED', _('Answered')
        COMPLETED = 'COMPLETED', _('Completed')
        BUSY = 'BUSY', _('Busy')
        NO_ANSWER = 'NO_ANSWER', _('No Answer')
        FAILED = 'FAILED', _('Failed')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    # Call identification
    unique_id = models.CharField(max_length=255, unique=True, verbose_name=_('Unique ID'))
    channel = models.CharField(max_length=255, blank=True, verbose_name=_('Channel'))
    direction = models.CharField(max_length=20, choices=Direction.choices, verbose_name=_('Direction'))
    status = models.CharField(max_length=20, choices=Status.choices, verbose_name=_('Status'))
    
    # Numbers
    caller_id = models.CharField(max_length=50, verbose_name=_('Caller ID'))
    destination = models.CharField(max_length=50, verbose_name=_('Destination'))
    
    # Relationships
    organization = models.ForeignKey('users.Organization', on_delete=models.CASCADE, related_name='calls')
    campaign = models.ForeignKey('campaigns.Campaign', on_delete=models.SET_NULL, null=True, blank=True, related_name='calls')
    contact = models.ForeignKey('contacts.Contact', on_delete=models.SET_NULL, null=True, blank=True, related_name='calls')
    agent = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='calls')
    queue = models.ForeignKey('queues.Queue', on_delete=models.SET_NULL, null=True, blank=True, related_name='calls')
    
    # Disposition
    disposition = models.ForeignKey('campaigns.DispositionCode', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, verbose_name=_('Notes'))
    
    # Timings
    start_time = models.DateTimeField(verbose_name=_('Start time'))
    answer_time = models.DateTimeField(null=True, blank=True, verbose_name=_('Answer time'))
    end_time = models.DateTimeField(null=True, blank=True, verbose_name=_('End time'))
    duration = models.DurationField(null=True, blank=True, verbose_name=_('Duration'))
    talk_time = models.DurationField(null=True, blank=True, verbose_name=_('Talk time'))
    wait_time = models.DurationField(null=True, blank=True, verbose_name=_('Wait time'))
    
    # Recording
    recording_url = models.URLField(blank=True, verbose_name=_('Recording URL'))
    recording_file = models.FileField(upload_to='recordings/', blank=True, null=True, verbose_name=_('Recording'))
    
    # Additional data
    hangup_cause = models.CharField(max_length=100, blank=True, verbose_name=_('Hangup cause'))
    data = models.JSONField(default=dict, blank=True, verbose_name=_('Additional data'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Call')
        verbose_name_plural = _('Calls')
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['unique_id']),
            models.Index(fields=['caller_id']),
            models.Index(fields=['start_time']),
            models.Index(fields=['agent', 'start_time']),
        ]
    
    def __str__(self):
        return f"{self.unique_id} - {self.caller_id} -> {self.destination}"

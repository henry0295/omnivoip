"""
Agent models
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class AgentStatus(models.Model):
    """Agent real-time status"""
    
    class State(models.TextChoices):
        OFFLINE = 'OFFLINE', _('Offline')
        AVAILABLE = 'AVAILABLE', _('Available')
        BUSY = 'BUSY', _('Busy')
        ON_CALL = 'ON_CALL', _('On Call')
        WRAP_UP = 'WRAP_UP', _('Wrap Up')
        BREAK = 'BREAK', _('Break')
        LUNCH = 'LUNCH', _('Lunch')
        MEETING = 'MEETING', _('Meeting')
        TRAINING = 'TRAINING', _('Training')
    
    agent = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='agent_status')
    state = models.CharField(max_length=20, choices=State.choices, default=State.OFFLINE, verbose_name=_('State'))
    
    # Current call info
    current_call = models.ForeignKey('calls.Call', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    current_queue = models.ForeignKey('queues.Queue', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Session info
    login_time = models.DateTimeField(null=True, blank=True, verbose_name=_('Login time'))
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name=_('Logout time'))
    state_since = models.DateTimeField(auto_now=True, verbose_name=_('State since'))
    
    # SIP/WebRTC info
    sip_status = models.CharField(max_length=20, default='UNREGISTERED', verbose_name=_('SIP status'))
    sip_user_agent = models.CharField(max_length=255, blank=True, verbose_name=_('SIP user agent'))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('IP address'))
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Agent Status')
        verbose_name_plural = _('Agent Statuses')
    
    def __str__(self):
        return f"{self.agent.email} - {self.get_state_display()}"


class AgentSession(models.Model):
    """Agent work session history"""
    
    agent = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='sessions')
    organization = models.ForeignKey('users.Organization', on_delete=models.CASCADE, related_name='agent_sessions')
    
    login_time = models.DateTimeField(verbose_name=_('Login time'))
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name=_('Logout time'))
    duration = models.DurationField(null=True, blank=True, verbose_name=_('Duration'))
    
    # Statistics
    total_calls = models.IntegerField(default=0, verbose_name=_('Total calls'))
    inbound_calls = models.IntegerField(default=0, verbose_name=_('Inbound calls'))
    outbound_calls = models.IntegerField(default=0, verbose_name=_('Outbound calls'))
    successful_calls = models.IntegerField(default=0, verbose_name=_('Successful calls'))
    
    total_talk_time = models.DurationField(null=True, blank=True, verbose_name=_('Total talk time'))
    total_wrap_time = models.DurationField(null=True, blank=True, verbose_name=_('Total wrap time'))
    total_idle_time = models.DurationField(null=True, blank=True, verbose_name=_('Total idle time'))
    
    class Meta:
        verbose_name = _('Agent Session')
        verbose_name_plural = _('Agent Sessions')
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.agent.email} - {self.login_time}"

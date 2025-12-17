"""
Queue models
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Queue(models.Model):
    """Call queue model"""
    
    class Strategy(models.TextChoices):
        RING_ALL = 'RINGALL', _('Ring All')
        LEAST_RECENT = 'LEASTRECENT', _('Least Recent')
        FEWEST_CALLS = 'FEWESTCALLS', _('Fewest Calls')
        RANDOM = 'RANDOM', _('Random')
        ROUND_ROBIN = 'RRMEMORY', _('Round Robin')
    
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    extension = models.CharField(max_length=20, unique=True, verbose_name=_('Extension'))
    organization = models.ForeignKey('users.Organization', on_delete=models.CASCADE, related_name='queues')
    
    # Queue settings
    strategy = models.CharField(max_length=20, choices=Strategy.choices, default=Strategy.ROUND_ROBIN, verbose_name=_('Strategy'))
    max_wait_time = models.IntegerField(default=300, help_text='Seconds', verbose_name=_('Max wait time'))
    max_callers = models.IntegerField(default=0, help_text='0 = unlimited', verbose_name=_('Max callers'))
    
    # Music on hold
    moh_class = models.CharField(max_length=100, default='default', verbose_name=_('Music on hold'))
    
    # Announcements
    announcement_file = models.FileField(upload_to='announcements/', blank=True, null=True, verbose_name=_('Announcement'))
    periodic_announce_frequency = models.IntegerField(default=0, help_text='Seconds, 0 = disabled', verbose_name=_('Periodic announce frequency'))
    
    # Agent assignment
    members = models.ManyToManyField('users.User', through='QueueMember', related_name='queues')
    
    # Settings
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    record_calls = models.BooleanField(default=True, verbose_name=_('Record calls'))
    
    # Statistics
    total_calls = models.IntegerField(default=0, verbose_name=_('Total calls'))
    answered_calls = models.IntegerField(default=0, verbose_name=_('Answered calls'))
    abandoned_calls = models.IntegerField(default=0, verbose_name=_('Abandoned calls'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Queue')
        verbose_name_plural = _('Queues')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.extension})"


class QueueMember(models.Model):
    """Queue member (agent assignment)"""
    
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE)
    agent = models.ForeignKey('users.User', on_delete=models.CASCADE)
    
    penalty = models.IntegerField(default=0, verbose_name=_('Penalty'))
    paused = models.BooleanField(default=False, verbose_name=_('Paused'))
    
    # Statistics
    calls_taken = models.IntegerField(default=0, verbose_name=_('Calls taken'))
    last_call = models.DateTimeField(null=True, blank=True, verbose_name=_('Last call'))
    
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Queue Member')
        verbose_name_plural = _('Queue Members')
        unique_together = ['queue', 'agent']
    
    def __str__(self):
        return f"{self.queue.name} - {self.agent.email}"


class QueueStatistics(models.Model):
    """Historical queue statistics"""
    
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name='statistics')
    date = models.DateField(verbose_name=_('Date'))
    
    # Call counts
    total_calls = models.IntegerField(default=0)
    answered_calls = models.IntegerField(default=0)
    abandoned_calls = models.IntegerField(default=0)
    
    # Times
    avg_wait_time = models.DurationField(null=True, blank=True)
    avg_talk_time = models.DurationField(null=True, blank=True)
    max_wait_time = models.DurationField(null=True, blank=True)
    
    # Service level (calls answered within threshold)
    service_level_threshold = models.IntegerField(default=20, help_text='Seconds')
    calls_within_sl = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = _('Queue Statistics')
        verbose_name_plural = _('Queue Statistics')
        unique_together = ['queue', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.queue.name} - {self.date}"

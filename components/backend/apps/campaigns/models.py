"""
Campaign models
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Campaign(models.Model):
    """Campaign model for outbound/inbound campaigns"""
    
    class CampaignType(models.TextChoices):
        OUTBOUND = 'OUTBOUND', _('Outbound')
        INBOUND = 'INBOUND', _('Inbound')
        BLENDED = 'BLENDED', _('Blended')
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        ACTIVE = 'ACTIVE', _('Active')
        PAUSED = 'PAUSED', _('Paused')
        COMPLETED = 'COMPLETED', _('Completed')
        ARCHIVED = 'ARCHIVED', _('Archived')
    
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    campaign_type = models.CharField(max_length=20, choices=CampaignType.choices, verbose_name=_('Type'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name=_('Status'))
    
    organization = models.ForeignKey('users.Organization', on_delete=models.CASCADE, related_name='campaigns')
    queue = models.ForeignKey('queues.Queue', on_delete=models.SET_NULL, null=True, blank=True, related_name='campaigns')
    
    # Campaign settings
    start_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Start date'))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_('End date'))
    max_calls_per_contact = models.IntegerField(default=3, verbose_name=_('Max calls per contact'))
    retry_delay = models.IntegerField(default=3600, help_text='Seconds', verbose_name=_('Retry delay'))
    
    # Dialer settings
    dialer_enabled = models.BooleanField(default=False, verbose_name=_('Dialer enabled'))
    dialer_ratio = models.DecimalField(max_digits=3, decimal_places=2, default=1.0, verbose_name=_('Dialer ratio'))
    
    # Statistics
    total_contacts = models.IntegerField(default=0, verbose_name=_('Total contacts'))
    called_contacts = models.IntegerField(default=0, verbose_name=_('Called contacts'))
    successful_calls = models.IntegerField(default=0, verbose_name=_('Successful calls'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_campaigns')
    
    class Meta:
        verbose_name = _('Campaign')
        verbose_name_plural = _('Campaigns')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_campaign_type_display()})"


class CampaignScript(models.Model):
    """Call scripts for campaigns"""
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='scripts')
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    content = models.TextField(verbose_name=_('Content'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    order = models.IntegerField(default=0, verbose_name=_('Order'))
    
    class Meta:
        verbose_name = _('Campaign Script')
        verbose_name_plural = _('Campaign Scripts')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.campaign.name} - {self.name}"


class DispositionCode(models.Model):
    """Disposition codes for call outcomes"""
    
    code = models.CharField(max_length=50, unique=True, verbose_name=_('Code'))
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    is_successful = models.BooleanField(default=False, verbose_name=_('Is successful'))
    requires_callback = models.BooleanField(default=False, verbose_name=_('Requires callback'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Disposition Code')
        verbose_name_plural = _('Disposition Codes')
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

"""
Reports models
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Report(models.Model):
    """Saved reports"""
    
    class ReportType(models.TextChoices):
        AGENT_PERFORMANCE = 'AGENT_PERFORMANCE', _('Agent Performance')
        CAMPAIGN_SUMMARY = 'CAMPAIGN_SUMMARY', _('Campaign Summary')
        CALL_VOLUME = 'CALL_VOLUME', _('Call Volume')
        QUEUE_STATISTICS = 'QUEUE_STATISTICS', _('Queue Statistics')
        CUSTOM = 'CUSTOM', _('Custom')
    
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    report_type = models.CharField(max_length=50, choices=ReportType.choices, verbose_name=_('Type'))
    
    organization = models.ForeignKey('users.Organization', on_delete=models.CASCADE, related_name='reports')
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_reports')
    
    # Report parameters
    parameters = models.JSONField(default=dict, verbose_name=_('Parameters'))
    
    # Schedule
    is_scheduled = models.BooleanField(default=False, verbose_name=_('Scheduled'))
    schedule_frequency = models.CharField(max_length=20, blank=True, verbose_name=_('Frequency'))
    last_generated = models.DateTimeField(null=True, blank=True, verbose_name=_('Last generated'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ReportExport(models.Model):
    """Report export history"""
    
    class Format(models.TextChoices):
        PDF = 'PDF', _('PDF')
        CSV = 'CSV', _('CSV')
        EXCEL = 'EXCEL', _('Excel')
        JSON = 'JSON', _('JSON')
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='exports')
    format = models.CharField(max_length=10, choices=Format.choices, verbose_name=_('Format'))
    file = models.FileField(upload_to='reports/', verbose_name=_('File'))
    
    generated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Report Export')
        verbose_name_plural = _('Report Exports')
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.report.name} - {self.format} - {self.generated_at}"

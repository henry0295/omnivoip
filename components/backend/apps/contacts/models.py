"""
Contact models
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Contact(models.Model):
    """Contact/Lead model"""
    
    class Status(models.TextChoices):
        NEW = 'NEW', _('New')
        CONTACTED = 'CONTACTED', _('Contacted')
        QUALIFIED = 'QUALIFIED', _('Qualified')
        CONVERTED = 'CONVERTED', _('Converted')
        LOST = 'LOST', _('Lost')
    
    organization = models.ForeignKey('users.Organization', on_delete=models.CASCADE, related_name='contacts')
    
    # Personal information
    first_name = models.CharField(max_length=100, verbose_name=_('First name'))
    last_name = models.CharField(max_length=100, verbose_name=_('Last name'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    phone = models.CharField(max_length=20, verbose_name=_('Phone'))
    phone_2 = models.CharField(max_length=20, blank=True, verbose_name=_('Phone 2'))
    phone_3 = models.CharField(max_length=20, blank=True, verbose_name=_('Phone 3'))
    
    # Additional info
    company = models.CharField(max_length=255, blank=True, verbose_name=_('Company'))
    job_title = models.CharField(max_length=100, blank=True, verbose_name=_('Job title'))
    address = models.TextField(blank=True, verbose_name=_('Address'))
    city = models.CharField(max_length=100, blank=True, verbose_name=_('City'))
    state = models.CharField(max_length=100, blank=True, verbose_name=_('State'))
    country = models.CharField(max_length=100, blank=True, verbose_name=_('Country'))
    postal_code = models.CharField(max_length=20, blank=True, verbose_name=_('Postal code'))
    
    # CRM fields
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, verbose_name=_('Status'))
    source = models.CharField(max_length=100, blank=True, verbose_name=_('Source'))
    notes = models.TextField(blank=True, verbose_name=_('Notes'))
    tags = models.JSONField(default=list, blank=True, verbose_name=_('Tags'))
    custom_fields = models.JSONField(default=dict, blank=True, verbose_name=_('Custom fields'))
    
    # Campaign association
    campaigns = models.ManyToManyField('campaigns.Campaign', through='ContactCampaign', related_name='contacts')
    
    # Metadata
    do_not_call = models.BooleanField(default=False, verbose_name=_('Do not call'))
    last_contacted = models.DateTimeField(null=True, blank=True, verbose_name=_('Last contacted'))
    assigned_to = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_contacts')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
            models.Index(fields=['organization', 'status']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone}"


class ContactCampaign(models.Model):
    """M2M through model for Contact-Campaign"""
    
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    campaign = models.ForeignKey('campaigns.Campaign', on_delete=models.CASCADE)
    
    attempts = models.IntegerField(default=0, verbose_name=_('Attempts'))
    last_attempt = models.DateTimeField(null=True, blank=True, verbose_name=_('Last attempt'))
    next_attempt = models.DateTimeField(null=True, blank=True, verbose_name=_('Next attempt'))
    disposition = models.ForeignKey('campaigns.DispositionCode', on_delete=models.SET_NULL, null=True, blank=True)
    
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Contact Campaign')
        verbose_name_plural = _('Contact Campaigns')
        unique_together = ['contact', 'campaign']
    
    def __str__(self):
        return f"{self.contact} - {self.campaign}"


class ContactList(models.Model):
    """Contact list for bulk imports"""
    
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    organization = models.ForeignKey('users.Organization', on_delete=models.CASCADE, related_name='contact_lists')
    
    file = models.FileField(upload_to='contact_lists/', verbose_name=_('File'))
    total_records = models.IntegerField(default=0, verbose_name=_('Total records'))
    imported_records = models.IntegerField(default=0, verbose_name=_('Imported records'))
    failed_records = models.IntegerField(default=0, verbose_name=_('Failed records'))
    
    is_processed = models.BooleanField(default=False, verbose_name=_('Processed'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = _('Contact List')
        verbose_name_plural = _('Contact Lists')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

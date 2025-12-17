"""
User models for OmniVoIP
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model"""
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        SUPERVISOR = 'SUPERVISOR', _('Supervisor')
        AGENT = 'AGENT', _('Agent')
        MANAGER = 'MANAGER', _('Manager')
    
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.AGENT,
        verbose_name=_('Role')
    )
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Phone'))
    extension = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('Extension'))
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name=_('Avatar'))
    
    # Tenant/Organization support
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True,
        verbose_name=_('Organization')
    )
    
    # Additional fields
    timezone = models.CharField(max_length=50, default='America/Argentina/Cordoba', verbose_name=_('Timezone'))
    language = models.CharField(max_length=10, default='es', verbose_name=_('Language'))
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name=_('Last activity'))
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def full_name(self):
        return self.get_full_name()


class Organization(models.Model):
    """Multi-tenant organization model"""
    
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    slug = models.SlugField(unique=True, verbose_name=_('Slug'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    # Contact information
    email = models.EmailField(verbose_name=_('Email'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Phone'))
    address = models.TextField(blank=True, verbose_name=_('Address'))
    
    # Settings
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    max_agents = models.IntegerField(default=10, verbose_name=_('Max agents'))
    max_campaigns = models.IntegerField(default=5, verbose_name=_('Max campaigns'))
    
    # Logo and branding
    logo = models.ImageField(upload_to='organizations/', blank=True, null=True, verbose_name=_('Logo'))
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    
    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Extended user profile"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Preferences
    theme = models.CharField(max_length=20, default='light', verbose_name=_('Theme'))
    notifications_enabled = models.BooleanField(default=True, verbose_name=_('Notifications enabled'))
    email_notifications = models.BooleanField(default=True, verbose_name=_('Email notifications'))
    
    # Agent-specific settings
    sip_username = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('SIP Username'))
    sip_password = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('SIP Password'))
    auto_answer = models.BooleanField(default=False, verbose_name=_('Auto answer'))
    
    # Performance metrics
    total_calls = models.IntegerField(default=0, verbose_name=_('Total calls'))
    successful_calls = models.IntegerField(default=0, verbose_name=_('Successful calls'))
    average_call_duration = models.DurationField(null=True, blank=True, verbose_name=_('Avg call duration'))
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        return f"Profile: {self.user.email}"

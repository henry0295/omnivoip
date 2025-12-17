from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Organization, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin"""
    
    list_display = ['email', 'first_name', 'last_name', 'role', 'organization', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'organization', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'extension', 'avatar')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Organization', {'fields': ('organization',)}),
        ('Preferences', {'fields': ('timezone', 'language')}),
        ('Important dates', {'fields': ('last_login', 'last_activity', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role', 'organization'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_activity']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Organization admin"""
    
    list_display = ['name', 'email', 'is_active', 'max_agents', 'max_campaigns', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User Profile admin"""
    
    list_display = ['user', 'theme', 'notifications_enabled', 'total_calls', 'successful_calls']
    list_filter = ['theme', 'notifications_enabled', 'auto_answer']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

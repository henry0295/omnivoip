from django.contrib import admin
from .models import Campaign, CampaignScript, DispositionCode


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign_type', 'status', 'organization', 'total_contacts', 'called_contacts', 'created_at']
    list_filter = ['campaign_type', 'status', 'organization', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'total_contacts', 'called_contacts', 'successful_calls']


@admin.register(CampaignScript)
class CampaignScriptAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign', 'is_active', 'order']
    list_filter = ['is_active', 'campaign']
    search_fields = ['name', 'content']


@admin.register(DispositionCode)
class DispositionCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_successful', 'requires_callback', 'is_active']
    list_filter = ['is_successful', 'requires_callback', 'is_active']
    search_fields = ['code', 'name']

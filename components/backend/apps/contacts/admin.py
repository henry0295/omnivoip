from django.contrib import admin
from .models import Contact, ContactList, ContactCampaign


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone', 'email', 'status', 'organization', 'created_at']
    list_filter = ['status', 'organization', 'do_not_call', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone', 'email', 'company']
    readonly_fields = ['created_at', 'updated_at', 'last_contacted']


@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'total_records', 'imported_records', 'failed_records', 'is_processed', 'created_at']
    list_filter = ['is_processed', 'organization', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['total_records', 'imported_records', 'failed_records', 'is_processed', 'created_at']

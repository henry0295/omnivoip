from django.contrib import admin
from .models import Call


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ['unique_id', 'direction', 'status', 'caller_id', 'destination', 'agent', 'start_time', 'duration']
    list_filter = ['direction', 'status', 'organization', 'campaign', 'start_time']
    search_fields = ['unique_id', 'caller_id', 'destination']
    readonly_fields = ['unique_id', 'created_at', 'updated_at', 'duration', 'talk_time', 'wait_time']
    date_hierarchy = 'start_time'

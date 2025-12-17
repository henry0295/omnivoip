from django.contrib import admin
from .models import AgentStatus, AgentSession


@admin.register(AgentStatus)
class AgentStatusAdmin(admin.ModelAdmin):
    list_display = ['agent', 'state', 'sip_status', 'state_since', 'updated_at']
    list_filter = ['state', 'sip_status']
    search_fields = ['agent__email', 'agent__first_name', 'agent__last_name']
    readonly_fields = ['state_since', 'updated_at']


@admin.register(AgentSession)
class AgentSessionAdmin(admin.ModelAdmin):
    list_display = ['agent', 'login_time', 'logout_time', 'duration', 'total_calls', 'successful_calls']
    list_filter = ['organization', 'login_time']
    search_fields = ['agent__email', 'agent__first_name', 'agent__last_name']
    readonly_fields = ['duration']
    date_hierarchy = 'login_time'

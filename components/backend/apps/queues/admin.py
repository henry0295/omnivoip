from django.contrib import admin
from .models import Queue, QueueMember, QueueStatistics


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ['name', 'extension', 'organization', 'strategy', 'is_active', 'total_calls', 'answered_calls']
    list_filter = ['is_active', 'organization', 'strategy']
    search_fields = ['name', 'extension']
    readonly_fields = ['created_at', 'updated_at', 'total_calls', 'answered_calls', 'abandoned_calls']


@admin.register(QueueMember)
class QueueMemberAdmin(admin.ModelAdmin):
    list_display = ['queue', 'agent', 'penalty', 'paused', 'calls_taken', 'last_call']
    list_filter = ['paused', 'queue']
    search_fields = ['queue__name', 'agent__email']
    readonly_fields = ['calls_taken', 'last_call', 'added_at']


@admin.register(QueueStatistics)
class QueueStatisticsAdmin(admin.ModelAdmin):
    list_display = ['queue', 'date', 'total_calls', 'answered_calls', 'abandoned_calls', 'avg_wait_time']
    list_filter = ['queue', 'date']
    readonly_fields = ['date']
    date_hierarchy = 'date'

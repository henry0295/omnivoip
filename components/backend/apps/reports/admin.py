from django.contrib import admin
from .models import Report, ReportExport


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'organization', 'is_scheduled', 'last_generated', 'created_at']
    list_filter = ['report_type', 'is_scheduled', 'organization', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'last_generated']


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = ['report', 'format', 'generated_by', 'generated_at']
    list_filter = ['format', 'generated_at']
    readonly_fields = ['generated_at']
    date_hierarchy = 'generated_at'

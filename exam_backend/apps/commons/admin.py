"""
Commons Admin
"""
from django.contrib import admin

from apps.commons.models import SystemConfig, OperationLog, Notification, FileUpload


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'key', 'value', 'is_active']
    list_filter = ['is_active']
    search_fields = ['key', 'description']


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'type', 'module', 'action', 'ip_address', 'created_at']
    list_filter = ['type', 'module', 'created_at']
    search_fields = ['action', 'detail', 'user__username']
    ordering = ['-created_at']
    readonly_fields = ['user', 'type', 'module', 'action', 'detail', 'ip_address', 'user_agent', 'created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'type', 'title', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['title', 'content', 'user__username']
    ordering = ['-created_at']


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'original_name', 'type', 'size', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['original_name', 'user__username']
    ordering = ['-created_at']

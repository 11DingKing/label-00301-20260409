"""
Grading Admin
"""
from django.contrib import admin

from apps.grading.models import GradingTask


@admin.register(GradingTask)
class GradingTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'exam', 'grader', 'question', 'status', 'progress', 'created_at']
    list_filter = ['status', 'exam']
    search_fields = ['exam__title', 'grader__username']
    ordering = ['-created_at']

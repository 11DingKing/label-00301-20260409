"""
Statistics Admin
"""
from django.contrib import admin

from apps.statistics.models import ExamStatistics, UserStatistics


@admin.register(ExamStatistics)
class ExamStatisticsAdmin(admin.ModelAdmin):
    list_display = ['id', 'exam', 'participant_count', 'average_score', 'pass_rate', 'updated_at']
    search_fields = ['exam__title']
    ordering = ['-updated_at']


@admin.register(UserStatistics)
class UserStatisticsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'exam_count', 'average_score', 'accuracy_rate', 'updated_at']
    search_fields = ['user__username']
    ordering = ['-updated_at']

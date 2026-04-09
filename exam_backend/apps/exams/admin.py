"""
Exams Admin
"""
from django.contrib import admin

from apps.exams.models import Exam
from apps.submissions.models import Submission


class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0
    readonly_fields = ['user', 'status', 'attempt', 'start_time', 'submit_time', 'score']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'type', 'status', 'start_time', 'end_time', 'is_public', 'created_at']
    list_filter = ['type', 'status', 'is_public', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-start_time']
    inlines = [SubmissionInline]
    filter_horizontal = ['allowed_users']
    readonly_fields = ['created_by']

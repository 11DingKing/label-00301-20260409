"""
Submissions Admin
"""
from django.contrib import admin

from apps.submissions.models import Answer, Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'exam', 'user', 'status', 'attempt', 'score', 'start_time', 'submit_time']
    list_filter = ['status', 'exam', 'created_at']
    search_fields = ['user__username', 'exam__title']
    ordering = ['-created_at']
    readonly_fields = ['exam', 'user', 'attempt', 'start_time', 'submit_time']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'submission', 'paper_question', 'status', 'score', 'is_correct', 'graded_at']
    list_filter = ['status', 'is_correct', 'is_marked']
    search_fields = ['submission__user__username', 'answer_content']
    ordering = ['-created_at']
    readonly_fields = ['submission', 'paper_question', 'first_answer_time', 'last_answer_time']

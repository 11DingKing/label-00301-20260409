"""
Questions Admin
"""
from django.contrib import admin

from apps.questions.models import Question, Option, Attachment


class OptionInline(admin.TabularInline):
    model = Option
    extra = 4


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'type', 'difficulty', 'score', 'is_public', 'use_count', 'created_at']
    list_filter = ['type', 'difficulty', 'is_public', 'is_deleted', 'created_at']
    search_fields = ['title', 'content']
    ordering = ['-created_at']
    inlines = [OptionInline, AttachmentInline]
    filter_horizontal = ['tags']

    fieldsets = (
        ('基本信息', {'fields': ('title', 'type', 'difficulty', 'score', 'is_public')}),
        ('题目内容', {'fields': ('content', 'answer', 'answer_analysis')}),
        ('编程题设置', {'fields': ('programming_language', 'time_limit', 'memory_limit', 'test_cases')}),
        ('分类标签', {'fields': ('category', 'tags')}),
        ('统计信息', {'fields': ('use_count', 'correct_count')}),
        ('其他', {'fields': ('created_by', 'is_deleted', 'deleted_at')}),
    )
    readonly_fields = ['use_count', 'correct_count', 'created_by']


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'label', 'content', 'is_correct', 'order']
    list_filter = ['is_correct']
    search_fields = ['content', 'question__title']


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'name', 'type', 'size', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['name', 'description']

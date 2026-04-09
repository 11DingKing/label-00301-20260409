"""
Papers Admin
"""
from django.contrib import admin

from apps.papers.models import Paper, PaperSection, PaperQuestion


class PaperSectionInline(admin.TabularInline):
    model = PaperSection
    extra = 1


class PaperQuestionInline(admin.TabularInline):
    model = PaperQuestion
    extra = 1
    raw_id_fields = ['question']


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'total_score', 'time_limit', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'is_deleted', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    inlines = [PaperSectionInline, PaperQuestionInline]
    readonly_fields = ['created_by']


@admin.register(PaperSection)
class PaperSectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'title', 'question_type', 'order']
    list_filter = ['question_type']
    search_fields = ['title', 'paper__title']


@admin.register(PaperQuestion)
class PaperQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'paper', 'question', 'section', 'score', 'question_number', 'order']
    list_filter = ['paper', 'section']
    raw_id_fields = ['question']

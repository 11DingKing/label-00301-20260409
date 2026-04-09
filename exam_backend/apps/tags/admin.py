"""
Tags Admin
"""
from django.contrib import admin

from apps.tags.models import Tag, Category


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'color', 'is_active', 'created_at']
    list_filter = ['color', 'is_active']
    search_fields = ['name', 'description']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']

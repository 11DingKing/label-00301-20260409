"""
标签 URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.tags.views import TagViewSet, CategoryViewSet

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tag')
router.register('categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]

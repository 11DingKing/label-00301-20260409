"""
阅卷 URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.grading.views import GradingViewSet, GradingTaskViewSet

router = DefaultRouter()
router.register('tasks', GradingTaskViewSet, basename='grading-task')
router.register('', GradingViewSet, basename='grading')

urlpatterns = [
    path('', include(router.urls)),
]

"""
考试 URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.exams.views import ExamViewSet, SubmissionViewSet

router = DefaultRouter()
router.register('submissions', SubmissionViewSet, basename='submission')
router.register('', ExamViewSet, basename='exam')

urlpatterns = [
    path('', include(router.urls)),
]

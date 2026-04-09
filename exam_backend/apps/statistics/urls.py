"""
统计 URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.statistics.views import (
    StatisticsViewSet,
    ExamStatisticsView,
    ExamRankingView,
    ExamQuestionAnalysisView,
)

router = DefaultRouter()
router.register('', StatisticsViewSet, basename='statistics')

urlpatterns = [
    # RESTful 风格的考试统计 API
    # GET /api/statistics/exam/{id}/
    path('exam/<int:exam_id>/', ExamStatisticsView.as_view(), name='exam-statistics'),
    # GET /api/statistics/exam/{id}/ranking/
    path('exam/<int:exam_id>/ranking/', ExamRankingView.as_view(), name='exam-ranking'),
    # GET /api/statistics/exam/{id}/question_analysis/
    path('exam/<int:exam_id>/question_analysis/', ExamQuestionAnalysisView.as_view(), name='exam-question-analysis'),

    # 用户相关统计（保留 ViewSet 风格）
    path('', include(router.urls)),
]
